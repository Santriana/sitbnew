from django.shortcuts import render
from rest_framework import generics, status, serializers
from .serializers import TransactionCreateSerializer, TransactionFhirCreateSerializer, TransactionDetailSerializer, TransactionSitbCreateSerializer
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseRedirect
from apps.users.models import User
from .bundling_fhir import bundle, data_fhir_validation, response_data_ihs
from .bundling_sitb import bundle_sitb
from fhir.resources.bundle import Bundle
from .models import Transaction, TransactionStatus, Log, TransactionSitb
from django.urls import reverse
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction
import json
import ast

# Create your views here.
class TransactionCreateApiView(generics.CreateAPIView):
    serializer_class = TransactionCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = TransactionCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.filter(email=self.request.user.email).first()
            response = bundle(user.id, serializer.data)
            if response['status_process'] == 'success':
                return Response(response, status=status.HTTP_201_CREATED)
            elif response['status_process'] == 'pending':
                return Response(response, status=status.HTTP_200_OK)
            elif response['status_process'] == 'error':
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionFhirCreateApiView(generics.CreateAPIView):
    serializer_class = TransactionFhirCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = TransactionFhirCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.filter(email=self.request.user.email).first()
            try:
                data = serializer.data['data']
                if isinstance(data, dict):
                    Bundle(**data)
                    response = data_fhir_validation(data, user.id)
                    if response['status_process'] == 'success':
                        return Response(response, status=status.HTTP_201_CREATED)
                    elif response['status_process'] == 'pending':
                        return Response(response, status=status.HTTP_200_OK)
                    elif response['status_process'] == 'error':
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"status_process": "failed", "response_data": "format data is not valid", "user_id": None},
                        status=status.HTTP_400_BAD_REQUEST)
            except (Exception, ValueError) as e:
                return Response(
                    {"status_process": "failed", "response_data": "{}".format(e), "user_id": None},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailApiView(generics.RetrieveAPIView):
    serializer_class = TransactionDetailSerializer()

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email=self.request.user)
        pk = kwargs.get('pk', None)

        transaction = Transaction.objects.filter(
            created_by=user,
            pk=pk
        ).first()
        if transaction:
            serializer = TransactionDetailSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Transaction Not Found'}, status=status.HTTP_400_BAD_REQUEST)

class TransactionSitbCreateApiView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = TransactionSitbCreateSerializer(data=request.data)
        user = User.objects.filter(email=self.request.user.email).first()
        middleware_id = request.data.get('middleware_id')
        
        # add patient_nik and id_tb_03 to serializer initial data
        serializer.initial_data['patient_nik'] = request.data.get('patient', {}).get('nik')
        serializer.initial_data['id_tb_03'] = request.data.get('episode_of_care', {}).get('id_tb_03')
        
        # cek middleware_id empty or not
        if middleware_id:
            try:    
                log = Log.objects.get(pk=middleware_id)
            except Log.DoesNotExist:
                response = {"status_process": "error", "response_data": "middleware_id not found", "user_id": user.pk}
                return Response([response], status=status.HTTP_404_NOT_FOUND)
        
            if log.satusehat_status == self.convert_status_string_to_integer('error') or log.satusehat_status == self.convert_status_string_to_integer('failed'):
                return self.handle_serializer(serializer, 'satusehat', user, log.id)
            elif log.sitb_status == self.convert_status_string_to_integer('error') or log.sitb_status == self.convert_status_string_to_integer('failed'):
                return self.handle_serializer(serializer, 'sitb', user, log.id)
                
        # check user is satusehat active or not
        # if is satusehat active, then use parallel handle serializer
        if user.is_satusehat:
            return self.parallel_handle_serializer(serializer, bundle, bundle_sitb, user)
        else:
            return self.handle_serializer(serializer, 'sitb', user)
        
        
    def convert_status_string_to_integer(self, status_string):
        status_mapping = {
            'success': TransactionStatus.SUCCESS,
            'failed': TransactionStatus.FAILED,
            'pending': TransactionStatus.PENDING,
            'error': TransactionStatus.ERROR,
        }

        return status_mapping.get(status_string.lower(), None)
    
    def parallel_handle_serializer(self, serializer, function_satusehat, function_sitb, user):
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # create initial log
        log = Log.objects.create(created_by=user)
        
        with transaction.atomic():
            with ThreadPoolExecutor() as executor:
                satusehat = executor.submit(function_satusehat, user.id, serializer.initial_data, log.id)
                sitb = executor.submit(function_sitb, user.id, serializer.initial_data, log.id)
                
                # tunggu hingga semua proses selesai dan dapatkan hasilnya
                response_satusehat = satusehat.result()
                response_sitb = sitb.result()
                
                return self.handle_parallel_responses(response_satusehat, response_sitb, log.id)
        
    def build_response(self, provider_name, status_process, response_data):
        return {
            'provider_name': provider_name,
            'status_process': status_process,
            'response_data': response_data
        }
        
    def handle_parallel_responses(self, satusehat, sitb, log_id):
        
        # update log
        log = Log.objects.filter(pk=log_id).first()
        log.satusehat_status = self.convert_status_string_to_integer(satusehat['status_process'])
        log.sitb_status = self.convert_status_string_to_integer(sitb['status_process'])
        log.save()
        
        # mapping response
        response = {
            'id': log_id,
            'details': [
                self.build_response('satusehat', satusehat['status_process'], satusehat['response_data']),
                self.build_response('sitb', sitb['status_process'], sitb['response_data'])
            ]
        }

        # jika status_process dari satusehat dan sitb adalah success
        if satusehat['status_process'] == 'success' and sitb['status_process'] == 'success':
            return Response(response, status=status.HTTP_201_CREATED)
        
        # jika status_process dari satusehat dan sitb adalah error
        elif satusehat['status_process'] == 'error' and sitb['status_process'] == 'error':
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # jika status_process dari satusehat dan sitb adalah error, pending, atau success
        elif satusehat['status_process'] in ['error', 'pending', 'success'] or sitb['status_process'] in ['error', 'pending', 'success']:
            return Response(response, status=status.HTTP_200_OK)
            
    
    def handle_serializer(self, serializer, type, user, log_id=None):
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # cek log_id empty or not
        log = Log.objects.get(pk=log_id) if log_id else Log.objects.create(created_by=user)
        
        with transaction.atomic():
            # mapping response
            response = {
                'id': log.id,
                'details': []
            }
            
            if type == 'satusehat':
                satusehat = bundle(user.id, serializer.initial_data, log.id)
                response['details'].append({
                    'provider_name': 'satusehat',
                    'status_process': satusehat['status_process'],
                    'response_data': satusehat['response_data']
                })
                
                # update log
                log.satusehat_status = self.convert_status_string_to_integer(satusehat['status_process'])
                log.save()
            
            elif type == 'sitb':
                sitb = bundle_sitb(user.id, serializer.initial_data, log.id)
                response['details'].append({
                    'provider_name': 'sitb',
                    'status_process': sitb['status_process'],
                    'response_data': sitb['response_data']
                })
                
                # update log
                log.sitb_status = self.convert_status_string_to_integer(sitb['status_process'])
                log.save()
            
            if response['details'][0]['status_process'] == 'success':
                return Response(response, status=status.HTTP_201_CREATED)
            elif response['details'][0]['status_process'] == 'pending':
                return Response(response, status=status.HTTP_200_OK)
            elif response['details'][0]['status_process'] == 'error':
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            return Response(response, status=status.HTTP_200_OK)
        
class TransactionSitbDetailApiView(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        try:
            log = Log.objects.get(pk=pk)
        except Log.DoesNotExist:
            return Response({'detail': 'Transaction Not Found'}, status=status.HTTP_400_BAD_REQUEST)
        
        response = {
            'id': log.id,
            'details': [],
        }
        
        satusehat = Transaction.objects.filter(created_by=log.created_by, log=log.id).order_by('-id').first()
        if satusehat:
            try:
                response_data = response_data_ihs(ast.literal_eval(satusehat.response_data))
            except ValueError:
                response_data = satusehat.response_data
                
            try:
                satusehat_error_messages = ast.literal_eval(satusehat.error_messages)
            except (ValueError, SyntaxError):
                satusehat_error_messages = satusehat.error_messages
                
            response['details'].append({
                'provider_name': 'satusehat',
                'status_process': satusehat.get_status_display().lower(),
                'response_data': response_data,
                'error_messages': satusehat_error_messages
            })
            
            
        sitb = TransactionSitb.objects.filter(created_by=log.created_by, log=log.id).order_by('-id').first()
        if sitb:
            try:
                response_data = ast.literal_eval(sitb.response_data)
            except ValueError:
                response_data = sitb.response_data
                
            try:
                sitb_error_messages = ast.literal_eval(sitb.error_messages)
            except (ValueError, SyntaxError):
                sitb_error_messages = sitb.error_messages
                
            response['details'].append({
                'provider_name': 'sitb',
                'status_process': sitb.get_status_display().lower(),
                'response_data': response_data,
                'error_messages': sitb_error_messages
            })
        
        return Response(response, status=status.HTTP_200_OK)
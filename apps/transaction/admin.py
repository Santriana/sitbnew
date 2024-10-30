from django.contrib import admin
from .models import Transaction, TransactionSitb, Log
from apps.users.models import User
from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from rangefilter.filters import DateRangeFilter
from .forms import TransactionForm
from django.urls import reverse
from django.utils.html import escape, mark_safe

# Register your models here.

class TransactionAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    model = Transaction
    form = TransactionForm
    list_display = [
        'id',
        'organization',
        'location',
        'status', 'last_retry', 'count_retry', 'log_id', 'created_by', 'created_at'
    ]
    search_fields = [
        'location__name', 'location__ihs_id',
        'location__organization__name', 'location__organization__ihs_id', 'log__id'
    ]

    list_filter = [
        ['location__organization', AutocompleteListFilter],
        ['location', AutocompleteListFilter],
        'status',
        ['created_by', AutocompleteListFilter],
        ['created_at', DateRangeFilter]
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False    
    def get_rangefilter_created_at_title(self, request, field_path):
        return 'By created at'

    def organization(self, obj):
        return obj.location.organization.name if obj.location else None
    
    def log_id(self, obj):
        id_log = obj.log.id if obj.log else None
        if id_log:
            link = reverse("admin:transaction_log_change", args=[id_log])
            return mark_safe(f'<a href="{link}">{escape(id_log)}</a>')
        else:
            return None
    
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def get_queryset (self, request):
        if request.user.is_superuser:
            return Transaction.objects
        else :
            return Transaction.objects.filter(created_by_id = request.user.id)

class TransactionAdminSitb(AutocompleteFilterMixin, admin.ModelAdmin):
    model = TransactionSitb
    list_display = [
        'id',
        'rs_name',
        'code_fasyankes',
        'status', 'last_retry', 'count_retry', 'log_id', 'created_by', 'created_at'
    ]
    search_fields = [
        'created_by__name', 'created_by__code_fasyankes', 'log__id',
    ]

    list_filter = ['status', ['created_at', DateRangeFilter]]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_rangefilter_created_at_title(self, request, field_path):
        return 'By created at'

    def rs_name(self, obj):
        return obj.created_by.name if obj.created_by else None

    def code_fasyankes(self, obj):
        return obj.created_by.code_fasyankes if obj.created_by else None

    def created_by(self, obj):
        return obj.created_by.created_by if obj.created_by else None
    
    def log_id(self, obj):
        get_log_id = obj.log.id if obj.log else None
        if get_log_id:
            link = reverse("admin:transaction_log_change", args=[get_log_id])
            return mark_safe(f'<a href="{link}">{escape(get_log_id)}</a>')
        else:
            return None
    
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def get_queryset (self, request):
        if request.user.is_superuser:
            return TransactionSitb.objects
        else :
            return TransactionSitb.objects.filter(created_by_id = request.user.id)

class TransactionLog(admin.ModelAdmin):
    model = Log
    list_display = [
        'id',
        'satusehat_status', 'sitb_status', 'created_by', 'created_at'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def get_queryset (self, request):
        if request.user.is_superuser:
            return Log.objects
        else :
            return Log.objects.filter(created_by_id = request.user.id)

admin.site.register(Log, TransactionLog)
admin.site.register(TransactionSitb, TransactionAdminSitb)
admin.site.register(Transaction, TransactionAdmin)

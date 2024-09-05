from rest_framework import serializers
from .data import data_encounter_status, data_encounter_class, data_icd_x_code, data_condition_clinical_status, \
    data_medication_form, data_medication_extension_medication_on_type, data_episode_of_care_type, \
    data_questionnaire_response_type_diagnosis, data_questionnaire_response_classification_location_anatomy, \
    data_questionnaire_response_classification_treatment_history, \
    data_questionnaire_response_end_result_of_treatment_tb, \
    data_episode_of_care_status, \
    data_type_observation, data_type_observation_bta, data_type_observation_thorax, is_valid, is_valid_date, is_valid_date_end, \
    data_type_observation_bta_valid, data_type_observation_tcm_valid, data_type_observation_tcm_rifam_valid, \
    data_type_observation_culture_treatment_valid, data_type_observation_thorax_valid

from .models import Transaction
from .bundling_fhir import response_data_ihs
import ast
from django.utils.html import escape
from django.conf import settings


class EncounterItemSerializer(serializers.Serializer):
    local_id = serializers.CharField(
        max_length=255, allow_blank=False, allow_null=False, required=True
    )
    classification = serializers.ChoiceField(
        choices=list(data_encounter_class().keys()),
        allow_null=False, allow_blank=False, required=True
    )
    period_start = serializers.DateTimeField(allow_null=False, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=True)
    period_end = serializers.DateTimeField(allow_null=False, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=True)
    period_in_progress = serializers.DateTimeField(allow_null=False, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=True)

    def validate_local_id(self, value):
        return escape(value)

    def validate_classification(self, value):
        return escape(value)

    def validate(self, data):
        period_start = data["period_start"]
        period_in_progress = data["period_in_progress"]
        period_end = data["period_end"]
        local_id = data["local_id"]
        msg_period = "Not Allowed : Future Date"

        if not is_valid(local_id):
            raise serializers.ValidationError({"local_id": "{} {}".format(local_id, settings.INVALID_INPUT)})
        elif is_valid_date(period_start):
            raise serializers.ValidationError({"period_start": "{} {}".format(period_start, msg_period)})

        elif is_valid_date(period_in_progress):
            raise serializers.ValidationError(
                {"period_in_progress": "{} {}".format(period_in_progress, msg_period)})

        elif is_valid_date(period_end):
            raise serializers.ValidationError({"period_end": "{} {}".format(period_end, msg_period)})

        elif is_valid_date_end(period_start, period_in_progress, period_end):
            raise serializers.ValidationError(
                {"period_end": "{} Not Allowed : Past Date older than start or progress".format(period_end)})

        return super().validate(data)


class ConditionOtherItemSerializer(serializers.Serializer):
    icd_x_code = serializers.CharField(
        allow_null=False, allow_blank=False, required=True
    )
    icd_x_code_name = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    clinical_status = serializers.ChoiceField(
        choices=list(data_condition_clinical_status().keys()),
        allow_null=False, allow_blank=False, required=True
    )

    def validate_icd_x_code(self, value):
        return escape(value)

    def validate_icd_x_code_name(self, value):
        return escape(value)

    def validate_clinical_status(self, value):
        return escape(value)


class ConditionItemSerializer(serializers.Serializer):
    icd_x_code_tb = serializers.ChoiceField(
        choices=list(data_icd_x_code().keys()),
        allow_null=False, allow_blank=False, required=True
    )
    clinical_status_tb = serializers.ChoiceField(
        choices=list(data_condition_clinical_status().keys()),
        allow_null=False, allow_blank=False, required=True
    )
    others = ConditionOtherItemSerializer(required=False, many=True, allow_null=True)

    def validate_icd_x_code_tb(self, value):
        return escape(value)

    def validate_clinical_status_tb(self, value):
        return escape(value)


class MedicationItemSerializer(serializers.Serializer):
    kfa_code = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    kfa_name = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    form_code = serializers.ChoiceField(
        choices=list(data_medication_form().keys()),
        allow_null=False, allow_blank=False, required=True
    )

    def validate_kfa_code(self, value):
        if is_valid(value):
            return escape(value)
        raise serializers.ValidationError(settings.INVALID_INPUT)

    def validate_kfa_name(self, value):
        return escape(value)

    def validate_form_code(self, value):
        return escape(value)

    def validate(self, data):
        kfa_code = data['kfa_code']
        if not is_valid(kfa_code):
            raise serializers.ValidationError(
                {"kfa_code": "{} {}".format(kfa_code, settings.INVALID_INPUT)})
        return super().validate(data)


class EpisodeOfCareItemSerializer(serializers.Serializer):
    ihs_id = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    status = serializers.ChoiceField(
        choices=list(data_episode_of_care_status()),
        allow_null=False, allow_blank=False, required=True
    )
    type_code = serializers.ChoiceField(
        choices=list(data_episode_of_care_type().keys()),
        allow_null=False, allow_blank=False, required=True
    )
    period_start = serializers.DateTimeField(allow_null=True, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=False)
    period_end = serializers.DateTimeField(allow_null=True, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=False)

    def validate_ihs_id(self, value):
        return escape(value)

    def validate_status(self, value):
        return escape(value)

    def validate_type_code(self, value):
        return escape(value)

    def validate(self, data):
        try:
            ihs_id = data['ihs_id']
            if not is_valid(ihs_id):
                raise serializers.ValidationError(
                    {"ihs_id": "{} {}".format(ihs_id, settings.INVALID_INPUT)})
        except KeyError:
            pass
        return super().validate(data)


class QuestionnaireResponseItemSerializer(serializers.Serializer):
    type_diagnosis = serializers.ChoiceField(
        choices=list(data_questionnaire_response_type_diagnosis().keys()),
        allow_null=True, allow_blank=True, required=False
    )
    location_anatomy = serializers.ChoiceField(
        choices=list(data_questionnaire_response_classification_location_anatomy().keys()),
        allow_null=True, allow_blank=True, required=False
    )
    treatment_history = serializers.ChoiceField(
        choices=list(data_questionnaire_response_classification_treatment_history().keys()),
        allow_null=True, allow_blank=True, required=False
    )
    end_result_treatment = serializers.ChoiceField(
        choices=list(data_questionnaire_response_end_result_of_treatment_tb().keys()),
        allow_null=True, allow_blank=True, required=False
    )

    def validate_type_diagnosis(self, value):
        return escape(value)

    def validate_location_anatomy(self, value):
        return escape(value)

    def validate_treatment_history(self, value):
        return escape(value)

    def validate_end_result_treatment(self, value):
        return escape(value)


class ObservationItemSerializer(serializers.Serializer):
    local_id = serializers.CharField(
        max_length=255, allow_blank=False, allow_null=False, required=True
    )
    type_observation = serializers.ChoiceField(
        choices=list(data_type_observation()),
        allow_null=False, allow_blank=False, required=True
    )
    issued = serializers.DateTimeField(allow_null=False, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=True)
    issued_rifampicin = serializers.DateTimeField(allow_null=True, input_formats=["%Y-%m-%dT%H:%M:%SZ"], required=False)
    value = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def validate_local_id(self, value):
        return escape(value)

    def validate_value(self, value):
        return escape(value)

    def validate_type_observation(self, attrs):
        return escape(attrs)

    def validate(self, data):
        type_observation = data["type_observation"]
        value = data["value"]
        local_id = data["local_id"]
        msg_invalid = "is not a valid choice."

        if not is_valid(local_id):
            raise serializers.ValidationError({"local_id": "{} {}.".format(local_id, settings.INVALID_INPUT)})
        elif not data_type_observation_bta_valid(type_observation, value):
            raise serializers.ValidationError({"value": "{} {}".format(value, msg_invalid)})
        elif not data_type_observation_tcm_valid(type_observation, value):
            raise serializers.ValidationError({"value": "{} {}".format(value, msg_invalid)})
        elif data_type_observation_tcm_rifam_valid(type_observation, value):
            if "issued_rifampicin" not in data:
                raise serializers.ValidationError({"issued_rifampicin": "This field is required."})
        elif not data_type_observation_culture_treatment_valid(type_observation, value):
            raise serializers.ValidationError({"value": "{} {}".format(value, msg_invalid)})
        elif not data_type_observation_thorax_valid(type_observation, value):
            raise serializers.ValidationError({"value": "{} {}".format(value, msg_invalid)})
        return super().validate(data)


class TransactionCreateSerializer(serializers.Serializer):
    organization_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    location_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)

    practitioner_nik = serializers.DecimalField(max_digits=16, decimal_places=0, allow_null=False, required=True)
    patient_nik = serializers.DecimalField(max_digits=16, decimal_places=0, allow_null=False, required=True)

    encounter = EncounterItemSerializer(required=True)
    questionnaire_response = QuestionnaireResponseItemSerializer(required=False)
    condition = ConditionItemSerializer(required=True, many=True)
    medication = MedicationItemSerializer(required=False, many=True)
    observation = ObservationItemSerializer(required=False, many=True)
    episode_of_care = EpisodeOfCareItemSerializer(required=True)

    def validate_organization_id(self, value):
        return escape(value)

    def validate_location_id(self, value):
        return escape(value)

    def validate_practitioner_nik(self, value):
        return escape(value)

    def validate_patient_nik(self, value):
        return escape(value)

    def validate(self, data):
        organization_id = data['organization_id']
        location_id = data['location_id']

        if not is_valid(organization_id):
            raise serializers.ValidationError({"organization_id": "{}.".format(settings.INVALID_INPUT)})
        elif not is_valid(location_id):
            raise serializers.ValidationError({"location_id": "{}.".format(settings.INVALID_INPUT)})

        return super().validate(data)


class TransactionFhirCreateSerializer(serializers.Serializer):
    data = serializers.JSONField(required=True, allow_null=False)


class TransactionDetailSerializer(serializers.ModelSerializer):
    status_process = serializers.SerializerMethodField()
    error_messages = serializers.SerializerMethodField()
    response_data = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "status_process",
            "response_data",
            "error_messages",
        ]

    def get_status_process(self, instance):
        return instance.get_status_display().lower()

    def get_error_messages(self, instance):
        try:
            return ast.literal_eval(instance.error_messages)
        except (ValueError, SyntaxError):
            return instance.error_messages

    def get_response_data(self, instance):
        try:
            return response_data_ihs(ast.literal_eval(instance.response_data))
        except ValueError:
            return instance.response_data

class PatientItemSerializer(serializers.Serializer):
    nik = serializers.IntegerField(allow_null=False, required=True)
    name = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    gender = serializers.ChoiceField( 
        choices=list(['L', 'P']),
        allow_null=False, allow_blank=False, required=True
    )
    dob = serializers.DateField(allow_null=False, required=True)
    province = serializers.CharField(max_length=255, allow_blank=True, allow_null=False)
    district = serializers.CharField(max_length=255, allow_blank=True, allow_null=False)
    address = serializers.CharField(max_length=255, allow_blank=True, allow_null=False)

    def validate_nik(self, value):
        return escape(value)

    def validate_name(self, value):
        return escape(value)

    def validate_dob(self, value):
        return escape(value)
    
    def validate_address(self, value):
        return escape(value)

class TransactionSitbCreateSerializer(serializers.Serializer):
    middleware_id = serializers.CharField(allow_null=False, allow_blank=True, required=True)
    organization_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)
    location_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, required=True)

    practitioner_nik = serializers.DecimalField(max_digits=16, decimal_places=0, allow_null=False, required=True)
    patient = PatientItemSerializer(required=True)
    encounter = EncounterItemSerializer(required=True)
    questionnaire_response = QuestionnaireResponseItemSerializer(required=False)
    condition = ConditionItemSerializer(required=True, many=True)
    medication = MedicationItemSerializer(required=False, many=True)
    observation = ObservationItemSerializer(required=False, many=True)
    episode_of_care = EpisodeOfCareItemSerializer(required=True)

    def validate_organization_id(self, value):
        return escape(value)

    def validate_location_id(self, value):
        return escape(value)

    def validate_practitioner_nik(self, value):
        return escape(value)

    def validate_patient(self, value):
        return escape(value['nik'])

    def validate(self, data):
        organization_id = data['organization_id']
        location_id = data['location_id']

        if not is_valid(organization_id):
            raise serializers.ValidationError({"organization_id": "{}.".format(settings.INVALID_INPUT)})
        elif not is_valid(location_id):
            raise serializers.ValidationError({"location_id": "{}.".format(settings.INVALID_INPUT)})

        return super().validate(data)
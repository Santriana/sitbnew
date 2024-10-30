from apps.transaction.data import data_icd_x_code, data_questionnaire_response_type_diagnosis, \
    data_questionnaire_response_classification_location_anatomy, \
    data_questionnaire_response_classification_treatment_history, \
    data_questionnaire_response_end_result_of_treatment_tb, data_medication_kfa, \
    data_questionnaire_response_items, data_observation_bta_culture_thorax_value, \
    data_observation_bta_culture_thorax_code, data_diagnostic_report_code, \
    data_diagnostic_report_category, data_observation_tcm_dna, data_observation_tcm_sputum, \
    data_encounter_class, data_condition_clinical_status, data_episode_of_care_type, \
    data_medication_form, data_medication_extension_medication_on_type, \
    data_type_observation_bta, data_type_observation_thorax

from django.utils import timezone
from usaid.settings import AUTH_URL, BASE_URL, USER_AGENT_BROWSER, ENV_API_KEY
from django.core.cache import cache
from .models import Transaction, TransactionStatus, Log
from apps.users.models import User
from apps.organization.models import Organization
from apps.location.models import Location
from collections import defaultdict
import string
import secrets
import uuid
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
from django.utils.html import escape

def generate_random_code_transaction_id():
    string_name = string.ascii_lowercase
    string_digit = string.digits
    return ''.join(secrets.choice(string_name + string_digit) for i in range(3))


def request_data_headers(token):
    headers = {
        "Authorization": "Bearer {}".format(token),
        "User-Agent": "{}".format(USER_AGENT_BROWSER),
        "Content-Type": "application/json"
    }
    return headers


def request_auth(user_id):
    user = User.objects.get(pk=user_id)
    data = {
        "client_id": "{}".format(user.client_id),
        "client_secret": "{}".format(user.client_secret)
    }

    url = "{}/accesstoken".format(AUTH_URL)
    params = {
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "{}".format(USER_AGENT_BROWSER)
    }
    response = requests.request("POST", url=url, params=params, headers=headers, data=data)
    access_token = None
    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json['access_token']
        cache.set('{}_{}'.format(settings.ACCESS_TOKEN_USER, user.id), access_token, int(response_json['expires_in']))
    return access_token


def transaction_request(full_url, request_type):
    data = {
        "fullUrl": "{}{}".format(settings.URN_UUID, full_url),
        "request": {
            "method": "POST",
            "url": "{}".format(request_type)
        }
    }
    return data


def transaction_request_update(episode_of_care_ihs_id, request_type):
    data = {
        "fullUrl": "{}{}".format(settings.URN_UUID, uuid.uuid4()),
        "request": {
            "method": "PUT",
            "url": settings.URL_FORMAT.format(request_type, episode_of_care_ihs_id)
        }
    }
    return data


def condition_diagnosis(data=None, role=False):
    diagnosis_data = []
    if data:
        counter = 1
        for result in data:
            condition_uuid = result["condition_uuid"]
            icd_x_name = result["icd_x_name"]
            diagnosis_code = result["diagnosis_code"]
            diagnosis_name = result["diagnosis_name"]

            diagnosis = {
                "condition": {
                    "reference": "{}{}".format(settings.URN_UUID, condition_uuid),
                    "display": "{}".format(icd_x_name)
                },
                "use" if role is False else "role": {
                    "coding": [
                        {
                            "system": "https://terminology.hl7.org/CodeSystem/diagnosis-role",
                            "code": "{}".format(diagnosis_code),
                            "display": "{}".format(diagnosis_name)
                        }
                    ]
                },
                "rank": counter
            }
            diagnosis_data.append(diagnosis)
            counter += 1

    result = {}
    if diagnosis_data:
        result = {"diagnosis": diagnosis_data}
    return result


def encounter(encounter_uuid, organization_id,
              location_id, location_name,
              patient_id, patient_name,
              practitioner_id, practitioner_name,
              data_input, service_provider,
              diagnosis_data=None, episode_of_care_uuid=None, episode_of_care_ihs_id=None):
    encounter_local_id = data_input["local_id"]
    encounter_status = "finished"
    encounter_period_start = escape(data_input["period_start"])
    encounter_period_end = escape(data_input["period_end"])
    encounter_period_in_progress = escape(data_input["period_in_progress"])
    encounter_class_code = data_input["classification"]

    encounter_class_display = None
    if encounter_class_code and "{}".format(encounter_class_code) in data_encounter_class():
        encounter_class_display = data_encounter_class()[encounter_class_code]

    data_request = transaction_request(encounter_uuid, "Encounter")
    data_default = {
        "resourceType": "Encounter",
        "identifier": [
            {
                "system": "https://sys-ids.kemkes.go.id/encounter/{}".format(organization_id),
                "value": "{}".format(encounter_local_id)
            }
        ],
        "status": "{}".format(encounter_status),
        "class": {
            "system": "https://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "{}".format(encounter_class_code),
            "display": "{}".format(encounter_class_display)
        },
        "subject": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id),
            "display": "{}".format(patient_name)
        },
        "participant": [
            {
                "type": [
                    {
                        "coding": [
                            {
                                "system": "https://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                "code": "ATND",
                                "display": "attender"
                            }
                        ]
                    }
                ],
                "individual": {
                    "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id),
                    "display": "{}".format(practitioner_name)
                }
            }
        ],
        "location": [
            {
                "location": {
                    "reference": "Location/{}".format(location_id),
                    "display": "{}".format(location_name)
                }
            }
        ],
        "serviceProvider": {
            "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, service_provider)
        },
        "episodeOfCare": [
            {
                "reference": "{}{}".format(settings.URN_UUID, episode_of_care_uuid)
                if episode_of_care_ihs_id is None or episode_of_care_ihs_id == ""
                else "EpisodeOfCare/{}".format(episode_of_care_ihs_id)
            }
        ],
        "statusHistory": [
            {
                "status": "arrived",
                "period": {
                    "start": "{}".format(encounter_period_start),
                    "end": "{}".format(encounter_period_in_progress)
                }
            },
            {
                "status": "in-progress",
                "period": {
                    "start": "{}".format(encounter_period_in_progress),
                    "end": "{}".format(encounter_period_end)
                }
            },
            {
                "status": "finished",
                "period": {
                    "start": "{}".format(encounter_period_end),
                    "end": "{}".format(encounter_period_end)
                }
            },
        ],
    }

    data_period = {}
    if encounter_period_start or encounter_period_end:
        start_value, end_value = {}, {}
        if encounter_period_start:
            start_value = {"start": "{}".format(encounter_period_start)}
        if encounter_period_end:
            end_value = {"end": "{}".format(encounter_period_end)}
        data_period = {
            "period": {**start_value, **end_value}
        }

    diagnosis = condition_diagnosis(diagnosis_data)

    data = {"resource": {**data_default, **diagnosis, **data_period}}
    merge_data = {**data, **data_request}
    return merge_data


def condition_item_detail(
        encounter_uuid,
        condition_uuid,
        patient_id, patient_name,
        icd_x_code, icd_x_name,
        condition_clinical_status_code, condition_clinical_status_name):
    data_request = transaction_request(condition_uuid, "Condition")
    data_default = {
        "resource": {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "https://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "{}".format(condition_clinical_status_code),
                        "display": "{}".format(condition_clinical_status_name)
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "https://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "https://hl7.org/fhir/sid/icd-10",
                        "code": "{}".format(icd_x_code),
                        "display": "{}".format(icd_x_name)
                    }
                ]
            },
            "subject": {
                "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id),
                "display": "{}".format(patient_name)
            },
            "encounter": {
                "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
            }
        }
    }
    merge_data = {**data_default, **data_request}
    return merge_data


def condition(encounter_uuid, condition_uuid,
              patient_id, patient_name,
              data_input):
    list_data = []
    if data_input:
        for result in data_input:
            icd_x_code_tb = result["icd_x_code_tb"]
            condition_clinical_status_code_tb = result["clinical_status_tb"]

            icd_x_name_tb = None
            if icd_x_code_tb and "{}".format(icd_x_code_tb) in data_icd_x_code():
                icd_x_name_tb = data_icd_x_code()[icd_x_code_tb]

            condition_clinical_status_name_tb = None
            if condition_clinical_status_code_tb and "{}".format(
                    condition_clinical_status_code_tb) in data_condition_clinical_status():
                condition_clinical_status_name_tb = data_condition_clinical_status()[condition_clinical_status_code_tb]

            print(condition_uuid.get(icd_x_code_tb)[0])
            condition_tb = condition_item_detail(
                encounter_uuid, condition_uuid.get(icd_x_code_tb)[0],
                patient_id, patient_name,
                icd_x_code_tb, icd_x_name_tb,
                condition_clinical_status_code_tb, condition_clinical_status_name_tb
            )
            list_data.append(condition_tb)

            if "others" in result and result["others"] is not None:
                for result_other in result["others"]:
                    icd_x_code = result_other["icd_x_code"]
                    icd_x_code_name = result_other["icd_x_code_name"]
                    condition_clinical_status_code = result_other["clinical_status"]

                    condition_clinical_status_name = None
                    if condition_clinical_status_code and "{}".format(
                            condition_clinical_status_code) in data_condition_clinical_status():
                        condition_clinical_status_name = data_condition_clinical_status()[
                            condition_clinical_status_code_tb]
                    print("other")
                    print(condition_uuid.get(icd_x_code)[0])
                    condition_other = condition_item_detail(
                        encounter_uuid, condition_uuid.get(icd_x_code)[0],
                        patient_id, patient_name,
                        icd_x_code, icd_x_code_name,
                        condition_clinical_status_code, condition_clinical_status_name
                    )
                    list_data.append(condition_other)

    return list_data


def episode_of_care(episode_of_care_uuid,
                    organization_id,
                    patient_id,
                    patient_name,
                    practitioner_id,
                    practitioner_name,
                    data_input,
                    diagnosis_data=None):
    episode_of_care_ihs_id = data_input["ihs_id"]
    episode_of_care_status = data_input["status"]
    episode_of_care_type_code = data_input["type_code"]
    episode_of_care_period_start = data_input["period_start"]
    episode_of_care_period_end = data_input.get("period_end", '')

    episode_of_care_type_name = None
    if episode_of_care_type_code and "{}".format(
            episode_of_care_type_code) in data_episode_of_care_type():
        episode_of_care_type_name = data_episode_of_care_type()[episode_of_care_type_code]

    if not episode_of_care_ihs_id:
        data_request = transaction_request(episode_of_care_uuid, "EpisodeOfCare")
    else:
        data_request = transaction_request_update(episode_of_care_ihs_id, "EpisodeOfCare")

    data_default = {
        "resourceType": "EpisodeOfCare",
        "status": "{}".format(episode_of_care_status),
        "patient": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id),
            "display": "{}".format(patient_name)
        },
        "managingOrganization": {
            "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
        },
        "careManager": {
            "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id),
            "display": "{}".format(practitioner_name)
        },
        "type": [
            {
                "coding": [
                    {
                        "system": "https://terminology.kemkes.go.id/CodeSystem/episodeofcare-type",
                        "code": "{}".format(episode_of_care_type_code),
                        "display": "{}".format(episode_of_care_type_name)
                    }
                ]
            }
        ],
    }

    data_period = {}
    if episode_of_care_period_start or episode_of_care_period_end:
        start_value, end_value = {}, {}
        if episode_of_care_period_start:
            start_value = {"start": "{}".format(escape(episode_of_care_period_start))}
        if episode_of_care_period_end:
            end_value = {"end": "{}".format(escape(episode_of_care_period_end))}
        data_period = {
            "period": {**start_value, **end_value}
        }

    diagnosis = condition_diagnosis(diagnosis_data, True)

    data = {"resource": {**data_default, **data_period, **diagnosis}}
    merge_data = {**data, **data_request}
    return merge_data


def questionnaire_response_item(data):
    item_data = []
    if data:
        for result in data:
            if "{}".format(result["type"]) in data_questionnaire_response_items():
                item = data_questionnaire_response_items()[result["type"]]
                item_data.append(
                    {
                        "linkId": "{}".format(item["linkId"]),
                        "text": "{}".format(item["text"]),
                        "answer": [
                            {
                                "valueCoding": {
                                    "system": "{}".format(item["system"]),
                                    "code": "{}".format(result["code"]),
                                    "display": "{}".format(result["name"])
                                }
                            }
                        ]
                    }
                )

    return {"item": item_data}


def questionnaire_response(encounter_uuid, questionnaire_response_uuid,
                           patient_id, patient_name,
                           practitioner_id, practitioner_name,
                           data_input, data_encounter):
    questionnaire_response_authored = data_encounter["period_end"]
    questionnaire_response_status = "completed"

    questionnaire_response_item_data = []
    type_diagnosis_code = data_input.get('type_diagnosis', '')
    location_anatomy_code = data_input.get('location_anatomy', '')
    treatment_history_code = data_input.get('treatment_history', '')
    end_result_treatment_code = data_input.get("end_result_treatment", '')

    if type_diagnosis_code and "{}".format(
            type_diagnosis_code) in data_questionnaire_response_type_diagnosis():
        questionnaire_response_item_data.append(
            {
                "type": "type_diagnosis",
                "code": type_diagnosis_code,
                "name": data_questionnaire_response_type_diagnosis()[type_diagnosis_code]
            }
        )

    if location_anatomy_code and "{}".format(
            location_anatomy_code) in data_questionnaire_response_classification_location_anatomy():
        questionnaire_response_item_data.append(
            {
                "type": "classification_location_anatomy",
                "code": location_anatomy_code,
                "name": data_questionnaire_response_classification_location_anatomy()[location_anatomy_code]
            }
        )

    if treatment_history_code and "{}".format(
            treatment_history_code) in data_questionnaire_response_classification_treatment_history():
        questionnaire_response_item_data.append(
            {
                "type": "classification_treatment_history",
                "code": treatment_history_code,
                "name": data_questionnaire_response_classification_treatment_history()[treatment_history_code]
            }
        )

    if end_result_treatment_code and "{}".format(
            end_result_treatment_code) in data_questionnaire_response_end_result_of_treatment_tb():
        questionnaire_response_item_data.append(
            {
                "type": "end_result_of_treatment_tb",
                "code": end_result_treatment_code,
                "name": data_questionnaire_response_end_result_of_treatment_tb()[end_result_treatment_code]
            }
        )

    merge_data = None
    if type_diagnosis_code or location_anatomy_code or treatment_history_code or \
            treatment_history_code or end_result_treatment_code:
        data_request = transaction_request(questionnaire_response_uuid, "QuestionnaireResponse")
        data_default = {
            "resourceType": "QuestionnaireResponse",
            "questionnaire": "https://fhir.kemkes.go.id/Questionnaire/Q0001",
            "status": "{}".format(questionnaire_response_status),
            "subject": {
                "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id),
                "display": "{}".format(patient_name)
            },
            "encounter": {
                "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
            },
            "authored": "{}".format(questionnaire_response_authored),
            "author": {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id),
                "display": "{}".format(practitioner_name)
            },
            "source": {
                "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id)
            },
        }
        data_item = questionnaire_response_item(questionnaire_response_item_data)
        data = {"resource": {**data_default, **data_item}}
        merge_data = {**data, **data_request}

    return merge_data


def medication_request(medication_uuid, medication_request_uuid,
                       encounter_uuid,
                       patient_id, patient_name,
                       practitioner_id, practitioner_name,
                       medication_kfa_name, organization_id):
    data_request = transaction_request(medication_request_uuid, "MedicationRequest")
    data_default = {
        "resource": {
            "resourceType": "MedicationRequest",
            "status": "active",
            "intent": "order",
            "encounter": {
                "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
            },
            "identifier": [{
                "system": "https://sys-ids.kemkes.go.id/prescription/{}".format(organization_id),
                "use": "official",
                "value": "{}".format(uuid.uuid4())
            }],
            "medicationReference": {
                "reference": "{}{}".format(settings.URN_UUID, medication_uuid),
                "display": "{}".format(medication_kfa_name)
            },
            "subject": {
                "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id),
                "display": "{}".format(patient_name)
            },
            "requester": {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id),
                "display": "{}".format(practitioner_name)
            },
        }
    }
    merge_data = {**data_default, **data_request}
    return merge_data


def medication_kfa_code(kfa_code, kfa_name):
    if kfa_code and kfa_name == "" and "{}".format(kfa_code) in data_medication_kfa():
        kfa_name = data_medication_kfa()[kfa_code]

    if kfa_code:
        data_coding = {
            "system": "https://sys-ids.kemkes.go.id/kfa",
            "code": "{}".format(kfa_code),
            "display": "{}".format(kfa_name)
        }
    else:
        data_coding = {
            "system": "https://sys-ids.kemkes.go.id/kfa",
            "display": "{}".format(kfa_name)
        }
    return {"code": {"coding": [data_coding]}}


def medication(encounter_uuid,
               organization_id,
               patient_id, patient_name,
               practitioner_id, practitioner_name,
               data, medication_request_uuid):
    list_data = []
    if data:
        for result in data:
            medication_uuid = uuid.uuid4()

            kfa_code = result["kfa_code"]
            kfa_name = result["kfa_name"]
            form_code = result["form_code"]
            type_code = "NC"

            form_name = None
            if form_code and "{}".format(form_code) in data_medication_form():
                form_name = data_medication_form()[form_code]

            type_name = None
            if type_code and "{}".format(type_code) in data_medication_extension_medication_on_type():
                type_name = data_medication_extension_medication_on_type()[type_code]

            data_request = transaction_request(medication_uuid, "Medication")
            data_default = {

                "resourceType": "Medication",
                "status": "active",
                "manufacturer": {
                    "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
                },
                "identifier": [{
                    "system": "https://sys-ids.kemkes.go.id/medication/{}".format(organization_id),
                    "use": "official",
                    "value": "{}".format(uuid.uuid4())
                }],
                "form": {
                    "coding": [
                        {
                            "system": "https://terminology.kemkes.go.id/CodeSystem/medication-form",
                            "code": "{}".format(form_code),
                            "display": "{}".format(form_name)
                        }
                    ]
                },
                "extension": [
                    {
                        "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/MedicationType",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://terminology.kemkes.go.id/CodeSystem/medication-type",
                                    "code": "{}".format(type_code),
                                    "display": "{}".format(type_name)
                                }
                            ]
                        }
                    }
                ]
            }

            data_kfa = medication_kfa_code(kfa_code, kfa_name)
            data = {"resource": {**data_default, **data_kfa}}
            merge_data = {**data, **data_request}
            list_data.append(merge_data)

            list_data.append(
                medication_request(
                    medication_uuid, medication_request_uuid,
                    encounter_uuid,
                    patient_id, patient_name,
                    practitioner_id, practitioner_name,
                    kfa_name,
                    organization_id
                )
            )
    return list_data


def diagnostic_report_category(report_type):
    data_code = {}
    if "{}".format(report_type) in data_diagnostic_report_category():
        code = data_diagnostic_report_category()[report_type]
        data_code = {"category": [{"coding": [code]}]}
    return data_code


def diagnostic_report_code(report_type):
    data_code = {}
    if "{}".format(report_type) in data_diagnostic_report_code():
        code = data_diagnostic_report_code()[report_type]
        data_code = {"code": {"coding": [code]}}
    return data_code


def diagnostic_report(
        encounter_uuid,
        observation_uuid,
        diagnostic_report_uuid,
        organization_id,
        patient_id,
        practitioner_id,
        local_id,
        diagnostic_report_type,
        diagnostic_report_issued, medication_request_uuid):
    data_request = transaction_request(diagnostic_report_uuid, "DiagnosticReport")
    data_default = {
        "resourceType": "DiagnosticReport",
        "identifier": [
            {
                "system": "https://sys-ids.kemkes.go.id/diagnostic/{}/lab".format(organization_id),
                "use": "official",
                "value": "{}".format(local_id)
            }
        ],
        "status": "final",
        "subject": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id)
        },
        "encounter": {
            "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
        },
        "performer": [
            {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id)
            },
            {
                "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
            }
        ],
        "basedOn": [
            {
                "reference": "{}{}".format(settings.URN_UUID, medication_request_uuid)
            }
        ],
        "issued": "{}".format(diagnostic_report_issued),
    }

    result_observation_uuid = []
    for result in observation_uuid:
        result_observation_uuid.append({"reference": "{}{}".format(settings.URN_UUID, result)})

    data_category = diagnostic_report_category(diagnostic_report_type)
    data_code = diagnostic_report_code(diagnostic_report_type)
    data_result = {"result": result_observation_uuid}

    data = {"resource": {**data_default, **data_code, **data_category, **data_result}}
    merge_data = {**data, **data_request}
    return merge_data


def observation_bta_culture_thorax_code(observation_type):
    data_code = {}
    if "{}".format(observation_type) in data_observation_bta_culture_thorax_code():
        code = data_observation_bta_culture_thorax_code()[observation_type]
        data_code = {"code": {"coding": [code]}}
    return data_code


def observation_bta_culture_thorax_value(data_value):
    data = {}
    if "{}".format(data_value.lower()) in data_observation_bta_culture_thorax_value():
        value = data_observation_bta_culture_thorax_value()[data_value.lower()]
        if data_value in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            data = {
                "valueQuantity": value
            }
        elif data_value in ["tidak dilakukan", "not-performed"]:
            data = {
                "dataAbsentReason": {"coding": [value]}
            }
        else:
            data = {
                "interpretation": [{"coding": [value]}]
            }
    return data


def observation_bta_culture_thorax(
        encounter_uuid,
        observation_uuid,
        organization_id,
        patient_id,
        practitioner_id,
        observation_type,
        data_input, medication_request_uuid):
    local_id = data_input["local_id"]
    observation_category_issued = escape(data_input["issued"])
    observation_value = data_input["value"]

    data_request = transaction_request(observation_uuid, "Observation")
    data_default = {
        "resourceType": "Observation",
        "identifier": [
            {
                "system": "{}{}".format(settings.OBSERVATION_SYSTEM_URL, organization_id),
                "value": "{}".format(local_id)
            }
        ],
        "status": "final",
        "subject": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id)
        },
        "encounter": {
            "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
        },
        "performer": [
            {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id)
            },
            {
                "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
            }
        ],
        "issued": "{}".format(observation_category_issued),
        "category": [
            {
                "coding": [
                    {
                        "system": settings.OBSERVATION_CATEGORY_SYSTEM,
                        "code": "imaging" if observation_type in ["thorax-ap", "thorax-pa"] else "laboratory",
                        "display": "Imaging" if observation_type in ["thorax-ap", "thorax-pa"] else "Laboratory"
                    }
                ]
            }
        ],
    }
    data_code = observation_bta_culture_thorax_code(observation_type)
    data_value = observation_bta_culture_thorax_value(observation_value)

    data = {"resource": {**data_default, **data_code, **data_value}}
    merge_data = {**data, **data_request}

    return [
        merge_data,
        diagnostic_report(
            encounter_uuid,
            [observation_uuid],
            uuid.uuid4(),
            organization_id,
            patient_id,
            practitioner_id,
            local_id,
            observation_type,
            observation_category_issued,
            medication_request_uuid
        )
    ]


def observation_tcm_dna_value(observation_value):
    data = {}
    if "{}".format(observation_value) in data_observation_tcm_dna():
        value = data_observation_tcm_dna()[observation_value]
        if observation_value in ["detected", "not-detected"]:
            data = {
                "valueCodeableConcept": {"coding": [value]}
            }
        elif observation_value in ["invalid", "error", "no result", "tidak dilakukan"]:
            data = {
                "dataAbsentReason": {"coding": [value]}
            }
        elif observation_value == "neg":
            data = {
                "interpretation": [{"coding": [value]}]
            }
    return data


def observation_tcm_dna(encounter_uuid,
                        observation_uuid,
                        organization_id,
                        patient_id,
                        practitioner_id,
                        observation_value,
                        data_input):
    local_id = data_input["local_id"]
    observation_category_issued = escape(data_input["issued"])

    data_request = transaction_request(observation_uuid, "Observation")
    data_default = {
        "resourceType": "Observation",
        "identifier": [
            {
                "system": "{}{}".format(settings.OBSERVATION_SYSTEM_URL, organization_id),
                "value": "{}".format(local_id)
            }
        ],
        "status": "final",
        "subject": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id)
        },
        "encounter": {
            "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
        },
        "performer": [
            {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id)
            },
            {
                "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
            }
        ],
        "issued": "{}".format(observation_category_issued),
        "category": [
            {
                "coding": [
                    {
                        "system": settings.OBSERVATION_CATEGORY_SYSTEM,
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "https://loinc.org",
                    "code": "88874-3",
                    "display": "Mycobacteriu m tuberculosis complex DNA [Presence] in Isolate or Specimen by Molecular genetics method"
                }
            ]
        },
    }

    data_value = observation_tcm_dna_value(observation_value)
    data = {"resource": {**data_default, **data_value}}
    merge_data = {**data, **data_request}

    return merge_data


def observation_tcm_sputum_value(observation_value):
    data = {}
    if "{}".format(observation_value) in data_observation_tcm_sputum():
        value = data_observation_tcm_sputum()[observation_value]
        if observation_value in ["detected", "not-detected", "indeterminate"]:
            data = {
                "valueCodeableConcept": {"coding": [value]}
            }
        elif observation_value in ["negative", "rifampicin sensitive", "rifampicin resistant",
                                   "rifampicin indeterminate"]:
            data = {
                "interpretation": [{"coding": [value]}]
            }
    return data


def observation_tcm_sputum(encounter_uuid,
                           observation_uuid,
                           organization_id,
                           patient_id,
                           practitioner_id,
                           data_input):
    local_id = data_input["local_id"]
    observation_category_issued = data_input["issued_rifampicin"]
    observation_value = data_input["value"]

    data_request = transaction_request(observation_uuid, "Observation")
    data_default = {
        "resourceType": "Observation",
        "identifier": [
            {
                "system": "{}{}".format(settings.OBSERVATION_SYSTEM_URL, organization_id),
                "value": "{}".format(local_id)
            }
        ],
        "status": "final",
        "subject": {
            "reference": settings.URL_FORMAT.format(settings.PATIENT_RESOURCE, patient_id)
        },
        "encounter": {
            "reference": "{}{}".format(settings.URN_UUID, encounter_uuid)
        },
        "performer": [
            {
                "reference": settings.URL_FORMAT.format(settings.PRACTITIONER_RESOURCE, practitioner_id)
            },
            {
                "reference": settings.URL_FORMAT.format(settings.ORGANIZATION_RESOURCE, organization_id)
            }
        ],
        "issued": "{}".format(escape(observation_category_issued)),
        "category": [
            {
                "coding": [
                    {
                        "system": settings.OBSERVATION_CATEGORY_SYSTEM,
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "https://loinc.org",
                    "code": "89372-7",
                    "display": "Mycobacteriu m tuberculosis complex rpoB gene rifAMPin resistance mutation [Presence] by Molecular method"
                }
            ]
        },
    }
    data_tcm = {}
    if observation_value == "rif-sen":
        data_value = observation_tcm_sputum_value("not-detected")
        data_interpretation = observation_tcm_sputum_value("rifampicin sensitive")
        data_tcm = {**data_value, **data_interpretation}
    elif observation_value == "rif-res":
        data_value = observation_tcm_sputum_value("detected")
        data_interpretation = observation_tcm_sputum_value("rifampicin resistant")
        data_tcm = {**data_value, **data_interpretation}
    elif observation_value == "rif-indet":
        data_value = observation_tcm_sputum_value("indeterminate")
        data_interpretation = observation_tcm_sputum_value("rifampicin indeterminate")
        data_tcm = {**data_value, **data_interpretation}

    data = {"resource": {**data_default, **data_tcm}}
    merge_data = {**data, **data_request}
    return merge_data


def response_ihs_id_organization_location(user_id, url):
    result = {}
    try:
        response = requests.request(
            'GET', url=url, headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
        )
        if response.status_code == 200:
            response_json = response.json()
            result = {
                "id": response_json['id'],
                "name": response_json['name']
            }
        elif response.status_code == 401:
            access_token = request_auth(user_id)
            if access_token:
                response = requests.request(
                    'GET', url=url, headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
                )
                if response.status_code == 200:
                    response_json = response.json()
                    result = {
                        "id": response_json['id'],
                        "name": response_json['name']
                    }

    except Exception as e:
        logger.error(e)
    return result


def response_ihs_id_patient_practitioner(user_id, url):
    result = None
    try:
        response = requests.request(
            'GET', url=url, headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
        )
        if response.status_code == 200:
            result = True
        elif response.status_code == 401:
            access_token = request_auth(user_id)
            if access_token:
                response = requests.request(
                    'GET', url=url, headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
                )
                if response.status_code == 200:
                    result = True
    except Exception as e:
        logger.error(e)

    return result


def request_data_organization(user_id, ihs_id):
    url = "{}/{}/{}".format(BASE_URL, settings.ORGANIZATION_RESOURCE, ihs_id)
    result = response_ihs_id_organization_location(user_id, url)
    return result


def request_data_location(user_id, ihs_id):
    url = "{}/Location/{}".format(BASE_URL, ihs_id)
    result = response_ihs_id_organization_location(user_id, url)
    return result


def request_data_patient_ihs_id(user_id, ihs_id):
    url = "{pronoun}/Patient/{ihs_id}".format(pronoun=settings.BASE_URL_NEG if ENV_API_KEY == "neg" else BASE_URL, ihs_id=ihs_id)
    result = response_ihs_id_patient_practitioner(user_id, url)
    return result


def request_data_practitioner_ihs_id(user_id, ihs_id):
    url = "{pronoun}/Practitioner/{ihs_id}".format(pronoun=settings.BASE_URL_NEG if ENV_API_KEY == "neg" else BASE_URL, ihs_id=ihs_id)
    result = response_ihs_id_patient_practitioner(user_id, url)
    return result


def parsing_data_patient_or_practitioner(resource, status_code, url):
    if url.find('Patient') != -1:
        data = {
            "id": resource['id'],
            "name": None,
            "status_code": status_code,
            "detail": None
        }
    else:
        data = {
            "id": resource['id'],
            "name": resource['name'][0]['text'],
            "status_code": status_code,
            "detail": None
        }
    return data


def response_nik(user_id, url, params):
    result = {}
    try:
        response = requests.request(
            'GET', url=url, params=params,
            headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
        )
        if response.status_code == 200:
            response_json = response.json()
            if "entry" in response_json and "resource" in response_json['entry'][0]:
                entry_resource = response_json['entry'][0]['resource']
                result = parsing_data_patient_or_practitioner(entry_resource, response.status_code, url)
        elif response.status_code == 401:
            access_token = request_auth(user_id)
            if access_token:
                response = requests.request(
                    'GET', url=url, params=params,
                    headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
                )
                if response.status_code == 200:
                    response_json = response.json()
                    if "entry" in response_json and "resource" in response_json['entry'][0]:
                        entry_resource = response_json['entry'][0]['resource']
                        result = parsing_data_patient_or_practitioner(entry_resource, response.status_code, url)
    except Exception as e:
        logger.error(e)
    return result


def request_data_patient(user_id, nik):
    url = "{pronoun}/Patient".format(pronoun=settings.BASE_URL_NEG if ENV_API_KEY == "neg" else BASE_URL)
    params = {
        'identifier': 'https://fhir.kemkes.go.id/id/nik|{}'.format(nik)
    }
    result = response_nik(user_id, url, params)
    return result


def request_data_practitioner(user_id, nik):
    url = "{pronoun}/Practitioner".format(pronoun=settings.BASE_URL_NEG if ENV_API_KEY == "neg" else BASE_URL)
    params = {
        'identifier': 'https://fhir.kemkes.go.id/id/nik|{}'.format(nik)
    }
    result = response_nik(user_id, url, params)
    return result


def transaction_error(user_id, organization, location, patient, practitioner):
    error = []
    if cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)) is None:
        error.append({'credential': "client id and client secret is not valid"})
    if organization is None:
        error.append({"organization": settings.NOT_FOUND})

    if location is None:
        error.append({"location": settings.NOT_FOUND})

    if patient is None:
        error.append({"patient": settings.NOT_FOUND})
    if practitioner is None:
        error.append({"practitioner": settings.NOT_FOUND})

    return error


def response_data_ihs(data):
    response_data = data
    if isinstance(data, dict) and "entry" in data:
        for result in data['entry']:
            response = result["response"]
            if "resourceType" in response and response["resourceType"] == "EpisodeOfCare":
                response_data = {"episode_of_care_id": response["resourceID"]}
                break
    return response_data


def request_data_bundle(resource_data, location_id, user_id, log_id = None):
    url = "{}".format(BASE_URL)
    user = User.objects.get(pk=user_id)
    try:    
        log_id = Log.objects.get(pk=log_id)
    except Log.DoesNotExist:
        log_id = None

    location = Location.objects.get(pk=location_id)

    transaction = Transaction()
    transaction.location = location
    transaction.created_by = user

    status_process = "pending"
    response_data = None
    try:
        response = requests.request(
            "POST", url=url, json=resource_data,
            headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
        )
        if response.status_code in [200, 201]:
            transaction.log = log_id
            transaction.status = TransactionStatus.SUCCESS
            transaction.response_data = response.json()
            transaction.save()
            response_data = response_data_ihs(response.json())
            status_process = "success"
        elif response.status_code == 401:
            access_token = request_auth(user_id)
            if access_token:
                response = requests.request(
                    "POST", url=url, json=resource_data,
                    headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
                )
                if response.status_code in [200, 201]:
                    transaction.log = log_id
                    transaction.status = TransactionStatus.SUCCESS
                    transaction.response_data = response.json()
                    transaction.save()
                    status_process = "success"
                    response_data = response_data_ihs(response.json())
        elif response.status_code in [500, 502, 503, 504]:
            transaction.log = log_id
            transaction.status = TransactionStatus.PENDING
            transaction.raw_data = resource_data
            transaction.error_messages = response.json()
            transaction.save()
            response_data = response_data_ihs(response.json())
        else:
            transaction.log = log_id
            transaction.status = TransactionStatus.ERROR
            transaction.error_messages = response.json()
            transaction.save()
            status_process = "error"
            response_data = {"detail": "Data yang dikirim terdapat kesalahan, silahkan kontak administrator."}
    except Exception as e:
        transaction.log = log_id
        transaction.status = TransactionStatus.PENDING
        transaction.raw_data = resource_data
        transaction.error_messages = e
        transaction.save()
        response_data = {"detail": "{}".format(e)}
    logger.info(" === Generate Transaction === ")
    logger.info("Transaction id {} - Resource Data {}".format(transaction.pk, resource_data))
    return {"id": transaction.pk, "status_process": status_process, "response_data": response_data}


def data_fhir_validation(data, user_id):
    location_id, organization_id = None, None
    patient_id, practitioner_id = None, None

    if "entry" in data:
        for result in data["entry"]:
            resource = result["resource"]
            resource_type = resource["resourceType"]
            if resource_type == "Encounter":
                location = resource["location"][0]["location"]["reference"]
                organization = resource["serviceProvider"]["reference"]
                patient = resource["subject"]["reference"]
                practitioner = resource["participant"][0]["individual"]["reference"]

                location_id = location.replace("Location/", "")
                organization_id = organization.replace("Organization/", "")
                patient_id = patient.replace("Patient/", "")
                practitioner_id = practitioner.replace("Practitioner/", "")

                break

    if location_id and organization_id and patient_id and practitioner_id:
        organization, location = None, None

        check_organization = Organization.objects.filter(ihs_id=organization_id).first()
        if check_organization:
            organization = check_organization
        else:
            request_organization = request_data_organization(user_id, organization_id)
            if request_organization:
                organization = Organization.objects.create(
                    ihs_id=request_organization['id'],
                    name=request_organization['name']
                )
        if organization is not None:
            check_location = Location.objects.filter(
                ihs_id=location_id, organization=organization
            ).first()
            if check_location:
                location = check_location
            else:
                request_location = request_data_location(user_id, location_id)
                if request_location:
                    location = Location.objects.create(
                        organization=organization,
                        ihs_id=request_location['id'],
                        name=request_location['name']
                    )

        patient = request_data_patient_ihs_id(user_id, patient_id)
        practitioner = request_data_practitioner_ihs_id(user_id, practitioner_id)

        logger.info("organization")
        logger.info(organization)
        logger.info("location")
        logger.info(location)
        logger.info("patient")
        logger.info(patient)
        logger.info("practitioner")
        logger.info(practitioner)
        if organization and location and patient and practitioner:
            return request_data_bundle(data, location.id, user_id)
        else:
            error = transaction_error(user_id, organization, location, patient, practitioner)
    else:
        error = transaction_error(user_id, organization_id, location_id, patient_id, practitioner_id)

    user = User.objects.get(pk=user_id)
    transaction = Transaction()
    transaction.status = TransactionStatus.FAILED
    transaction.error_messages = error
    transaction.created_by = user
    transaction.save()
    return {"id": transaction.pk, "status_process": "failed", "response_data": response_data_ihs(error)}


def request_data_transaction_retry(transaction_id):
    transaction = Transaction.objects.get(pk=transaction_id)    
    log_status = None
    count_retry = transaction.count_retry + 1
    transaction.count_retry = count_retry
    url = "{}".format(BASE_URL)
    result = "pending"
    
    if transaction.raw_data is not None and count_retry <= 7:
        user_id = transaction.created_by.id
        transaction.last_retry = timezone.now()
        try:
            response = requests.request(
                "POST", url=url, json=transaction.raw_data,
                headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
            )
            if response.status_code in [200, 201]:
                transaction.status = TransactionStatus.SUCCESS
                transaction.response_data = response.json()
                transaction.error_messages = None
                transaction.raw_data = None
                transaction.save()
                
                log_status = TransactionStatus.SUCCESS
                result = "success"
            elif response.status_code == 401:
                access_token = request_auth(user_id)
                if access_token:
                    response = requests.request(
                        "POST", url=url, json=transaction.raw_data,
                        headers=request_data_headers(cache.get('{}_{}'.format(settings.ACCESS_TOKEN_USER, user_id)))
                    )
                    if response.status_code in [200, 201]:
                        transaction.status = TransactionStatus.SUCCESS
                        transaction.response_data = response.json()
                        transaction.error_messages = None
                        transaction.raw_data = None
                        transaction.save()

                        log_status = TransactionStatus.SUCCESS
                        result = "success"
            elif response.status_code in [500, 502, 503, 504]:
                transaction.status = TransactionStatus.PENDING
                transaction.error_messages = response.json()
                transaction.save()
                
                log_status = TransactionStatus.PENDING
            else:
                transaction.status = TransactionStatus.ERROR
                transaction.error_messages = response.json()
                transaction.raw_data = None
                transaction.save()
                
                log_status = TransactionStatus.ERROR
                result = "error"
        except Exception as e:
            if count_retry >= 8:
                transaction.status = TransactionStatus.FAILED
                transaction.raw_data = None
                transaction.error_messages = e
                result = "failed"
                
                log_status = TransactionStatus.FAILED
            transaction.save()
            logger.error(e)   
            
        try:
            log = Log.objects.get(pk=transaction.log.id)
            log.satusehat_status = log_status
            log.save()
        except Log.DoesNotExist:
            pass
    else:
        transaction.status = TransactionStatus.FAILED
        transaction.raw_data = None
        transaction.error_messages = {"retry": "has reached the maximum repetition limit"}
        result = "failed"
        transaction.save()
        
        try:
            log = Log.objects.get(pk=transaction.log.id)
            log.satusehat_status = log_status
            log.save()
        except Log.DoesNotExist:
            pass
    return result


def bundle(user_id, data_input, log_id = None):    
    organization_id = data_input["organization_id"]
    location_id = data_input["location_id"]
    patient_nik = data_input["patient_nik"]
    practitioner_nik = data_input['practitioner_nik']
    data_input_encounter = data_input["encounter"]
    data_input_condition = data_input["condition"]
    data_input_episode_of_care = data_input["episode_of_care"]
    data_input_questionnaire_response = data_input[
        "questionnaire_response"] if "questionnaire_response" in data_input else None
    try:
        data_input_medication = data_input["medication"]
    except KeyError:
        data_input_medication = None

    try:
        data_input_observation = data_input["observation"]
    except KeyError:
        data_input_observation = None

    organization, location = None, None
    patient_id, patient_name = None, None
    practitioner_id, practitioner_name = None, None

    check_organization = Organization.objects.filter(ihs_id=organization_id).first()
    if check_organization:
        organization = check_organization
    else:
        request_organization = request_data_organization(user_id, organization_id)
        if request_organization:
            organization = Organization.objects.create(
                ihs_id=request_organization['id'],
                name=request_organization['name']
            )

    if organization is not None:
        check_location = Location.objects.filter(
            ihs_id=location_id, organization=organization
        ).first()
        if check_location:
            location = check_location
        else:
            request_location = request_data_location(user_id, location_id)
            if request_location:
                location = Location.objects.create(
                    organization=organization,
                    ihs_id=request_location['id'],
                    name=request_location['name']
                )

    request_patient = request_data_patient(user_id, patient_nik)
    if request_patient:
        patient_id = request_patient['id']
        patient_name = ""

    request_practitioner = request_data_practitioner(user_id, practitioner_nik)
    if request_practitioner:
        practitioner_id = request_practitioner['id']
        practitioner_name = request_practitioner['name']

    logger.info("organization")
    logger.info(organization)
    logger.info("location")
    logger.info(location)
    logger.info("patient")
    logger.info(patient_id)
    logger.info("practitioner")
    logger.info(practitioner_id)

    if organization and location and patient_id and practitioner_id:
        user = User.objects.get(pk=user_id)
        service_provider = user.organization_id
        encounter_uuid = uuid.uuid4()
        questionnaire_response_uuid = uuid.uuid4()
        episode_of_care_uuid = uuid.uuid4()
        medication_request_uuid = uuid.uuid4()

        episode_of_care_ihs_id = data_input_episode_of_care["ihs_id"] \
            if "ihs_id" in data_input_episode_of_care else None

        condition_uuid_list = defaultdict(list)
        data_diagnosis = []
        for result in data_input_condition:
            condition_uuid_tb = uuid.uuid4()
            icd_x_code_tb = result["icd_x_code_tb"]
            icd_x_name_tb = None
            if icd_x_code_tb and "{}".format(icd_x_code_tb) in data_icd_x_code():
                icd_x_name_tb = data_icd_x_code()[icd_x_code_tb]

            condition_uuid_list[icd_x_code_tb].append(condition_uuid_tb)

            data_diagnosis.append(
                {
                    "condition_uuid": condition_uuid_tb,
                    "icd_x_name": icd_x_name_tb,
                    "diagnosis_code": "DD",
                    "diagnosis_name": "Discharge diagnosis"
                }
            )
            if "others" in result and result["others"] is not None:
                for result_other in result["others"]:
                    condition_uuid = uuid.uuid4()
                    icd_x_code = result_other["icd_x_code"]
                    icd_x_name = result_other["icd_x_code_name"]
                    data_diagnosis.append(
                        {
                            "condition_uuid": condition_uuid,
                            "icd_x_name": icd_x_name,
                            "diagnosis_code": "DD",
                            "diagnosis_name": "Discharge diagnosis"
                        }
                    )
                    condition_uuid_list[icd_x_code].append(condition_uuid)
        data_resource = []
        data_resource_encounter = encounter(
            encounter_uuid,
            organization.ihs_id,
            location.ihs_id,
            location.name,
            patient_id,
            patient_name,
            practitioner_id,
            practitioner_name,
            data_input_encounter,
            service_provider,
            data_diagnosis,
            episode_of_care_uuid,
            episode_of_care_ihs_id
        )

        data_resource_condition = condition(
            encounter_uuid,
            condition_uuid_list,
            patient_id,
            patient_name,
            data_input_condition
        )

        data_resource_medication = medication(
            encounter_uuid,
            organization.ihs_id,
            patient_id,
            patient_name,
            practitioner_id,
            practitioner_name,
            data_input_medication,
            medication_request_uuid
        )

        data_resource.append(data_resource_encounter)

        if data_input_questionnaire_response:
            data_resource_questionnaire_response = questionnaire_response(
                encounter_uuid,
                questionnaire_response_uuid,
                patient_id,
                patient_name,
                practitioner_id,
                practitioner_name,
                data_input_questionnaire_response,
                data_input_encounter
            )
            if data_resource_questionnaire_response:
                data_resource.append(data_resource_questionnaire_response)
        if data_input_observation:
            for result in data_input_observation:
                observation_uuid = uuid.uuid4()

                type_observation = result["type_observation"]
                value_observation = result["value"]
                local_id_observation = result["local_id"]
                issued_observation = result["issued"]

                if type_observation in list(data_type_observation_bta()):
                    data_resource_observation = observation_bta_culture_thorax(
                        encounter_uuid,
                        observation_uuid,
                        organization.ihs_id,
                        patient_id,
                        practitioner_id,
                        "bta",
                        result,
                        medication_request_uuid
                    )
                    data_resource = data_resource + data_resource_observation
                elif type_observation in list(data_type_observation_thorax()):
                    if type_observation == "photo-thorax-ap":
                        type_thorax = "thorax-ap"
                    else:
                        type_thorax = "thorax-pa"
                    data_resource_observation = observation_bta_culture_thorax(
                        encounter_uuid,
                        observation_uuid,
                        organization.ihs_id,
                        patient_id,
                        practitioner_id,
                        type_thorax,
                        result,
                        medication_request_uuid
                    )
                    data_resource = data_resource + data_resource_observation

                elif type_observation == "culture-treatment":
                    data_resource_observation = observation_bta_culture_thorax(
                        encounter_uuid,
                        observation_uuid,
                        organization.ihs_id,
                        patient_id,
                        practitioner_id,
                        "biakan",
                        result,
                        medication_request_uuid
                    )
                    data_resource = data_resource + data_resource_observation
                elif type_observation == "tcm":
                    if value_observation in ["rif-sen", "rif-res", "rif-indet"]:
                        observation_uuid_dna_uuid = uuid.uuid4()
                        observation_uuid_sputum_uuid = uuid.uuid4()
                        observation_dna = observation_tcm_dna(
                            encounter_uuid,
                            observation_uuid_dna_uuid,
                            organization.ihs_id,
                            patient_id,
                            practitioner_id,
                            "detected",
                            result
                        )
                        observation_sputum = observation_tcm_sputum(
                            encounter_uuid,
                            observation_uuid_sputum_uuid,
                            organization.ihs_id,
                            patient_id,
                            practitioner_id,
                            result
                        )
                        data_resource.append(observation_dna)
                        data_resource.append(observation_sputum)

                        data_resource.append(
                            diagnostic_report(
                                encounter_uuid,
                                [observation_uuid_dna_uuid, observation_uuid_sputum_uuid],
                                uuid.uuid4(),
                                organization.ihs_id,
                                patient_id,
                                practitioner_id,
                                local_id_observation,
                                "tcm",
                                issued_observation,
                                medication_request_uuid
                            )
                        )
                    else:
                        observation_uuid_dna_uuid = uuid.uuid4()
                        if value_observation == "neg":
                            dna_value = "not-detected"
                        else:
                            dna_value = value_observation

                        observation_dna = observation_tcm_dna(
                            encounter_uuid,
                            observation_uuid_dna_uuid,
                            organization.ihs_id,
                            patient_id,
                            practitioner_id,
                            dna_value,
                            result
                        )
                        data_resource.append(observation_dna)
                        data_resource.append(
                            diagnostic_report(
                                encounter_uuid,
                                [observation_uuid_dna_uuid],
                                uuid.uuid4(),
                                organization.ihs_id,
                                patient_id,
                                practitioner_id,
                                local_id_observation,
                                "tcm",
                                issued_observation,
                                medication_request_uuid
                            )
                        )

        data_resource_episode_of_care = episode_of_care(
            episode_of_care_uuid,
            organization.ihs_id,
            patient_id,
            patient_name,
            practitioner_id,
            practitioner_name,
            data_input_episode_of_care,
            data_diagnosis
        )
        data_resource.append(data_resource_episode_of_care)
        if not data_input_medication:
            data_merge = {
                "resourceType": "Bundle",
                "type": "transaction",
                "entry": data_resource + data_resource_condition
            }
        else:
            data_merge = {
                "resourceType": "Bundle",
                "type": "transaction",
                "entry": data_resource + data_resource_medication + data_resource_condition
            }
        return request_data_bundle(data_merge, location.id, user_id, log_id)
    else:
        user = User.objects.get(pk=user_id)
        
        try:    
            log_id = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            log_id = None
    
        error = transaction_error(user_id, organization, location, patient_id, practitioner_id)
        transaction = Transaction()
        transaction.log = log_id
        transaction.status = TransactionStatus.ERROR
        transaction.error_messages = error
        transaction.created_by = user
        transaction.save()
        return {"id": transaction.pk, "status_process": "error", "response_data": error}

import requests
from django.conf import settings
from apps.users.models import User, Province, District
from apps.organization.models import Organization
from django.contrib.auth.hashers import check_password
from .models import TransactionSitb, TransactionStatus, Log
from apps.transaction.data import data_icd_x_code, data_encounter_class, data_icd_x_code, data_condition_clinical_status, data_questionnaire_response_type_diagnosis_sitb, data_questionnaire_response_classification_location_anatomy_sitb, data_questionnaire_response_classification_treatment_history_sitb, data_questionnaire_response_end_result_of_treatment_tb_sitb, data_type_observation_bta, data_type_observation_thorax, data_medication_kfa
from usaid.settings import AUTH_URL, BASE_URL
from datetime import datetime
from django.utils import timezone
import calendar
import logging

logger = logging.getLogger(__name__)

def transaction_error(data_resource_patient, data_observation, data_faskes):
    response = {
        "status_process": "error", 
        "response_data": []
    }
            
    if 'error' in data_resource_patient:
        for error_patinent in data_resource_patient['response_data']:
            response['response_data'].append(error_patinent)

    if 'error' in data_observation:
        for error_observation in data_observation['response_data']:
            response['response_data'].append(error_observation)

    if 'error' in data_faskes:
        for error_faskes in data_faskes['response_data']:
            response['response_data'].append(error_faskes)

    return response

def request_data_transaction_sitb_retry(transaction_sitb_id):
    transaction_sitb = TransactionSitb.objects.get(pk=transaction_sitb_id)
    count_retry = transaction_sitb.count_retry + 1
    url = "{}".format(settings.BASE_URL_SITB)
    date = datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    log = Log.objects.get(pk=transaction_sitb.log.id)
    result = "pending"

    if transaction_sitb.raw_data is not None and count_retry <= 7:
        user_id = transaction_sitb.created_by.id
        user = User.objects.get(pk=user_id)
        transaction_sitb.last_retry = timezone.now()

        try:
            response = requests.request(
                "POST", url=url, json=transaction_sitb.raw_data, 
                headers={
                    "X-rs-id": user.sitb_rs_id,
                    "X-pass": user.sitb_rs_pass,
                    "X-Timestamp": str(utc_time),
                    "Content-Type": 'application/json',
                }
            )
            if response.status_code == 200:
                response_data_raw = response.json()
                response_data = response_data_raw if isinstance(response_data_raw, dict) else "Unexpected response format."
            
                # jika status == gagal / update gagal
                if isinstance(response_data, dict) and response_data.get('status') in [settings.STATUS_RESPONSE_SITB['GAGAL'], settings.STATUS_RESPONSE_SITB['UPDATE_GAGAL']]:
                    transaction_sitb.status =  TransactionStatus.ERROR
                    transaction_sitb.response_data = response_data
                    transaction_sitb.raw_data = None
                    
                    log_status = TransactionStatus.ERROR
                    result = "error"
                
                # jika status == berhasil / update berhasil
                elif isinstance(response_data, dict) and response_data.get('status') in [settings.STATUS_RESPONSE_SITB['BERHASIL'], settings.STATUS_RESPONSE_SITB['UPDATE_BERHASIL']]:
                    transaction_sitb.status =  TransactionStatus.SUCCESS
                    transaction_sitb.response_data = {"id_tb_03": response_data['id_tb_03']}
                    transaction_sitb.error_messages = None
                    transaction_sitb.raw_data = None
                    
                    log_status = TransactionStatus.SUCCESS
                    result = "success"
                else:
                    transaction_sitb.status = TransactionStatus.ERROR
                    transaction_sitb.response_data = response_data
                    transaction_sitb.raw_data = None
        
                    log_status = TransactionStatus.ERROR
                    result = "error"
                    
            elif response.status_code in [500, 502, 503, 504]:            
                transaction_sitb.status = TransactionStatus.PENDING
                transaction_sitb.error_messages = response_data
                
                log_status = TransactionStatus.PENDING
            else:
                transaction_sitb.status = TransactionStatus.ERROR
                transaction_sitb.error_messages = response_data
                transaction_sitb.raw_data = None
                
                log_status = TransactionStatus.ERROR
                result = "error"
        except Exception as e:        
            transaction_sitb.status = TransactionStatus.PENDING
            transaction_sitb.error_messages = e
            
            log_status = TransactionStatus.PENDING
            
        log.sitb_status = log_status

        transaction_sitb.count_retry = count_retry

        if count_retry == 7 and log_status == TransactionStatus.PENDING:
            log.sitb_status = TransactionStatus.FAILED
            transaction_sitb.raw_data = None
            transaction_sitb.status = TransactionStatus.FAILED
            result = "failed"

        log.save()
        transaction_sitb.save()

    return result
            

def request_data_bundle(data, user_id, log_id):
    url = "{}".format(settings.BASE_URL_SITB)
    user = User.objects.get(pk=user_id)
    date = datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())
    
    try:
        log_id = Log.objects.get(pk=log_id)
    except Exception:
        log_id = None

    status_process = "pending"
    response_data = None
    try:
        response = requests.request(
            "POST", url=url, json=data, 
            headers={
                "X-rs-id": user.sitb_rs_id,
                "X-pass": user.sitb_rs_pass,
                "X-Timestamp": str(utc_time),
                "Content-Type": 'application/json',
            }
        )

        if response.status_code == 200:
            response_data_raw = response.json()
            response_data = response_data_raw if isinstance(response_data_raw, dict) else "Unexpected response format."
            
            # jika status == gagal / update gagal
            if isinstance(response_data, dict) and response_data.get('status') in [settings.STATUS_RESPONSE_SITB['GAGAL'], settings.STATUS_RESPONSE_SITB['UPDATE_GAGAL']]:
                transaction_sitb = TransactionSitb.objects.create(
                    log = log_id,
                    created_by = user,
                    status = TransactionStatus.ERROR,
                    response_data = response_data,
                )
                status_process = 'error'
            
            # jika status == berhasil / update berhasil
            elif isinstance(response_data, dict) and response_data.get('status') in [settings.STATUS_RESPONSE_SITB['BERHASIL'], settings.STATUS_RESPONSE_SITB['UPDATE_BERHASIL']]:
                response_data = {"id_tb_03": response_data['id_tb_03']}
                transaction_sitb = TransactionSitb.objects.create(
                    log = log_id,
                    created_by = user,
                    status = TransactionStatus.SUCCESS,
                    response_data = response_data
                )
                status_process = 'success'
            else:
                transaction_sitb = TransactionSitb.objects.create(
                    log = log_id,
                    created_by = user,
                    status = TransactionStatus.ERROR,
                    response_data = response_data
                )
                status_process = 'error'
                
        elif response.status_code in [500, 502, 503, 504]:            
            transaction_sitb= TransactionSitb.objects.create(
                log = log_id,
                status = TransactionStatus.PENDING,
                raw_data = data,
                error_messages = response_data,
                created_by = user,
            )
        else:
            transaction_sitb = TransactionSitb.objects.create(
                log = log_id,
                created_by = user,
                status = TransactionStatus.ERROR,
                error_messages = response.json(),
            )
            status_process = 'error'
            response_data = {"detail": "Data yang dikirim terdapat kesalahan, silahkan kontak administrator."}
    except Exception as e:        
        transaction_sitb = TransactionSitb.objects.create(
            log = log_id,
            created_by = user,
            status = TransactionStatus.PENDING,
            raw_data = data,
            error_messages = e
        )
        response_data = {"detail": "{}".format(e)}

    return {"id": transaction_sitb.pk, "status_process": status_process, "response_data": response_data}

def patient(data):
    error = []
    
    # validate patient id_propinsi_pasien not null
    if data["province"] != None or data["province"] != "":
        get_province = Province.objects.filter(code=data["province"]).first()
        if get_province == None:
            error.append({"province": "province is not valid."})


    # validate patient kd_kabupaten_pasien not null
    if data["district"] != None or data["district"] != "":
        get_district = District.objects.filter(code=data["district"]).first()
        if get_district == None:
            error.append({"district": "district is not valid."})

    if error:
        return {"error": "error", "response_data": error}
    
    dob_date = datetime.strptime(data["dob"], "%Y-%m-%d")
    formatted_dob = dob_date.strftime("%Y%m%d")
    
    data_patient = {
        "kd_pasien": data["name"],
        "nik": data["nik"],
        "jenis_kelamin": data["gender"],
        "alamat_lengkap": data["address"],
        "id_propinsi_pasien": data["province"],
        "kd_kabupaten_pasien": data["district"],
        "tgl_lahir": formatted_dob,
    }

    return data_patient

def questionnaire_response(data):
    type_diagnosis = data.get('type_diagnosis', '')
    location_anatomy = data.get('location_anatomy', '')
    treatment_history = data.get('treatment_history', '')
    end_result_treatment = data.get("end_result_treatment", '')

    questionnaire_response = {
        "tipe_diagnosis": data_questionnaire_response_type_diagnosis_sitb([type_diagnosis])[0] if type_diagnosis else "",
        "klasifikasi_lokasi_anatomi": data_questionnaire_response_classification_location_anatomy_sitb([location_anatomy])[0] if location_anatomy else "",
        "klasifikasi_riwayat_pengobatan": data_questionnaire_response_classification_treatment_history_sitb([treatment_history])[0] if treatment_history else "",
        "hasil_akhir_pengobatan": data_questionnaire_response_end_result_of_treatment_tb_sitb([end_result_treatment])[0] if end_result_treatment else "",
    }

    return questionnaire_response

def condition(data):
    data_condition = []
    for result in data:
        icd_x_code_tb = result["icd_x_code_tb"]
        if icd_x_code_tb in data_icd_x_code():
            data_condition.append(
                {
                    "kode_icd_x": result["icd_x_code_tb"]
                }
            )

    return data_condition[0]

def episode_of_care(data):
    period_start = data.get("period_start", "")
    period_end = data.get("period_end", "")
    
    start_date_formated = datetime.strptime(period_start, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d")
    
    if period_end:
        end_date_formated = datetime.strptime(period_end, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d")
    else:
        end_date_formated = ""
    
    data_episode_of_care = {
        "tanggal_mulai_pengobatan": start_date_formated,
        "tanggal_hasil_akhir_pengobatan": end_date_formated
    }

    return data_episode_of_care

def medication(data):
    paduan_oat = []
    
    for result in data:
        kfa_code = result["kfa_code"]
        kfa_name = result["kfa_name"]
        if kfa_code in data_medication_kfa():
            paduan_oat.append(data_medication_kfa()[kfa_code])
        else:
            paduan_oat.append(kfa_name)
 
    # Convert the list to a comma-separated string
    paduan_oat_str = ', '.join(paduan_oat)
    return {"paduan_oat": paduan_oat_str}

def observation(data_input_observation, data_input_episode_of_care):
    data_observation = {
        "sebelum_pengobatan_hasil_mikroskopis": "-",
        "hasil_mikroskopis_bulan_2": "",
        "hasil_mikroskopis_bulan_3": "",
        "hasil_mikroskopis_bulan_5": "",
        "akhir_pengobatan_hasil_mikroskopis": "",
        "sebelum_pengobatan_hasil_tes_cepat": "-",
        "sebelum_pengobatan_hasil_biakan": "-",
        "foto_toraks": "",
    }
    error = []
    encountered_episode_numbers = set()

    if data_input_observation:
        for result in data_input_observation:
            type_observation = result['type_observation']
            value_observation = result['value']
            episode_number = result['episode_number']

            # microscopis
            if type_observation in list(data_type_observation_bta()):
                # validate episode_number jika ada yang sama
                if episode_number in encountered_episode_numbers:
                    error.append({"observation": "Duplicate entry for episode_number."})
                    encountered_episode_numbers.add(episode_number)
            
                # jika id_tb_03 == "" maka kunjungan pertama dan ambil episode_number == 1
                # jika bukan episode_number == 1 maka error
                if data_input_episode_of_care["id_tb_03"] == "":
                    if episode_number == "1":
                        data_observation["sebelum_pengobatan_hasil_mikroskopis"] = value_observation

                # jika id_tb_03 != "" maka kunjungan berikutnya dan tetap membawa episode_number == 1 dan seterusnya
                elif data_input_episode_of_care["id_tb_03"] != "":
                    if episode_number == "1":
                        data_observation["sebelum_pengobatan_hasil_mikroskopis"] = value_observation
                    if episode_number == "2":
                        data_observation["hasil_mikroskopis_bulan_2"] = value_observation
                    elif episode_number == "3":
                        data_observation["hasil_mikroskopis_bulan_3"] = value_observation

                    # jika episode_number == 4 maka error
                    elif episode_number == "4":
                        error.append({"observation": "invalid episode_number 4."})
                    elif episode_number == "5":
                        data_observation["hasil_mikroskopis_bulan_5"] = value_observation
                    elif "6" <= episode_number <= "9":
                        data_observation["akhir_pengobatan_hasil_mikroskopis"] = value_observation

            # tcm
            elif type_observation == 'tcm':
                if episode_number == "1":
                    data_observation["sebelum_pengobatan_hasil_tes_cepat"] = value_observation
                else:
                    error.append({"observation": "Invalid format for observation."})

            # culture-treatment
            elif type_observation == 'culture-treatment':
                if episode_number == "1":
                    data_observation["sebelum_pengobatan_hasil_biakan"] = value_observation
                else:
                    error.append({"observation": "Invalid format for observation."})

            # photo-thorax-ap, photo-thorax-pa
            elif type_observation in list(data_type_observation_thorax()):
                data_observation["foto_toraks"] = value_observation

            else:
                error.append({"observation": "Unknown observation type."})

        if error:
            return {"error": "error", "response_data": error}

    return data_observation

def faskes(user_id):
    error = []
    
    user = User.objects.filter(id=user_id).first()
    # validate sitb
    if user.code_fasyankes == None or user.sitb_rs_id == "" or user.sitb_rs_pass == "" or user.province == None or user.district == None:
        error.append({"detail": "invalid credentials."})
        
    if error:
        return {"error": "error", "response_data": error}
    
    data_faskes = {
        "id_propinsi_faskes": user.province.code,
        "kd_kabupaten_faskes": user.district.code,
        "kd_fasyankes": user.code_fasyankes
    }

    return data_faskes
    

def bundle_sitb(user_id, data_input, log_id):

    data_input_patient = data_input["patient"]
    data_input_questionnaire_response = data_input["questionnaire_response"]
    data_input_condition = data_input["condition"]
    data_input_medication = data_input["medication"]    
    data_input_observation = data_input.get("observation", {})
    data_input_episode_of_care = data_input["episode_of_care"]

    data_resource_patient = patient(data_input_patient)
    data_resource_condition = condition(data_input_condition)
    data_resource_questionnaire_response = questionnaire_response(data_input_questionnaire_response) # error
    data_resource_episode_of_care = episode_of_care(data_input_episode_of_care)
    data_observation = observation(data_input_observation, data_input_episode_of_care)
    data_medication = medication(data_input_medication)
    data_faskes = faskes(user_id)
    
    # handling succeess and error
    data_resources = [data_resource_patient, data_medication, data_observation, data_faskes]
    
    if all('error' not in data for data in data_resources):
        
        id_tb_03 = {
            "id_tb_03": data_input["id_tb_03"]
        }

        data_merge = {
            **id_tb_03,
            **data_resource_patient,
            **data_faskes,
            **data_resource_condition,
            **data_resource_questionnaire_response,
            **data_resource_episode_of_care,
            **data_observation,
            **data_medication,
        }
        
        return request_data_bundle(data_merge, user_id, log_id)

    else:
        user = User.objects.get(pk=user_id)
        
        try:    
            log_id = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            log_id = None
    
        error = transaction_error(data_resource_patient, data_observation, data_faskes)
        transaction_sitb = TransactionSitb()
        transaction_sitb.log = log_id
        transaction_sitb.status = TransactionStatus.ERROR
        transaction_sitb.error_messages = error
        transaction_sitb.created_by = user
        transaction_sitb.save()
        return {"status_process": "error", "response_data": error['response_data'], "user_id": user_id}
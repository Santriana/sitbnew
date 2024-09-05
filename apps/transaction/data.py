from django.conf import settings


def data_icd_x_code():
    data = {
        "A15": "Respiratory tuberculosis, bacteriologically and histologically confirmed",
        "A15.0": "Tuberculosis of lung, confirmed by sputum microscopy with or without culture",
        "A15.1": "Tuberculosis of lung, confirmed by culture only",
        "A15.2": "Tuberculosis of lung, confirmed histologically",
        "A15.3": "Tuberculosis of lung, confirmed by unspecified means",
        "A15.4": "Tuberculosis of intrathoracic lymph nodes, confirmed bacteriologically and histologically",
        "A15.5": "Tuberculosis of larynx, trachea and bronchus, confirmed bacteriologically and histologically",
        "A15.6": "Tuberculous pleurisy, confirmed bacteriologically and histologically",
        "A15.7": "Primary respiratory tuberculosis, confirmed bacteriologically and histologically",
        "A15.8": "Other respiratory tuberculosis, confirmed bacteriologically and histologically",
        "A15.9": "Respiratory tuberculosis unspecified, confirmed bacteriologically and histologically",

        "A16": "Respiratory tuberculosis, not confirmed bacteriologically or histologically",
        "A16.0": "Tuberculosis of lung, bacteriologically and histologically negative",
        "A16.1": "Tuberculosis of lung, bacteriological and histological examination not done",
        "A16.2": "Tuberculosis of lung, without mention of bacteriological or histological confirmation",
        "A16.3": "Tuberculosis of intrathoracic lymph nodes, without mention of bacteriological or histological confirmation",
        "A16.4": "Tuberculosis of larynx, trachea and bronchus, without mention of bacteriological or histological confirmation",
        "A16.5": "Tuberculous pleurisy, without mention of bacteriological or histological confirmation",
        "A16.7": "Primary respiratory tuberculosis without mention of bacteriological or histological confirmation",
        "A16.8": "Other respiratory tuberculosis, without mention of bacteriological or histological confirmation",
        "A16.9": "Respiratory tuberculosis unspecified, without mention of bacteriological or histological confirmation",

        "A17": "Tuberculosis of nervous system",
        "A17.0": "Tuberculous meningitis",
        "A17.1": "Meningeal tuberculoma",
        "A17.8": "Other tuberculosis of nervous system",
        "A17.9": "Tuberculosis of nervous system, unspecified",

        "A18": "Tuberculosis of other organs",
        "A18.0": "Tuberculosis of bones and joints",
        "A18.1": "Tuberculosis of genitourinary system",
        "A18.2": "Tuberculous peripheral lymphadenopathy",
        "A18.3": "Tuberculosis of intestines, peritoneum and mesenteric glands",
        "A18.4": "Tuberculosis of skin and subcutaneous tissue",
        "A18.5": "Tuberculosis of eye",
        "A18.6": "Tuberculosis of ear",
        "A18.7": "Tuberculosis of adrenal glands",
        "A18.8": "Tuberculosis of other specified organs",

        "A19": "Miliary tuberculosis",
        "A19.0": "Acute miliary tuberculosis of a single specified site",
        "A19.1": "Acute miliary tuberculosis of multiple sites",
        "A19.2": "Acute miliary tuberculosis, unspecified",
        "A19.8": "Other miliary tuberculosis",
        "A19.9": "Miliary tuberculosis, unspecified",

    }
    return data


def data_questionnaire_response_type_diagnosis():
    data = {
        "tb-bac": "Terkonfirmasi bakteriologis",
        "tb-clin": "Terdiagnosis klinis"
    }
    return data


def data_questionnaire_response_classification_location_anatomy():
    data = {
        "PTB": "TB Paru",
        "EPTB": "TB Ekstraparu"
    }
    return data


def data_questionnaire_response_classification_treatment_history():
    data = {
        "new": "Kasus Baru",
        "relapse": "Kasus Kambuh",
        "failure": "Kasus Pengobatan Setelah Gagal",
        "failure-cat1": "Kasus Pengobatan Setelah Gagal Kategori 1",
        "failure-cat2": "Kasus Pengobatan Setelah Gagal Kategori 2",
        "failure-2line": "Kasus Pengobatan Setelah Gagal lini 2",
        "loss-to-follow-up": "Kasus Setelah Loss To Follow Up",
        "other": "Kasus lain-lain",
        "unknown": "Kasus dengan riwayat pengobatan tidak diketahui"
    }
    return data


def data_questionnaire_response_end_result_of_treatment_tb():
    data = {
        "cured": "Sembuh",
        "cmpl": "Pengobatan Lengkap",
        "failed": "Pengobatan Gagal",
        "died": "Meninggal",
        "loss-to-follow-up": "Putus Obat",
        "not-eval": "Tidak dievaluasi"
    }
    return data


def data_questionnaire_response_items():
    data = {
        "type_diagnosis": {
            "linkId": "1",
            "text": "Tipe diagnosis tuberkulosis",
            "system": "https://terminology.kemkes.go.id/CodeSystem/tb-case-definition"
        },
        "classification_location_anatomy": {
            "linkId": "2",
            "text": "Klasifikasi tuberkulosis berdasarkan lokasi anatomis",
            "system": "https://terminology.kemkes.go.id/CodeSystem/tb-anatomical"
        },
        "classification_treatment_history": {
            "linkId": "3",
            "text": "Klasifikasi tuberkulosis berdasarkan riwayat pengobatan",
            "system": "https://terminology.kemkes.go.id/CodeSystem/prev-tb-treatment"
        },
        "end_result_of_treatment_tb": {
            "linkId": "4",
            "text": "Hasil akhir pengobatan tuberkulosis",
            "system": "https://terminology.kemkes.go.id/CodeSystem/tb-outcome-class"
        }
    }
    return data


def data_medication_kfa():
    data = {
        "92000689": "Isoniazid 300 mg Tablet",
        "92000457": "Pyrazinamide 500 mg Tablet",
        "92000288": "Streptomycin Sulfate 1000 mg Serbuk Injeksi",
        "92000298": "Ethambutol 400 mg Tablet Salut Selaput",
        "92000150": "Levofloxacin Hemihydrate 250 mg Tablet Salut Selaput",
        "92000746": "Moxifloxacin 400 mg Kaplet Salut Selaput",
        "92000290": "Bedaquiline Fumarate 100 mg Tablet",
        "92000716": "Obat Anti Tuberculosis / Rifampicin 150 mg / Isoniazid 75 mg / Pyrazinamide 400 mg / "
                    "Ethambutol 275 mg Kaplet Salut Selaput",
        "92000715": "Obat Anti Tuberculosis / Rifampicin 150 mg / Isoniazid 150 mg Tablet Salut Selaput",
        "92000760": "Rifampicin 450 mg Kaplet Salut Selaput",
        "92000710": "Obat Anti Tuberculosis / Rifampicin 75 mg / Isoniazid 50 mg / "
                    "Pyrazinamide 150 mg Tablet Dispersibel",
        "92000717": "Obat Anti Tuberculosis / Rifampicin 75 mg / Isoniazid 50 mg Tablet Dispersibel",
        "92000423": "Amikacin 250 mg/ml Injeksi",
        "92000428": "Isoniazid 100 mg Tablet",
        "92000801": "Rifapentine 150 mg Tablet Salut Selaput",
        "92000761": "Rifampicin 600 mg Kaplet Salut Selaput",
        "93001077": "Pyrazinamide 500 mg Tablet (DEXA MEDICA)",
        "93001078": "Pyrazinamide 500 mg Tablet (SANBE FARMA)",
        "93001079": "Pyrazinamide 500 mg Tablet (KIMIA FARMA)",
        "93000400": "Streptomycin Sulfate 1000 mg Serbuk Injeksi (KIMIA FARMA)",
        "93000147": "Levofloxacin Hemihydrate 250 mg Tablet Salut Selaput (KIMIA FARMA)",
        "93000402": "Bedaquiline Fumarate 100 mg Tablet (SIRTURO)",
        "93001019": "Obat Anti Tuberculosis / Rifampicin 150 mg / Isoniazid 75 mg / Pyrazinamide 400 mg / "
                    "Ethambutol 275 mg Kaplet Salut Selaput (KIMIA FARMA)",
        "93001021": "Obat Anti Tuberculosis / Rifampicin 150 mg / Isoniazid 75 mg / Pyrazinamide 400 mg / "
                    "Ethambutol 275 mg Kaplet Salut Selaput (PHAPROS)",
        "93001017": "Obat Anti Tuberculosis / Rifampicin 150 mg / Isoniazid 150 mg Tablet Salut Selaput (KIMIA FARMA)",
        "93001025": "Obat Anti Tuberculosis / Rifampicin 75 mg / Isoniazid 50 mg / "
                    "Pyrazinamide 150 mg Tablet Dispersibel (INDOFARMA)",
        "93001022": "Obat Anti Tuberculosis / Rifampicin 75 mg / Isoniazid 50 mg Tablet Dispersibel (INDOFARMA)",
        "93000761": "Amikacin 250 mg/ml Injeksi (DEXA MEDICA)",
        "93000832": "soniazid 100 mg Tablet (KIMIA FARMA Tbk.)",
        "93001162": "Rifapentine 150 mg Tablet Salut Selaput (PRIFTIN)",
        "91000328": "Isoniazid",
        "91000329": "Pyrazinamide",
        "91000293": "Streptomycin",
        "91000288": "Ethambutol",
        "91000136": "Levofloxacin",
        "91000585": "Moxifloxacin",
        "91000287": "Bedaquiline",
        "91000330": "Rifampin",
        "91000404": "Amikacin",
        "91000505": "Rifapentine"
    }
    return data


def data_medication_form():
    data = {
        "BS001": "Aerosol Foam",
        "BS002": "Aerosol Metered Dose",
        "BS003": "Aerosol Spray",
        "BS004": "Oral Spray",
        "BS005": "Buscal Spray",
        "BS006": "Transdermal Spray",
        "BS007": "Topical Spray",
        "BS008": "Serbuk Spray",
        "BS009": "Eliksir",
        "BS010": "Emulsi",

        "BS011": "Enema",
        "BS012": "Gas",
        "BS013": "Gel",
        "BS014": "Gel Mata",
        "BS015": "Granul Effervescent",
        "BS016": "Granula",
        "BS017": "Intra Uterine Device (IUD)",
        "BS018": "Implant",
        "BS019": "Kapsul",
        "BS020": "Kapsul Lunak",

        "BS021": "Kapsul Pelepasan Lambat",
        "BS022": "Kaplet",
        "BS023": "Kaplet Salut Selaput",
        "BS024": "Kaplet Salut Enterik",
        "BS025": "Kaplet Salut Gula",
        "BS026": "Kaplet Pelepasan Lambat",
        "BS027": "Kaplet Pelepasan Cepat",
        "BS028": "Kaplet Kunyah",
        "BS029": "Kaplet Kunyah Salut Selaput",
        "BS030": "Krim",

        "BS031": "Krim Lemak",
        "BS032": "Larutan",
        "BS033": "Larutan Inhalasi",
        "BS034": "Larutan Injeks",
        "BS035": "Infus",
        "BS036": "Obat Kumur",
        "BS037": "Ovula",
        "BS038": "Pasta",
        "BS039": "Pil",
        "BS040": "Patch",

        "BS041": "Pessary",
        "BS042": "Salep",
        "BS043": "Salep Mata",
        "BS044": "Sampo",
        "BS045": "Semprot Hidung",
        "BS046": "Serbuk Aerosol",
        "BS047": "Serbuk Oral",
        "BS048": "Serbuk Inhaler",
        "BS049": "Serbuk Injeksi",
        "BS050": "Serbuk Injeksi Liofilisasi",

        "BS051": "Serbuk Infus",
        "BS052": "Serbuk Obat Luar / Serbuk Tabur",
        "BS053": "Serbuk Steril",
        "BS054": "Serbuk Effervescent",
        "BS055": "Sirup",
        "BS056": "Sirup Kering",
        "BS057": "Sirup Kering Pelepasan Lambat",
        "BS058": "Subdermal Implants",
        "BS059": "Supositoria",
        "BS060": "Suspensi",

        "BS061": "Suspensi Injeksi",
        "BS062": "Suspensi / Cairan Obat Luar",
        "BS063": "Cairan Steril",
        "BS064": "Cairan Mata",
        "BS065": "Cairan Diagnostik",
        "BS066": "Tablet Tablet",
        "BS067": "Tablet Effervescent",
        "BS068": "Tablet Hisap",
        "BS069": "Tablet Kunyah",
        "BS070": "Tablet Pelepasan Cepat",

        "BS071": "Tablet Pelepasan Lambat",
        "BS072": "Tablet Disintegrasi Oral",
        "BS073": "Tablet Dispersibel",
        "BS074": "Tablet Cepat Larut",
        "BS075": "Tablet Salut Gula",
        "BS076": "Tablet Salut Enterik",
        "BS077": "Tablet Salut Selaput",
        "BS078": "Tablet Sublingual",
        "BS079": "Tablet Sublingual Pelepasan Lambat",
        "BS080": "Tablet Vaginal",

        "BS081": "Tablet Lapis",
        "BS082": "Tablet Lapis Lepas Lambat",
        "BS083": "Chewing Gum",
        "BS084": "Tetes Mata",
        "BS085": "Tetes Hidung",
        "BS086": "Tetes Telinga",
        "BS087": "Tetes Oral (Oral Drops)",
        "BS088": "Tetes Mata Dan Telinga",
        "BS089": "Transdermal",
        "BS090": "Transdermal Urethral",

        "BS091": "Tulle/Plester Obat",
        "BS092": "Vaginal Cream",
        "BS093": "Vaginal Gel",
        "BS094": "Vaginal Douche",
        "BS095": "Vaginal Ring",
        "BS096": "Vaginal Tissue",
        "BS097": "Suspensi Inhalasi",
    }

    return data


def data_observation_interpretation():
    data = {
        "_GeneticObservationInterpretation": "GeneticObservationInterpretation",
        "CAR": "Carrier",
        "_ObservationInterpretationChange": "ObservationInterpretationChange",
        "B": "Better",
        "D": "Significant change down",
        "U": "Significant change up",
        "W": "Worse",
        "_ObservationInterpretationExceptions": "ObservationInterpretationExceptions",
        "<": "Off scale low",
        ">": "Off scale high",
        "IE": "Insufficient evidence",
        "_ObservationInterpretationNormality": "ObservationInterpretationNormality",
        "A": "Abnormal",
        "AA": "Critical abnormal",
        "HH": "Critical high",
        "LL": "Critical low",
        "H": "High",
        "HU": "Significantly high",
        "L": "Low",
        "LU": "Significantly low",
        "N": "Normal",
        "_ObservationInterpretationSusceptibility": "ObservationInterpretationSusceptibility",
        "I": "Intermediate",
        "NCL": "No CLSI defined breakpoint",
        "NS": "Non-susceptible",
        "R": "Resistant",
        "SYN-R": "Synergy - resistant",
        "S": "Susceptible",
        "SDD": "Susceptible-dose dependent",
        "SYN-S": "Synergy - susceptible",
        "EX": "outside threshold",
        "HX": "above high threshold",
        "LX": "below low threshold",
        "ObservationInterpretationDetection": "ObservationInterpretationDetection",
        "IND": "Indeterminate",
        "E": "Equivocal",
        "NEG": "Negative",
        "ND": settings.NOT_DETECT,
        "POS": "Positive",
        "DET": "Detected",
        "ObservationInterpretationExpectation": "ObservationInterpretationExpectation",
        "EXP": "Expected",
        "UNE": "Unexpected",
        "ReactivityObservationInterpretation": "ReactivityObservationInterpretation",
        "NR": "Non-reactive",
        "RR": "Reactive",
        "WR": "Weakly reactive"
    }
    return data


def data_episode_of_care_type():
    data = {
        "TB-SO": "Tuberkulosis Sensitif Obat",
        "TB-RO": "Tuberkulosis Resisten Obat"
    }
    return data


def data_condition_diagnosis_use():
    data = {
        "AD": "Admission diagnosis",
        "DD": "Discharge diagnosis",
        "CC": "Chief complaint",
        "CM": "Comorbidity diagnosis",
        "pre-op": "pre-op diagnosis",
        "post-op": "post-op diagnosis",
        "billing": "Billing"
    }

    return data


def data_encounter_status():
    data = {
        "planned": "Sudah direncanakan",
        "arrived": "Sudah datang",
        "triaged": "Triase",
        "in-progress": "Sedang berlangsung",
        "onleave": "Sedang pergi",
        "finished": "Sudah selesai",
        "cancelled": "Dibatalkan"
    }
    return data


def data_encounter_class():
    data = {
        "AMB": "Ambulatory",
        "VR": "Virtual",
        "IMP": "Inpatient Encounter",
        "HH": "Home Health",
        "EMER": "Emergency"
    }
    return data


def data_condition_clinical_status():
    data = {
        "active": "Active",
        "recurrence": "Recurrence",
        "relapse": "Relapse",
        "inactive": "Inactive",
        "remission": "Remission",
        "resolved": "Resolved"
    }
    return data


def data_condition_category():
    data = {
        "problem-list-item": "Problem List Item",
        "encounter-diagnosis": "Encounter Diagnosis",
    }
    return data


def data_questionnaire_response_status():
    data = {
        "in-progress", "completed",
        "amended", "entered-in-error",
        "stopped"
    }
    return data


def data_observation_status():
    data = {
        "registered", "preliminary", "final",
        "amended", "corrected", "cancelled", "entered-in-error",
        "unknown"
    }
    return data


def data_observation_category():
    data = {
        "social-history": "Social History",
        "vital-signs": "Vital Signs",
        "imaging": "Imaging",
        "laboratory": "Laboratory",
        "procedure": "Procedure",
        "survey": "Survey",
        "exam": "Exam",
        "therapy": "Therapy",
        "activity": "Activity"
    }
    return data


def data_medication_extension_medication_on_type():
    data = {
        "NC": "Non-compound",
        "SD": "Gives of such doses",
        "EP": "Divide into equal parts",
    }
    return data


def data_medication_request_intent():
    data = {
        "proposal": "Proposal",
        "plan": "Plan",
        "order": "Order",
        "original-order": "Original Order",
        "reflex-order": "Reflex Order",
        "filler-order": "Filler Order",
        "instance-order": "Instance Order",
        "unknown": "Tidak diketahui"
    }
    return data


def data_medication_request_category():
    data = {
        "inpatient": "Inpatient",
        "outpatient": "Outpatient",
        "community": "Community",
        "discharge": "Discharge"
    }
    return data


def data_observation_bta_culture_thorax_value():
    data = {
        "neg": {
            "system": settings.LOINC_URL,
            "code": "LA6577-6",
            "display": "Negative"
        },
        "1+": {
            "system": settings.SNOMED_URL,
            "code": "260347006",
            "display": "+"
        },
        "2+": {
            "system": settings.SNOMED_URL,
            "code": "260348001",
            "display": "++"
        },
        "3+": {
            "system": settings.SNOMED_URL,
            "code": "260349009",
            "display": "+++"
        },
        "4+": {
            "system": settings.SNOMED_URL,
            "code": "260350009",
            "display": "++++"
        },
        "ntm": {
            "system": settings.SNOMED_URL,
            "code": "110379001",
            "display": "Mycobacterium, non-tuberculos is (organism)"
        },
        "kontaminasi": {
            "system": settings.LOINC_URL,
            "code": "LA18428-5",
            "display": "Culture contaminated"
        },
        settings.NOT_ACTION: {
            "system": settings.TERMINOLOGY_NOT_ACTION,
            "code": "not-performed",
            "display": settings.NOT_PERFORM
        },
        "1": {
            "value": 1,
            "unit": "Bacteria", 
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "2": {
            "value": 2,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "3": {
            "value": 3,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "4": {
            "value": 4,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "5": {
            "value": 5,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "6": {
            "value": 6,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "7": {
            "value": 7,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "8": {
            "value": 8,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "9": {
            "value": 9,
            "unit": "Bacteria",
            "system": "http://unitsofmeasure.org",
            "code":"/min",
        },
        "negative": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "NEG",
            "display": "Negative"
        },
        "positive": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "POS",
            "display": "Positive"
        },
        "not-performed": {
            "system": settings.TERMINOLOGY_NOT_ACTION,
            "code": "not-performed",
            "display": settings.NOT_PERFORM
        },
    }

    return data


def data_observation_bta_culture_thorax_code():
    data = {
        "bta": {
            "system": settings.LOINC_URL,
            "code": "11477-7",
            "display": "Microscopic observation [Identifier] in Sputum by Acid fast stain"
        },
        "biakan": {
            "system": settings.LOINC_URL,
            "code": "539-7",
            "display": "Mycobacterium sp identified in Sputum by Organism specific culture"
        },
        "thorax-pa": {
            "system": settings.LOINC_URL,
            "code": "24648-8",
            "display": "XR Chest PA upright"
        },
        "thorax-ap": {
            "system": settings.LOINC_URL,
            "code": "36572-6",
            "display": "XR Chest AP"
        }
    }
    return data


def data_diagnostic_report_category():
    data = {
        "bta": {
            "system": settings.TERMINOLOGY_DIAGNOSTIC_CODE_SYSTEM,
            "code": "MB",
            "display": "Microbiology"
        },
        "biakan": {
            "system": settings.TERMINOLOGY_DIAGNOSTIC_CODE_SYSTEM,
            "code": "MB",
            "display": "Microbiology"
        },
        "tcm": {
            "system": settings.TERMINOLOGY_DIAGNOSTIC_CODE_SYSTEM,
            "code": "MB",
            "display": "Microbiology"
        },
        "thorax": {
            "system": settings.TERMINOLOGY_DIAGNOSTIC_CODE_SYSTEM,
            "code": "RX",
            "display": "Radiograph"
        }
    }

    return data


def data_diagnostic_report_code():
    data = {
        "bta": {
            "system": settings.LOINC_URL,
            "code": "11477-7",
            "display": "Microscopic observation [Identifier] in Sputum by Acid fast stain"
        },
        "biakan": {
            "system": settings.LOINC_URL,
            "code": "539-7",
            "display": "Mycobacterium sp identified in Sputum by Organism specific culture"
        },
        "tcm": {
            "system": settings.LOINC_URL,
            "code": "89371-9",
            "display": "MTB complex DNA and rpoB RIF resistance mutation panel [Presence]"
        },
        "thorax-pa": {
            "system": settings.LOINC_URL,
            "code": "24648-8",
            "display": "XR Chest PA upright"
        },
        "thorax-ap": {
            "system": settings.LOINC_URL,
            "code": "36572-6",
            "display": "XR Chest AP upright"
        },
    }
    return data


def data_diagnostic_report_status():
    data = {
        "registered", "partial", "preliminary",
        "final", "amended", "corrected", "appended",
        "cancelled", "entered-in-error", "unknown"
    }
    return data


def data_observation_tcm_dna():
    data = {
        "not-detected": {
            "system": settings.LOINC_URL,
            "code": "LA11882-0",
            "display": settings.NOT_DETECT
        },
        "detected": {
            "system": settings.LOINC_URL,
            "code": "LA11883-8",
            "display": "Detected"
        },
        "invalid": {
            "system": settings.LOINC_URL,
            "code": "LA15841-2",
            "display": "Invalid"
        },
        "error": {
            "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "error",
            "display": "Error"
        },
        "no result": {
            "system": settings.LOINC_URL,
            "code": "LA22773-8",
            "display": "No result obtained"
        },
        settings.NOT_ACTION: {
            "system": settings.TERMINOLOGY_NOT_ACTION,
            "code": "not-performed",
            "display": settings.NOT_PERFORM
        },
        "neg": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "NEG",
            "display": "Negative"
        }
    }
    return data


def data_observation_tcm_sputum():
    data = {
        "not-detected": {
            "system": settings.LOINC_URL,
            "code": "LA11882-0",
            "display": settings.NOT_DETECT
        },
        "detected": {
            "system": settings.LOINC_URL,
            "code": "LA11883-8",
            "display": "Detected"
        },
        "indeterminate": {
            "system": settings.LOINC_URL,
            "code": "LA11884-6",
            "display": "Indeterminate"
        },
        "rifampicin sensitive": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "S",
            "display": "Susceptible"
        },
        "rifampicin resistant": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "R",
            "display": "Resistant"
        },
        "rifampicin indeterminate": {
            "system": settings.TERMINOLOGY_OBSERVATION_INTERPRETATION,
            "code": "IND",
            "display": "Indeterminate"
        }
    }
    return data


def data_episode_of_care_status():
    data = {
        "planned", "waitlist", "active", "onhold", "finished", "cancelled", "entered-in-error"
    }
    return data


def data_type_observation():
    data = {
        "microscopic", "tcm", "culture-treatment",
        "photo-thorax-ap", "photo-thorax-pa"
    }

    return data


def data_type_observation_bta():
    data = {
        "microscopic"
    }
    return data


def data_type_observation_bta_culture_thorax():
    data = {
        "microscopic", "culture-treatment", "photo-thorax-ap", "photo-thorax-pa"
    }
    return data


def data_type_observation_thorax():
    data = {
        "photo-thorax-ap", "photo-thorax-pa"
    }
    return data

# MAPPING DATA SITB
def data_questionnaire_response_type_diagnosis_sitb(value):
    data_mapping = {
        "tb-bac": "1",
        "tb-clin": "2"
    }

    output_array = [data_mapping.get(key, key) for key in value]
    return output_array

def data_questionnaire_response_classification_location_anatomy_sitb(value):
    data_mapping = {
        "PTB": "1",
        "EPTB": "2"
    }

    output_array = [data_mapping.get(key, key) for key in value]
    return output_array

def data_questionnaire_response_classification_treatment_history_sitb(value):
    data_mapping = {
        "new": "1",
        "relapse": "2",
        "failure-cat1": "3",
        "failure-cat2": "4",
        "failure": "5",
        "failure-2line": "6",
        "loss-to-follow-up": "7",
        "unknown": "8",
        "other": "9",
    }

    output_array = [data_mapping.get(key, key) for key in value]
    return output_array

def data_questionnaire_response_end_result_of_treatment_tb_sitb(value):
    data_mapping = {
        "cured": "Sembuh",
        "cmpl": "Pengobatan lengkap",
        "failed": "Gagal",
        "died": "Meninggal",
        "loss-to-follow-up": "Putus berobat",
        "not-eval": "Tidak dievaluasi/pindah"
    }
    output_array = [data_mapping.get(key, key) for key in value]
    return output_array

def is_valid(str):
    import re
    try:
        return bool(re.match(r'[a-zA-Z\d*+-/]*$', str))
    except TypeError:
        return False


def is_valid_date(day):
    from datetime import datetime
    now = datetime.now().strftime(settings.DATETIME_FORMAT)  # current date and time
    day_input = day.strftime(settings.DATETIME_FORMAT)
    if day_input > now:
        return True
    return False


def is_valid_date_end(start, progress, end):
    from datetime import datetime
    start_input = start.strftime(settings.DATETIME_FORMAT)
    progress_input = progress.strftime(settings.DATETIME_FORMAT)
    end_input = end.strftime(settings.DATETIME_FORMAT)
    if start_input > end_input or progress_input > end_input:
        return True
    return False


def data_type_observation_bta_valid(type_observation, value):
    if type_observation in list(data_type_observation_bta()):
        if value not in ["neg", "1", "2", "3", "4", "5", "6", "7", "8", "9", "1+", "2+", "3+", settings.NOT_ACTION]:
            return False
    return True


def data_type_observation_tcm_valid(type_observation, value):
    if type_observation == "tcm":
        if value not in ["neg", "rif-sen", "rif-res", "rif-indet", "invalid", "error", "no result", settings.NOT_ACTION]:
            return False
    return True


def data_type_observation_tcm_rifam_valid(type_observation, value):
    if type_observation == "tcm":
        if value in ["rif-sen", "rif-res", "rif-indet"]:
            return True
    return False


def data_type_observation_culture_treatment_valid(type_observation, value):
    if type_observation == "culture-treatment":
        if value not in ["neg", "1", "2", "3", "4", "6", "6", "7", "8", "9", "1+", "2+", "3+",
                         "4+", "ntm", "kontaminasi", settings.NOT_ACTION]:
            return False
    return True


def data_type_observation_thorax_valid(type_observation, value):
    if type_observation in list(data_type_observation_thorax()):
        if value not in ["negative", "positive", "not-performed"]:
            return False
    return True

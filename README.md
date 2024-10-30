## Usaid Tb Middleware Requirement
1. Docker

## Installation
1. Run docker
2. Run execute command `docker-compose up -d`
3. Run to load fixtures Province and District
`docker exec -it usaid-tb-backend-site python manage.py loaddata fixtures/District.json fixtures/Province.json`

## Set up new user with organization id and location id
1. Access users page `{domain}/admin/users/user/`
2. Add user
3. Enter email address, client id, client secret, password, and password confirmation
4. Save

## Get Token Auth
1. Access api token <br/>
    Url : `{domain}/api/users/token` <br/>
    Method : `POST` <br/>
    Parameter : 
    ```json
    {
        "email":"",
        "password":""
    }
    ```
    Send request use `json`

## Get Refresh Token
1. Access refresh token <br/>
    Url : `{domain}/api/users/token/refresh` <br/>
    Method : `POST` <br/>
    Parameter : 
    ```json
    {
        "refresh": ""
    }
    ```
    Send request use `json`

## Post transaction data
1. Access transaction data <br/>
    Url : `{domain}/api/transaction/data` <br/>
    Method : `POST` <br/>
    Parameter :
    ```json
    {
       "organization_id":"",
       "location_id":"",
       "practitioner_nik":"",
       "patient_nik":"",
       "encounter":{
          "local_id":"",
          "classification":"",
          "period_start":"",
          "period_in_progress":"",
          "period_end":""
       },
       "questionnaire_response":{
          "type_diagnosis":"",
          "location_anatomy":"",
          "treatment_history":"",
          "end_result_treatment":""
       },
       "condition":[
          {
             "icd_x_code_tb":"",
             "clinical_status_tb":"",
             "others":[
                {
                   "icd_x_code":"",
                   "icd_x_code_name":"",
                   "clinical_status":""
                },
                "......",
                "......",
                "......"
             ]
          }
       ],
       "medication":[
          {
             "kfa_code":"",
             "kfa_name":"",
             "form_code":""
          },
          "......",
          "......",
          "......"
       ],
       "observation":[
          {
             "local_id":"",
             "type_observation":"",
             "issued":"",
             "value":""
          },
          "......",
          "......",
          "......"
       ],
       "episode_of_care":{
          "ihs_id":"",
          "status":"",
          "type_code":"",
          "period_start":""
       }
    }
    ```
    Send request use `json`

2. For data entry, please check the brd documentation

## Post transaction data FHIR
1. Access transaction data fhir <br/>
    Url : `{domain}/api/transaction/data/fhir` <br/>
    Method : `POST` <br/>
    Parameter : 
    ```json
    {
      "data": "{FHIR Format data}"
    }
    ```
    Send request use `json`
2. For data entry, please check the brd documentation


## Get Transaction Data
1. Access transaction data detail <br/>
    Url : `{domain}/api/transaction/data/{id}/detail` <br/>
    Method : `GET` <br/>

## Example Collection Postman
- `https://www.getpostman.com/collections/8da48333e0cd169ee91e`

## Adminer Page
Access url : `http://localhost:8080/`

## Flower Page
Access url : `http://localhost:8888/`

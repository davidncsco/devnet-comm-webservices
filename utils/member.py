import requests, os
from db.model import Member

CLIENT_ID = "devnet-community-auth"
CLIENT_SECRET = "Cisc0Psdt123!"
# To obtain service token for DevNet profile inquiry, send this request
# POST /v1/auth/services/token
# Authorization: Basic {base64 encoded value of service_id:service_secret}
 
# {
#   "grant_type":"client_credential",
#   "resource":"target_service_id"
# }
SERVICE_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNvdXJjZSI6ImZvdW5kYXRpb24tdXBtIiwicGVybXMiOlt7InNlcnZpY2VfYXVkIjoiZm91bmRhdGlvbi11cG0iLCJzZXJ2aWNlX3N1YiI6ImRldm5ldC1jb21tdW5pdHktYXV0aCJ9XSwiYXVkIjoiZm91bmRhdGlvbi11cG0iLCJleHAiOjE3MTY0ODIwNTcsImp0aSI6ImVhZTIzMmVhLTE5MTktMTFlZi1iNGQ5LWVhMTE4NDgyODY4MCIsImlhdCI6MTcxNjQ3ODQ1NywiaXNzIjoiaW50ZXJuYWwiLCJzdWIiOiJkZXZuZXQtY29tbXVuaXR5LWF1dGgifQ.tDYQnXnxXqgDvnVojaiOh6zFWmt82mI6Lo_VJwVychlllhBVMWE3j5xPdUnaX4khohuouGnfb8ZYqRJbE0Sls467x0Lewnz2hIFKXUYPsohEi1xWFpVr79345mGBnXfVe0AsGaaOBcf_sbKhNPPNEt5tDbtAAd6noKDr2jOwAAc"


def process_new_registration(payload: dict):
    user = {}
    #print(f'payload={payload}')
    email =  payload['primaryEmail']
    if email:
        print(f"process new registration for user {email}")
        if( len(payload['allEmails']) > 1 ):
            allEmails = ','.join(payload['allEmails'])
            print(f"all emails = {allEmails}")
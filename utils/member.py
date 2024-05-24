import requests, base64, os
from requests.auth import HTTPBasicAuth
from db.model import Member

client_id = os.getenv("DEVNET_SERVICE_CLIENT_ID")
client_secret = os.getenv("DEVNET_SERVICE_CLIENT_SECRET")

def get_devnet_service_token() -> str:
    """
    Get service token from auth
    """
    
    url = "https://auth-devnet.cisco.com/v1/auth/services/token"
    body = {
        "grant_type":"client_credential",
        "resource":"foundation-upm"
    }
    response = requests.post(url, auth=(client_id,client_secret),json=body)
    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        if 'token' in data:
            #print(f'generated token: {data['token']}')
            return data['token']
        else:
            return None
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")
        return None

MAX_RETRIES = 2
devnet_service_token = None

def user_is_registered_on_devnet(email: str) -> str:
    """
    Check if user profile is on DevNet, return user id or None
    """
    global devnet_service_token
    
    url = f"https://devnet.cisco.com/v1/upm/profiles?email={email}"
    retries = 0
    if devnet_service_token is None:
        devnet_service_token = get_devnet_service_token()
        
    # Service token is short lived so need to get it again once it became invalid
    while retries < MAX_RETRIES:
        headers = {
            "Authorization": f"Bearer {devnet_service_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if email in data:
                provider_ids = data.get(email)
                if provider_ids:
                    first_key = next(iter(provider_ids.keys()))
                    return provider_ids[first_key]
                else:
                    return None
        elif response.status_code == 401:   # token is invalid, retry
            print("Token no longer valid, retry with new token")
            retries += 1
            devnet_service_token = get_devnet_service_token()
            continue
        else:
            print(f"Error fetching user profile from DevNet: {response.status_code} - {response.text}")
            return None
        
    return None

def process_new_registration(payload: dict):
    """
    Process new CR user who joins the space/source. This results in a Webhook trigger sent to our server
    """
    #print(f'payload={payload}')
    if 'primaryEmail' in payload:
        email =  payload['primaryEmail']
        print(f"process new registration for user {email}")
        if ('allEmails' in payload) and (len(payload['allEmails']) > 1):
            allEmails = ','.join(payload['allEmails'])
            print(f"all emails = {allEmails}")
        id = user_is_registered_on_devnet(email)
        if id:
            print(f"User has profile on DevNet with id={id}")
        else:
            print(f"User has NO profile on DevNet")


        
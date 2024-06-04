import requests, os, re
from utils.webex import send_message_to_room
from db.crud import DataAccess
from typing import List

client_id = os.getenv("DEVNET_SERVICE_CLIENT_ID")
client_secret = os.getenv("DEVNET_SERVICE_CLIENT_SECRET")
# To add devnet account tag to CR member
common_room_bearer_token = os.getenv("COMMON_ROOM_BEARER_TOKEN")
webex_room_trigger = os.getenv("WEBEX_ROOM_TRIGGER", "biggs_darklighter")
devnet_account_tag = os.getenv("DEVNET_ACCOUNT_TAG", "DevNet account")
devnet_service_token = None

class Member:
    def __init__(self, email: str, provider_id: str, devnet_profile: dict, cr_profile: dict):
        self.email = email
        self.provider_id = provider_id
        self.devnet_profile = devnet_profile
        self.cr_profile = cr_profile
        
    def __str__(self):
        return f"Member: email={self.email}, provider_id={self.provider_id}, DEVNET={self.devnet_profile}, COMMON ROOM={self.cr_profile}"
    
    def __repr__(self):
        return f"Member: email={self.email}, provider_id={self.provider_id}, DEVNET={self.devnet_profile}, COMMON ROOM={self.cr_profile}"
    
    def to_dict(self):
        return {
            "email": self.email,
            "provider_id": self.provider_id,
            "devnet_profile": self.devnet_profile,
            "cr_profile": self.cr_profile
        }
        
    @staticmethod
    def get_devnet_profile_by_email(email: str) -> str:
        """
        Check if user profile is on DevNet, return provider id or None
        """
        
        url = f"https://devnet.cisco.com/v1/upm/profiles?email={email}"
        data = devnet_upm_request(url)
        if email in data:
            provider_ids = data.get(email)
            if provider_ids:
                first_key = next(iter(provider_ids.keys()))
                return provider_ids[first_key]
            else:
                return None
                    
        return None
    
    @staticmethod
    def get_devnet_profile_by_id(id: str) -> dict:
        """
        Check if user profile is on DevNet, return user profile or None
        """
        
        url = f"https://devnet.cisco.com/v1/upm/profiles?id={id}"
        data = devnet_upm_request(url)
        if len(data) > 0:
            for item in data:
                if item['id'] == id:
                    return item
                    
        return None
    
    @staticmethod
    def get_cr_profile_by_email(email: str) -> list:
        """
        Get Community Member By E-Mail
        """
        
        url = f"https://api.commonroom.io/community/v1/members?email={email}"
        headers = {
            "Authorization": f"Bearer {common_room_bearer_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting cr member profile: {response.status_code} - {response.text}")            
        return None
    
    @staticmethod
    def from_dict(data: dict):
        return Member(data['email'], data['provider_id'], data['devnet_profile'], data['cr_profile'])
    
    @staticmethod
    def get_devnet_service_token() -> str:
        """
        Get new service token from auth
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
            return data.get('token', None)
        else:
            print(f"get_devnet_service_token: error sending message: {response.status_code} - {response.text}")
            return None
        
    @staticmethod
    def add_member_tag(email,tag_name):
        """
        Adds "DevNet account" tag to a CR Community Member
        """
        url = "https://api.commonroom.io/community/v1/members/tags"
        headers = {
            "Authorization": f"Bearer {common_room_bearer_token}",
            "Content-Type": "application/json"
        }
        body = {
            "socialType": "email",
            "value": f"{email}",
            "tags": f"{tag_name}"
        }
        response = requests.post(url, headers=headers,json=body)
        # Check for successful response
        if response.status_code == 200:
            print(f"{devnet_account_tag} tag added to member with email={email}")
        else:
            print(f"Error adding member tag: {response.status_code} - {response.text}")


def devnet_upm_request(url) -> dict:
    """
    Make a request to DevNet Foundation Services API: UPM, return JSON data or None
    """
    global devnet_service_token
    MAX_RETRIES = 2
    
    if devnet_service_token is None:
        print("Getting devnet service token on the first run")
        devnet_service_token = Member.get_devnet_service_token()
        if not devnet_service_token:
            return None
    
    retries = 0        
    # Service token is short lived so need to get it again once it became invalid
    while retries < MAX_RETRIES:
        headers = {
            "Authorization": f"Bearer {devnet_service_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:   # token is invalid, retry
            print("Token no longer valid, retry with new token")
            retries += 1
            devnet_service_token = Member.get_devnet_service_token()
            continue
        else:
            print(f"devnet_upm_request: Error fetching user profile from DevNet: {response.status_code} - {response.text}")
            return None
        
    return None


    
# Data dependency injection for DataAccess    
data_access = None

async def log_message_to_room(user: Member, activityType: str):
    global data_access
    
    print(f"log_message_to_room: webhook name = {webex_room_trigger}")
    if data_access is None:
        data_access = DataAccess()
    webhook = await data_access.get_webhook_by_name(webex_room_trigger)
    if webhook:
        template = await data_access.get_template_by_id(webhook.template)
        if template:
            send_message_to_room(webhook.roomId, {'email': user.email, 'provider_id': user.provider_id, 'activityType': activityType}, template)

post_fixes = ["ciscosso", "facebook", "gplus", "commonidentity", "webex", "netacad"]

def extract_email_prefix(accounts):
    """
    Extract the email prefix from the list of accounts. This is how DevNet UPM API returns in the user profile (?)
    """
    common_prefix = accounts[0]
    if len(accounts) > 1:
        for account in accounts[1:]:     # Iterate over the remaining accounts
            # Find the length of the common prefix
            prefix_length = 0
            while prefix_length < len(common_prefix) and prefix_length < len(account) and common_prefix[prefix_length] == account[prefix_length]:
                prefix_length += 1

            # Update the common prefix
            common_prefix = common_prefix[:prefix_length]
        return common_prefix
    else: # Use regex to extract the real email address
        for postfix in post_fixes:
            match_str = f"(.+?){postfix}"
            match = re.search(match_str, common_prefix)
            if match:
                return match.group(1)
        return None


async def process_new_registration(source: str,payload: dict):
    """
    This workflow event results in a Webhook trigger sent to our server when there are a new registration on DevNet or 
    new user from Common Room with payload type = 'member'
    """
    #print(f'payload={payload}')
    user = Member('','',{},{})
    
    if source == 'cr' and 'primaryEmail' in payload:
        user.email =  payload['primaryEmail']
        print(f"process new COMMON ROOM registration for user {user.email}")
        user.provider_id = Member.get_devnet_profile_by_email(user.email)
        if user.provider_id:
            user.devnet_profile = Member.get_devnet_profile_by_id(user.provider_id)
            user.cr_profile = [payload]
            Member.add_member_tag(user.email,devnet_account_tag)
            await log_message_to_room(user, activityType='Common Room member with DevNet account')
            print(user)
    elif source == 'devnet' and payload['id']:
        user.provider_id = payload['id']
        print(f"process new DEVNET registration for user id {user.provider_id}")
        user.devnet_profile = Member.get_devnet_profile_by_id(user.provider_id)
        if user.devnet_profile and 'accounts' in user.devnet_profile:
            user.email = extract_email_prefix(user.devnet_profile['accounts'])
            user.cr_profile = Member.get_cr_profile_by_email(user.email)
            if user.cr_profile:
                Member.add_member_tag(user.email,devnet_account_tag)
                await log_message_to_room(user, activityType='New Registration from DevNet')
        print(user)


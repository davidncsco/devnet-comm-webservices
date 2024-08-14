import requests, json, re, markdownify
from db.model import WebexMessageTemplate
from typing import List
from utils.session import SessionManager


def convert_to_localtime(utc_str):
    from datetime import datetime, timezone
    
    if utc_str:
        # Parse the UTC datetime string
        utc_datetime = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Convert to local time
        local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone()
        return local_datetime.strftime('%m/%d/%Y %H:%M')
    else:
        return None

def truncate_string(long_string, max_lines=2):
    """
    Truncates a long string to a maximum of two lines and adds "...".

    Args:
        long_string: The string to truncate.
        max_lines: The maximum number of lines to keep (default: 2).

    Returns:
        The truncated string.
    """
    lines = long_string.splitlines()
    if len(lines) <= max_lines:
        return long_string
    else:
        return "\n".join(lines[:max_lines]) + "..."
    
def get_filled_template(payload, template: List[str]) -> str:
    msg_template = '\n'.join(template)
    member_attr = payload.get('member', {})
    return msg_template.format(
        activityType=payload.get('activityType',''),
        member=member_attr.get('fullName',''),        
        platform=payload.get('serviceName', ''),
        title=payload.get('title', ''),
        topics=', '.join(payload.get('topics', [])),
        link=payload.get('externalActivityUrl', ''),
        emails=', '.join(member_attr.get('allEmails', [])),
        datetime=convert_to_localtime(payload.get('timestamp', '')),
        summary=truncate_string(payload.get('content', ''), 3),
        email=payload.get('email',''),
        provider_id=payload.get('provider_id','')
    )


def send_message_to_room(room_id, payload, template: WebexMessageTemplate): 
    # Prepare JSON data for the message
    # Message content (supports plain text, markdown, or HTML)
    if not payload: # If payload is empty
        return
    
    url = "https://webexapis.com/v1/messages"
    session = SessionManager()
    bot_access_token = session.get("bot_access_token")
    headers = {
        "Authorization": f"Bearer {bot_access_token}",
        "Content-Type": "application/json",
    }   

    filled_template = get_filled_template(payload,template.template)
    data = {"roomId": room_id, "html": filled_template}
    #print(f"send_message_to_room, data={data}")
    response = requests.post(url, headers=headers, json=data)

    # Check for successful response
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")


def send_warning_message_to_room(room_id: str, message: str): 
    # Send warning message to admin in the community manager webex room
    url = "https://webexapis.com/v1/messages"
    session = SessionManager()
    bot_access_token = session.get("bot_access_token")
    headers = {
        "Authorization": f"Bearer {bot_access_token}",
        "Content-Type": "application/json",
    }   

    data = {"roomId": room_id, "text": message}
    print(f"send_warning_message_to_room, data={data}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")
        

def get_access_token(session: SessionManager, code: str):
    #STEP 3 : use code in response from Webex api to collect the code parameter
    #to obtain an access token or refresh token
    url = 'https://webexapis.com/v1/access_token'
    headers = {
        'accept':'application/json',
        'content-type':'application/x-www-form-urlencoded'
    }
    payload = {
        "grant_type": "authorization_code",
        "client_id": session.get("webex_client_id"),
        "client_secret": session.get("webex_client_secret"),
        "redirect_uri": session.get("webex_redirect_uri"),
        "code": code
    }
    response = requests.post(url=url, data=payload, headers=headers)
    if response.status_code != 200:
        print(f"func get_access_token, Error: {response.status_code} - {response.text}")
        return None
    results = json.loads(response.text)
    print(f"func get_access_token, results={results}")
    session.set("access_token", results["access_token"])
    session.set("refresh_token", results["refresh_token"])

    return results["access_token"]

def refresh_webex_token(session: SessionManager):
    url = "https://webexapis.com/v1/access_token"
    headers = {
        'accept':'application/json',
        'content-type':'application/x-www-form-urlencoded'
    }
    payload = {
        "grant_type": "refresh_token",
        "client_id": session.get("webex_client_id"),
        "client_secret": session.get("webex_client_secret"),
        "refresh_token": session.get("refresh_token")
    }
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code != 200:
        print(f"func refresh_webex_token, Error: {response.status_code} - {response.text}")
        return None
    results = json.loads(response.text)
    print(f"func refresh_webex_token, results={results}")
    session.set("access_token", results["access_token"])
    session.set("refresh_token", results["refresh_token"])

    return results["access_token"]

def get_webex_room_title(room_id: str) -> str:
    """
    Get the title of a Webex room using its ID.
    """
    if not room_id:
        return None
    session = SessionManager()
    access_token = session.get("access_token")
    url = f"https://webexapis.com/v1/rooms/{room_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        room_details = json.loads(response.text)
        return room_details.get("title")
    return None
    
def get_webex_message_details(session: SessionManager, message_id: str) -> dict:
    access_token = session.get("access_token")
    url = f"https://webexapis.com/v1/messages/{message_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        message_details = json.loads(response.text)
        return message_details
    else:
        if response.status_code == 401:
            new_access_token = refresh_webex_token(session)
            if new_access_token:
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    message_details = json.loads(response.text)
                    return message_details
                else:
                    print(f"Error getting message details after refreshing token: {response.status_code} - {response.text}")
                    return None
            else:
                print("Error refreshing access token")
                return None
        else:
            print(f"Error getting message details: {response.status_code} - {response.text}")
            return None


def parse_social_handles(social_dict: dict) -> str:
    """
    Parse social handles from the given dictionary.

    Parameters:
    - social_dict: Dictionary containing social media URLs.

    Returns:
    - A dictionary with non-empty social handles in the specified format.
    """
    parsed_handles = {}

    for platform, url in social_dict.items():
        if url:
            # Extract the handle part from the URL
            handle = re.sub(r'^https?://(www\.)?[^/]+/', '', url)
            parsed_handles[platform] = {"type": "handle", "value": handle}

    return parsed_handles
            
# Webex Activity signal in Commom Room (API signal)  
DESTINATION_SOURCE_ID = 64482

def process_member_activity(email: str, message: dict):
    from utils.member import Member
    
    """
    Process member activity from Webex message
    """
    print("func process_member_activity")
    #print(f"process_member_activity: email={email}, message={message}")
    user = Member(email,'',{},{})
    user.provider_id = Member.get_devnet_profile_by_email(email)
    if user.provider_id:
        user.devnet_profile = Member.get_devnet_profile_by_id(user.provider_id)
        if message_content := message.get('html'):
            content_text = markdownify.markdownify(message_content).replace('`', '')
            content_type = "markdown"
        else:
            content_text = message.get('text')
            content_type = "text"
        socials = parse_social_handles(user.devnet_profile['social'])
        activity_details = {  
            "id" : message.get('id'),
            "activityType" : "sent_a_message",
            "user" : {
                "id" : user.provider_id,
                "fullName": user.devnet_profile['user'].get('fullName',''),
                "firstName": user.devnet_profile['user'].get('firstName',''),
                "lastName": user.devnet_profile['user'].get('lastName',''),
                "city": user.devnet_profile['address'].get('city',''),
                "email": email,
                "linkedin": socials.get('linkedin',{'type':'handle','value':''}),
                "twitter": socials.get('twitter',{'type':'handle','value':''}),
                "github": socials.get('github',{'type':'handle','value':''})
            },
            "activityTitle" : {
                "type": "text",
                "value": f"New Webex message from {get_webex_room_title(message.get('roomId'))} room"
            },
            "content": {
                "type": content_type,
                "value": content_text
            },
            "timestamp": message.get('created'),
        }
        #print(f"Activity details: {activity_details}")
        Member.add_member_activity(DESTINATION_SOURCE_ID,activity_details)

async def process_webex_new_message(session: SessionManager, data: dict):
    print("func process_webex_new_message")
    #print(f"access_token={session.get('access_token')}, data={data}")
    email = data.get('personEmail')
    if email.endswith('@webex.bot'):
        print("Ignore message from Webex bot")
        return
    print(f"Received message from {email}")
    message = get_webex_message_details(session, data.get('id'))
    if message:
        #print(f"Message details: {message}")
        process_member_activity(email, message)




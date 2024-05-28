import requests, os
from db.model import WebexMessageTemplate
from typing import List

# Bot's access token
access_token = os.getenv("BOT_ACCESS_TOKEN", None)

# Build the request URL
url = "https://webexapis.com/v1/messages"

# Set headers with authorization
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
 
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
        
    filled_template = get_filled_template(payload,template.template)
    data = {"roomId": room_id, "html": filled_template}
    #print(f"send_message_to_room, data={data}")
    response = requests.post(url, headers=headers, json=data)

    # Check for successful response
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")

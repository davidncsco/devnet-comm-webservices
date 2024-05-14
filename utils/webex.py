import requests, json
from db.model import WebhookPayload

# Bot's access token
access_token = "Y2NjNjU1ODItNDAzYi00ZDBmLWEyNzQtMDFmNjExMGRlNjJjODE0ZGE2NjAtNWI3_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"

# Build the request URL
url = "https://webexapis.com/v1/messages"

# Set headers with authorization
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

TEMPLATES = [
    """
    <hr>
    <h2>{activityType}</h2><br>
    <br>
    <b>Title:</b> {title}<br>
    <b>Member:</b> {member}<br>
    <b>Email:</b> {emails}<br>
    <b>Platform:</b> {platform}<br>
    <b>Date/time:</b> {datetime}<br>
    <b>Topics:</b> {topics}<br>
    <b>Link:</b> {link}<br>
    <b>Summary:</b> {summary}
    """,
    
    """
    <hr>
    <h2>{activityType}</h2><br>
    <br>   
    <b>Member:</b> {member}<br>
    <b>Platform:</b> {platform}<br>
    <b>Date/time:</b> {datetime}<br>
    <b>Topics:</b> {topics}<br>
    <b>Link:</b> {link}
    """,
    
    """
    <h2>{activityType}</h2><br>
    <br>
    <b>Member:</b> {member}<br>
    <b>Topics:</b> {topics}<br>
    <b>Link:</b> {link}
    """
]

def convert_to_localtime(utc_str):
    from datetime import datetime, timezone

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # Convert to local time
    local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone()

    return local_datetime.strftime('%m/%d/%Y %H:%M')
    

def truncate_string(long_string, max_lines=3):
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


def send_message_to_room(room_id, body, template): 
    # Prepare JSON data for the message
    # Message content (supports plain text, markdown, or HTML)
    print(f"Sending msg to room: {room_id} with template={template}")
    payload = dict(body.data).get('payload',{})
    if not payload:
        return
    filled_template = TEMPLATES[template-1].format(
        activityType=payload['activityType'],
        member=payload['member']['fullName'],
        platform=payload['serviceName'],
        title=payload.get('title', ''),
        topics=', '.join(payload['topics']),
        link=payload['externalActivityUrl'],
        emails=', '.join(payload['member']['allEmails']),
        datetime=convert_to_localtime(payload['timestamp']),
        summary=truncate_string(payload.get('content', ''), 6)
    )

    data = {"roomId": room_id, "html": filled_template}
    response = requests.post(url, headers=headers, json=data)

    # Check for successful response
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")

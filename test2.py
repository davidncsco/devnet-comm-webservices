import random,json,os
import requests
import asyncio

from utils.webex import send_message_to_room
from db.crud import DataAccess
from db.model import Webhook

def get_random_star_wars_character():
    # Fetch data from SWAPI, return a random character name, replacing blank with underline
    response = requests.get("https://swapi.dev/api/people/")
    if response.status_code != 200:
        print("Error fetching data from SWAPI")
        return None

    characters = response.json().get("results", [])
    if not characters:
        print("No characters found in SWAPI data")
        return None

    # Select a random character
    random_character = random.choice(characters)
    return random_character.get("name", "Unknown").replace(" ", "_")

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

def convert_to_localtime(utc_str):
    from datetime import datetime

    # Define the UTC datetime string
    utc_datetime_str = "2024-05-13T21:56:34.000Z"

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Convert to local time and format as desired
    local_datetime = utc_datetime.astimezone()
    return local_datetime.strftime('%m/%d/%Y %H:%M')

def convert_to_localtime2(utc_str):
    from datetime import datetime, timezone

    # Parse the UTC datetime string
    utc_datetime = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # Convert to local time
    local_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone()

    return local_datetime.strftime('%m/%d/%Y %H:%M')

async def main():
    room_id = "Y2lzY29zcGFyazovL3VzL1JPT00vMTYzMDc4OTAtZTZmNy0xMWVlLTgxYzgtNGRhY2Q3ZTM4Yjdj"
    with open('sample.json') as sample:
        data = json.load(sample)
        payload = data['payload']
    # summary=payload.get('content', '')
    # truncated_summary = truncate_string(summary,6)
    # print(f"Summary:{truncated_summary}")
    if payload['type'] == "member":
        #process_new_registration(payload)
        name = "biggs_darklighter"
        data_access = DataAccess()      
        webhook = await data_access.get_webhook_by_name(name)
        template = await data_access.get_template_by_id(webhook.template)
        payload = {"email": 'davidn@cisco.com',"provider_id":'867ef884-fab7-5c9e-9b20-dd73fd6293e5'}
        print(f"payload={payload}")
        send_message_to_room(webhook.roomId, payload, template)
        
asyncio.run(main())
    
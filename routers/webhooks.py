from fastapi import APIRouter, Depends, Request, Response
from db.database import get_database
from db.model import Webhook, CommonRoom_WebhookPayload, WebhookDevNetNewRegistration
from utils.member import process_new_registration
from utils.session import SessionManager

from utils.webex import (
    send_message_to_room,
    send_warning_message_to_room,
    process_webex_new_message
)

from db.crud import (
    fetch_all_webhooks,
    add_webhook,
    get_webhook,
    update_webhook,
    delete_webhook,
    get_template
)

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
webhooks = APIRouter(prefix="/v1/community/webhooks", tags=["Webhooks"])
webhooks.limiter = limiter

@webhooks.get("/")
@limiter.limit("10/second")
async def get_all_webhooks(request: Request, response: Response, db: any = Depends(get_database)):
    return await fetch_all_webhooks(db)


@webhooks.post("/")
async def create_webhook(webhook: Webhook, db: any = Depends(get_database)):
    return await add_webhook(db, webhook)


@webhooks.get("/{name}")
async def read_webhook(name: str, db: any = Depends(get_database)):
    return await get_webhook(db, name)


@webhooks.put("/{name}")
async def modify_webhook(name: str, webhook: Webhook, db: any = Depends(get_database)):
    return await update_webhook(db, name, webhook.template)


@webhooks.delete("/{name}")
async def remove_webhook(name: str, db: any = Depends(get_database)):
    return await delete_webhook(db, name)


@webhooks.post("/process/{name}")
async def process_webhook(name: str, body: CommonRoom_WebhookPayload, db: any = Depends(get_database)):
    print(f"Webhook name = {name}")
    if body.payload:
        payload = dict(body.payload)
        print(f"payload type={payload['type']}")
        if payload['type'] == "activity":
            webhook: Webhook = await get_webhook(db, name)
            msg_template = await get_template(db,webhook.template)
            if msg_template:
                send_message_to_room(webhook.roomId, dict(body.payload), msg_template)
                return {"message": "webhook processed successfully!"}
            else:
                return {"message": "can't process webhook"}
        elif payload['type'] == "member":
            await process_new_registration(source='cr', payload=payload)
            return {"message": f"received member payload for {payload['fullName']}"}
        elif payload['type'] == "organization":
            return {"message": f"received organization payload for {payload['name']}"}
    return {"message": f"unknown payload type '{payload['type']}'"}


@webhooks.post("/registration")
async def process_devnet_registration(new_user: WebhookDevNetNewRegistration):
    print("Receive new DevNet user registration")
    print(f"user_id={new_user.profile_id}")
    print(f"registration time={new_user.registration_time}")
    print(f"refer url={new_user.refer_url}")
    await process_new_registration(source='devnet', payload={'id': new_user.profile_id, 'time': new_user.registration_time})
    return {"Message":"devnet registration processed"}

# Define name of functions to process webex webhooks with matching resource and event
webhooks_processor = [
    {'resource': 'messages', 'event': 'created', 'handler': 'process_webex_new_message'},
]
# This is  "DevNet Community Programs" roomId, hardcoded for now


@webhooks.post("/webex")
async def process_webex_webhook(body: dict, db: any = Depends(get_database)):
    session = SessionManager()
    if not session.get('access_token'):
        if admin_webex_room_id := session.get("admin_webex_room_id"):
            send_warning_message_to_room(admin_webex_room_id,"ATTENTION: Community Webservices needs to seed access_token to start processing Webex webhooks.")
        return {"message": "No access token. Please generate a seed access token"}
    # print(f"access_token = {session.get('access_token')}")
    # print(f"Webex webhook body = {body}")
    resource = body.get('resource')
    event = body.get('event')
    for processor in webhooks_processor:
        if processor['resource'] == resource and processor['event'] == event:
            handler_name = processor['handler']
            handler = globals().get(handler_name)
            if handler:
                await handler(session,body.get('data'))
                return {"message": "Webex webhook processed successfully!"}
            else:
                print(f"Handler {handler_name} not found.")
                return {"message": "invalid handler defined for event!"}
    print(f"No handler found for resource {resource} and event {event}.")   
    return {"message": "No handler found for resource and event!"}
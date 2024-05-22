from fastapi import APIRouter, Depends 
from db.database import get_database
from db.model import Webhook, WebhookPayload, WebhookDevNetNewRegistration
from utils.webex import send_message_to_room
from db.crud import (
    fetch_all_webhooks,
    add_webhook,
    get_webhook,
    update_webhook,
    delete_webhook,
    get_template
)


webhooks = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@webhooks.get("/")
async def get_all_webhooks(db: any = Depends(get_database)):
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
async def process_webhook(name: str, body: WebhookPayload, db: any = Depends(get_database)):
    print(f"Webhook name = {name}")
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
        return {"message": f"received member payload for {payload['fullName']}"}
    elif payload['type'] == "organization":
        return {"message": f"received organization payload for {payload['name']}"}
    else:
        return {"message": f"unknown payload type {payload['type']}"}
    
@webhooks.post("/registration")
async def process_devnet_new_registration(new_user: WebhookDevNetNewRegistration):
    print("Receive new DevNet user registration")
    print(f"user_id={new_user.user_id}")
    print(f"registration time={new_user.registration_time}")
    print(f"refer url={new_user.refer_url}")
    return {"Message":"new registration processed successfully"}
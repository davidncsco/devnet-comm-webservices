from fastapi import APIRouter, Depends, HTTPException 
from db.database import get_database
from db.model import Webhook, WebhookPayload
from utils.crud import (
    fetch_all_webhooks,
    add_webhook,
    get_webhook,
    update_webhook,
    delete_webhook
)

from utils.webex import (
  send_message_to_room
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
    return await update_webhook(db, name, webhook)


@webhooks.delete("/{name}")
async def remove_webhook(name: str, db: any = Depends(get_database)):
    return await delete_webhook(db, name)


@webhooks.post("/name={name}")
async def process_webhook(name: str, body: WebhookPayload, db: any = Depends(get_database)):
  print(f"Webhook name = {name}")
  webhook = await get_webhook(db, name)
  if webhook:
      room_id, template = (webhook.roomId, webhook.template)
      send_message_to_room(room_id, body, template)
      return {"message": "webhook processed successfully!"}
  else:
      return {"message": "can't process webhook"}
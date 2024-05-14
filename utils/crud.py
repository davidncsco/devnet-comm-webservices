from fastapi import HTTPException
from bson import ObjectId
from db.model import Webhook

async def fetch_all_webhooks(db):
    webhooks = []
    cursor = db.webhooks.find({})
    async for webhook in cursor:
        webhooks.append(Webhook(**webhook))
    return webhooks

async def add_webhook(db, webhook: Webhook):
    await db.webhooks.insert_one(dict(webhook))
    return webhook

async def get_webhook(db, name: str):
    webhook = await db.webhooks.find_one({"name": name})
    if not webhook:
        raise HTTPException(status_code=404, detail="webhook "+name+" not found")
        return None
    return Webhook(**webhook)

async def update_webhook(db, name: str, webhook: Webhook):
    return webhook

async def delete_webhook(db, name: str):
    webhook = await db.webhooks.delete_one({"name": name})
    return {"message":"webhook deleted"}

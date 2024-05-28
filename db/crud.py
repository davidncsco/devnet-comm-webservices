from fastapi import HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from db.model import Webhook, WebexMessageTemplate, WebhookDevNetNewRegistration
from typing import List
import os

db_connect_uri = os.getenv("DB_CONNECTION","mongodb://davidn:cisco@127.0.0.1:27017/")
db_name = 'webservices'

class DataAccess:
    def __init__(self):
        self.client = AsyncIOMotorClient(db_connect_uri)
        self.db = self.client[db_name]
        self.webhooks: List[Webhook] = []
        self.templates: List[WebexMessageTemplate] = []

    async def get_all_webhooks(self) -> List[Webhook]:
        if len(self.webhooks) == 0:
            self.webhooks = await fetch_all_webhooks(self.db)

        return self.webhooks
    
    async def get_all_templates(self) -> List[WebexMessageTemplate]:
        if len(self.templates) == 0:
            self.templates = await fetch_all_templates(self.db)
        return self.templates
    
    async def get_webhook_by_name(self, name) -> Webhook:
        await self.get_all_webhooks()
        for webhook in self.webhooks:
            if webhook.name == name.lower():
                return webhook
        return None
    
    async def get_template_by_id(self, id):
        await self.get_all_templates()
        for template in self.templates:
            if template.id == id:
                return template
        return None
        
async def fetch_all_webhooks(db) -> list:
    webhooks = []
    async for webhook in db.webhooks.find({}):
        webhooks.append(Webhook(**webhook))
    return webhooks

async def add_webhook(db, webhook: Webhook) -> Webhook:
    await db.webhooks.insert_one(dict(webhook))
    return webhook

async def get_webhook(db, name: str) -> Webhook:
    webhook = await db.webhooks.find_one({"name": name})
    if not webhook:
        raise HTTPException(status_code=404, detail="webhook "+name+" not found")
        return None

    return Webhook(**webhook)

async def update_webhook(db, name: str, template_id: int) -> Webhook:
    # Only update template id is allowed
    filter = {"name": name}
    webhook = await db.webhooks.find_one(filter)
    if webhook is None:
        raise HTTPException(status_code=404, detail=f"webhook {name} not found")
        return None
    await db.webhooks.update_one(filter,  {"$set": {"template": template_id}})
    webhook['template'] = template_id
    return (Webhook)(**webhook)

async def delete_webhook(db, name: str) -> dict:
    webhook = await db.webhooks.delete_one({"name": name})
    return {"message":"webhook deleted"}

async def fetch_all_templates(db) -> List[WebexMessageTemplate]:
    templates = []
    async for template in db.templates.find({}):
        templates.append(WebexMessageTemplate(**template))
    return templates

async def add_template(db, template: WebexMessageTemplate) -> WebexMessageTemplate:
    global templates
    
    await db.templates.insert_one(dict(template))
    templates.append(WebexMessageTemplate(**template))
    return template

async def get_template(db, id: int) -> WebexMessageTemplate:
    template = await db.templates.find_one({"id": id})
    if not template:
        raise HTTPException(status_code=404, detail="template "+str(id)+" not found")
        return None
    return WebexMessageTemplate(**template)

async def update_template(db, id: int, update_template: WebexMessageTemplate) -> WebexMessageTemplate:
    global templates
    
    filter = {"id": id}
    template = await db.templates.find_one(filter)
    if template is None:
        raise HTTPException(status_code=404, detail=f"template {id} not found")
        return None
    await db.templates.update_one(filter,  {"$set": {"template": update_template.template}})
    if len(templates) >= id:
        templates[id-1] = update_template
    return update_template

async def delete_template(db, id: int) -> dict:
    template = await db.templates.delete_one({"id": id})
    return {"message":"template deleted"}

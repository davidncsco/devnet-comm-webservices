from fastapi import HTTPException
from db.model import Webhook, WebexMessageTemplate, WebhookDevNetNewRegistration
from typing import List

async def fetch_all_webhooks(db) -> list:
    webhooks = []
    cursor = db.webhooks.find({})
    async for webhook in cursor:
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

##### Webex message Template CRUD #####
templates: List[WebexMessageTemplate] = []

async def fetch_all_templates(db) -> list:
    global templates
    
    if len(templates) == 0:
        async for template in db.templates.find({}):
            templates.append(WebexMessageTemplate(**template))
    return templates

async def add_template(db, template: WebexMessageTemplate) -> WebexMessageTemplate:
    global templates
    
    await db.templates.insert_one(dict(template))
    templates.append(WebexMessageTemplate(**template))
    return template

async def get_template(db, id: int) -> WebexMessageTemplate:
    global templates
    
    if len(templates) == 0:
        templates = await fetch_all_templates(db)
    if( id > len(templates)):   # default is the first template
        return templates[0]
    return  templates[id-1]

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

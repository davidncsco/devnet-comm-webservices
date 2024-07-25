
from pydantic import BaseModel
from typing import List
    
class Webhook(BaseModel):
    _id: str | None = None
    roomId: str
    name: str
    template: int | None = 1

class CommonRoom_WebhookPayload(BaseModel):
    payload: dict
    id: str
    source: dict
    

class WebexMessageTemplate(BaseModel):
    id: int
    name: str
    type: str
    template: List[str]
  
class WebhookDevNetNewRegistration(BaseModel):
    profile_id: str
    registration_time: str
    refer_url: str

from pydantic import BaseModel
    
class Webhook(BaseModel):
    _id: str | None = None
    roomId: str
    name: str
    template: int | None = 1
    
    
class WebhookPayload(BaseModel):
  payload: dict
  id: str
  source: dict


import os
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from routers.webhooks import webhooks
from routers.templates import templates
from fastapi.responses import FileResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from utils.webex import get_access_token
from utils.session import SessionManager


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(webhooks)
app.include_router(templates)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Get environment variables and store them in the session
session = SessionManager()
# DevNet Community Bot access token
session.set("bot_access_token", os.getenv("BOT_ACCESS_TOKEN"))
# Client ID and secret for Webex OAuth workflow
session.set("webex_client_id", os.getenv("WEBEX_CLIENT_ID"))
session.set("webex_client_secret", os.getenv("WEBEX_CLIENT_SECRET"))
session.set("webex_redirect_uri", os.getenv("WEBEX_REDIRECT_URI"))
# Admin Webex Room ID where the bot will send messages for admin purposes
session.set("admin_webex_room_id",os.getenv("ADMIN_WEBEX_ROOM_ID"))

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request, response: Response):
    return {"message": "Hello from DevNet Community Web Services"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/v1/community/auth_code")
async def webex_auth_redirect(code: str, state:str):
    print(f"code: {code}, state: {state}")
    results = get_access_token(session, code)
    if results:
        return {"access_token": results}
    else:
        return {"error": "Failed to get access token"}

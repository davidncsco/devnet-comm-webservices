
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.webhooks import webhooks
from routers.templates import templates

app = FastAPI()
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
 
@app.get("/")
async def root():
    return {"message": "Hello from DevNet Community Web Services"}

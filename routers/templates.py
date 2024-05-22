from fastapi import APIRouter, Depends 
from db.database import get_database
from db.model import WebexMessageTemplate

from db.crud import (
    fetch_all_templates,
    add_template,
    get_template,
    update_template,
    delete_template
)

templates = APIRouter(prefix="/template", tags=["Message Template"])


@templates.get("/")
async def get_all_template(db: any = Depends(get_database)):
    return await fetch_all_templates(db)


@templates.post("/")
async def create_template(template: WebexMessageTemplate, db: any = Depends(get_database)):
    return await add_template(db, template)


@templates.get("/{id}")
async def read_template(id: int, db: any = Depends(get_database)):
    return await get_template(db, id)


@templates.put("/{id}")
async def modify_template(id: int, template: WebexMessageTemplate, db: any = Depends(get_database)):
    return await update_template(db, id, template)


@templates.delete("/{id}")
async def remove_template(id: int, db: any = Depends(get_database)):
    return await delete_template(db, id)

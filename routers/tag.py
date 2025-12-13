from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from databases.schemas import TagCreate, TagUpdate, TagOut
from databases.crud import (
    create_tag, get_tags, get_tag, update_tag, delete_tag, get_enabled_tags
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token
from helpers.config import AppConfig

app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/tags", tags=["Tags"])

@router.post("/", dependencies=[Depends(verify_yang_auth_token)], response_model=TagOut)
async def create_tag_route(data: TagCreate, db: AsyncSession = Depends(get_db)):
    return await create_tag(db, data)

@router.get("/", dependencies=[Depends(verify_yang_auth_token)], response_model=list[TagOut])
async def list_tags_route(db: AsyncSession = Depends(get_db)):
    return await get_tags(db)

@router.get("/enabled", dependencies=[Depends(verify_yang_auth_token)], response_model=list[TagOut])
async def list_enabled_tags_route(db: AsyncSession = Depends(get_db)):
    return await get_enabled_tags(db)

@router.get("/{tag_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=TagOut)
async def get_tag_route(tag_id: int, db: AsyncSession = Depends(get_db)):
    tag = await get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.put("/{tag_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=TagOut)
async def update_tag_route(tag_id: int, data: TagUpdate, db: AsyncSession = Depends(get_db)):
    tag = await update_tag(db, tag_id, data)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.delete("/{tag_id}", dependencies=[Depends(verify_yang_auth_token)])
async def delete_tag_route(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_tag(db, tag_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tag not found")
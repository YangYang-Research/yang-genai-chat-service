from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from databases.schemas import MessageCreate, MessageOut
from databases.crud import (
    create_message, get_message, get_user_messages, delete_message
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token
from helpers.config import AppConfig

app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/messages", tags=["Messages"])


@router.post("/", response_model=MessageOut)
async def create_message_route(data: MessageCreate, db: AsyncSession = Depends(get_db)):
    return await create_message(db, data)


@router.get("/user/{user_id}", response_model=list[MessageOut])
async def list_user_messages(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_messages(db, user_id)


@router.get("/{message_id}", response_model=MessageOut)
async def get_message_route(message_id: int, db: AsyncSession = Depends(get_db)):
    msg = await get_message(db, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


@router.delete("/{message_id}")
async def delete_message_route(message_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_message(db, message_id)
    if not result:
        raise HTTPException(status_code=404, detail="Message not found")

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from databases.schemas import UserCreate, UserUpdate, UserOut
from databases.crud import (
    create_user, get_users, get_user, get_user_by_username, update_user, delete_user
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token
from helpers.config import AppConfig

app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/users", tags=["Users"])


@router.post("/", dependencies=[Depends(verify_yang_auth_token)], response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_route(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, data)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return user


@router.get("/", dependencies=[Depends(verify_yang_auth_token)], response_model=list[UserOut])
async def list_users_route(db: AsyncSession = Depends(get_db)):
    return await get_users(db)


@router.get("/{user_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=UserOut)
async def get_user_route(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=UserOut)
async def update_user_route(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await update_user(db, user_id, data)
    if isinstance(user, tuple):
        if user[0] == 404:
            raise HTTPException(status_code=404, detail="User not found")
        elif user[0] == 400:
            raise HTTPException(status_code=400, detail="Username or email already taken")
    return user


@router.delete("/{user_id}", dependencies=[Depends(verify_yang_auth_token)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

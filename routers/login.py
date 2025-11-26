from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from databases.schemas import UserCreate, UserUpdate, UserOut
from databases.crud import (
    get_user_by_username
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_password, create_jwt_token
from helpers.config import AppConfig

app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/authentication", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", dependencies=[Depends(verify_yang_auth_token)])
async def user_login_route(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    username = payload.username
    password = payload.password

    user = await get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_user_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 3. Validate account status
    if user.active_status != "enable":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    
    # 4. Generate JWT token
    payload = {
        "sub": 'yang-yang',
        "username": user.username,
        "email": user.email,
        "fullname": user.fullname,
        "role": user.roles.name,
    }

    jwt_token = create_jwt_token(payload)

    return {
        "message": "Login successful",
        "jwt_token": jwt_token
    }
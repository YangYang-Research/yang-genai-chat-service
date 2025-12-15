from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from databases.schemas import RoleCreate, RoleUpdate, RoleOut
from databases.crud import (
    create_role, get_roles, get_role, update_role, delete_role
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token
from helpers.config import AppConfig

app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/roles", tags=["Roles"])

@router.post("/", dependencies=[Depends(verify_yang_auth_token)], response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role_route(data: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await create_role(db, data)

@router.get("/", dependencies=[Depends(verify_yang_auth_token)], response_model=list[RoleOut])
async def list_roles_route(db: AsyncSession = Depends(get_db)):
    return await get_roles(db)

@router.get("/{role_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=RoleOut)
async def get_role_route(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=RoleOut)
async def update_role_route(role_id: int, data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    role = await update_role(db, role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.delete("/{role_id}", dependencies=[Depends(verify_yang_auth_token)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_route(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_role(db, role_id)
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
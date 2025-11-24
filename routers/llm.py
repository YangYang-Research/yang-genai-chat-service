from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from databases.schemas import LLMCreate, LLMUpdate, LLMOut
from databases.crud import (
    create_llm, get_llms, get_llm, update_llm, delete_llm
)
from databases.database import get_db
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token

router = APIRouter(prefix="/llms", tags=["LLMs"])


@router.post("/", dependencies=[Depends(verify_yang_auth_token)], response_model=LLMOut)
async def create_llm_route(data: LLMCreate, db: AsyncSession = Depends(get_db)):
    return await create_llm(db, data)


@router.get("/", dependencies=[Depends(verify_yang_auth_token)], response_model=list[LLMOut])
async def list_llms_route(db: AsyncSession = Depends(get_db)):
    return await get_llms(db)


@router.get("/{llm_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=LLMOut)
async def get_llm_route(llm_id: int, db: AsyncSession = Depends(get_db)):
    llm = await get_llm(db, llm_id)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm


@router.put("/{llm_id}", dependencies=[Depends(verify_yang_auth_token)], response_model=LLMOut)
async def update_llm_route(llm_id: int, data: LLMUpdate, db: AsyncSession = Depends(get_db)):
    llm = await update_llm(db, llm_id, data)
    if not llm:
        raise HTTPException(status_code=404, detail="LLM not found")
    return llm


@router.delete("/{llm_id}", dependencies=[Depends(verify_yang_auth_token)])
async def delete_llm_route(llm_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_llm(db, llm_id)
    if not result:
        raise HTTPException(status_code=404, detail="LLM not found")

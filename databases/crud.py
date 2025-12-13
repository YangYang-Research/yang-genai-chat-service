# crud.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from databases import models, schemas

# -------------------  USERS  -------------------

async def create_user(db: AsyncSession, data: schemas.UserCreate):
    user_data = data.model_dump()
    user = models.UserModel(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession):
    result = await db.execute(select(models.UserModel))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.UserModel).options(joinedload(models.UserModel.roles)).where(models.UserModel.username == username)
    )
    return result.scalars().first()

async def update_user(db: AsyncSession, user_id: int, data: schemas.UserUpdate):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        return None

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        return None

    await db.delete(user)
    await db.commit()
    return True

# -------------------  MESSAGES  -------------------

async def create_message(db: AsyncSession, data: schemas.MessageCreate):
    message_data = data.model_dump()
    message = models.MessageModel(**message_data)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_user_messages(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.MessageModel).where(models.MessageModel.user_id == user_id)
    )
    return result.scalars().all()


async def get_message(db: AsyncSession, message_id: int):
    result = await db.execute(
        select(models.MessageModel).where(models.MessageModel.id == message_id)
    )
    return result.scalars().first()


async def delete_message(db: AsyncSession, message_id: int):
    result = await db.execute(
        select(models.MessageModel).where(models.MessageModel.id == message_id)
    )
    msg = result.scalars().first()
    if not msg:
        return None

    await db.delete(msg)
    await db.commit()
    return True

# -------------------  TOOL CONFIG  -------------------

async def create_tool(db: AsyncSession, data: schemas.ToolCreate):
    tool_data = data.model_dump()
    tool = models.ToolModel(**tool_data)
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def get_tools(db: AsyncSession):
    result = await db.execute(select(models.ToolModel))
    return result.scalars().all()


async def get_tool(db: AsyncSession, tool_id: int):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id)
    )
    return result.scalars().first()


async def get_tool_by_name(db: AsyncSession, tool_name: str):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.name == tool_name)
    )
    return result.scalars().first()


async def get_enabled_tools(db: AsyncSession):
    """Return all tools where status=='enable'"""
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.status == "enable")
    )
    return result.scalars().all()


async def update_tool(db: AsyncSession, tool_id: int, data: schemas.ToolUpdate):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id)
    )
    tool = result.scalars().first()
    if not tool:
        return None

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tool, key, value)

    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def delete_tool(db: AsyncSession, tool_id: int):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id)
    )
    tool = result.scalars().first()
    if not tool:
        return None

    await db.delete(tool)
    await db.commit()
    return True


# -------------------  LLMs  -------------------

async def create_llm(db: AsyncSession, data: schemas.LLMCreate):
    llm_data = data.model_dump()
    llm = models.LLMModel(**llm_data)
    db.add(llm)
    await db.commit()
    await db.refresh(llm)
    return llm


async def get_llms(db: AsyncSession):
    result = await db.execute(select(models.LLMModel))
    return result.scalars().all()

async def get_enabled_llms(db: AsyncSession):
    result = await db.execute(select(models.LLMModel).where(models.LLMModel.status == "enable"))
    return result.scalars().all()

async def get_llm(db: AsyncSession, llm_id: int):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id)
    )
    return result.scalars().first()

async def get_llm_by_name(db: AsyncSession, llm_name: str):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.name == llm_name)
    )
    return result.scalars().first()

async def update_llm(db: AsyncSession, llm_id: int, data: schemas.LLMUpdate):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id)
    )
    llm = result.scalars().first()
    if not llm:
        return None

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(llm, key, value)

    db.add(llm)
    await db.commit()
    await db.refresh(llm)
    return llm


async def delete_llm(db: AsyncSession, llm_id: int):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id)
    )
    llm = result.scalars().first()
    if not llm:
        return None

    await db.delete(llm)
    await db.commit()
    return True

# -------------------  AGENTS  -------------------

async def create_agent(db: AsyncSession, data: schemas.AgentCreate):
    agent_data = data.model_dump()
    agent = models.AgentModel(**agent_data)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_agents(db: AsyncSession):
    result = await db.execute(select(models.AgentModel))
    return result.scalars().all()


async def get_agent(db: AsyncSession, agent_id: int):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id)
    )
    return result.scalars().first()

async def get_agent_by_name(db: AsyncSession, agent_name: str):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.name == agent_name)
    )
    return result.scalars().first()

async def update_agent(db: AsyncSession, agent_id: int, data: schemas.AgentUpdate):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id)
    )
    agent = result.scalars().first()
    if not agent:
        return None

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(agent, key, value)

    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent_id: int):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id)
    )
    agent = result.scalars().first()
    if not agent:
        return None

    await db.delete(agent)
    await db.commit()
    return True

async def get_default_agent(db: AsyncSession):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.default_agent == True)
    )
    return result.scalars().first()
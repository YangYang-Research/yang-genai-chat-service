# crud.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from databases import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# -------------------  ROLES  -------------------

async def create_role(db: AsyncSession, data: schemas.RoleCreate):
    role_data = data.model_dump()
    role = models.RoleModel(**role_data)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def get_roles(db: AsyncSession):
    result = await db.execute(select(models.RoleModel).where(models.RoleModel.trashed == False))
    return result.scalars().all()

async def get_role(db: AsyncSession, role_id: int):
    result = await db.execute(
        select(models.RoleModel).where(models.RoleModel.id == role_id and models.RoleModel.trashed == False)
    )
    return result.scalars().first()

async def get_role_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.RoleModel).where(models.RoleModel.name == name and models.RoleModel.trashed == False)
    )
    return result.scalars().first()

async def update_role(db: AsyncSession, role_id: int, data: schemas.RoleUpdate):
    result = await db.execute(
        select(models.RoleModel).where(models.RoleModel.id == role_id and models.RoleModel.trashed == False)
    )
    role = result.scalars().first()
    if not role:
        return 404, "Role not found"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(role, key, value)

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

async def delete_role(db: AsyncSession, role_id: int):
    result = await db.execute(
        select(models.RoleModel).where(models.RoleModel.id == role_id and models.RoleModel.trashed == False)
    )
    role = result.scalars().first()
    if not role:
        return 404, "Role not found"

    role.trashed = True
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return True

# -------------------  USERS  -------------------

async def create_user(db: AsyncSession, data: schemas.UserCreate):
    # Check if username or email already exists (not trashed)
    result = await db.execute(
        select(models.UserModel).where(
            ((models.UserModel.username == data.username) | (models.UserModel.email == data.email))
            & (models.UserModel.trashed == False)
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        return 400, "Username or email already taken"

    user_data = data.model_dump()
    user_data["hashed_password"] = pwd_context.hash(user_data["hashed_password"])
    user = models.UserModel(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_users(db: AsyncSession):
    result = await db.execute(select(models.UserModel).where(models.UserModel.trashed == False))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id and models.UserModel.trashed == False)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.UserModel).options(joinedload(models.UserModel.roles)).where(models.UserModel.username == username and models.UserModel.trashed == False)
    )
    return result.scalars().first()

async def update_user(db: AsyncSession, user_id: int, data: schemas.UserUpdate):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id and models.UserModel.trashed == False)
    )
    user = result.scalars().first()
    if not user:
        return 404, "User not found"
    result = await db.execute(
        select(models.UserModel).where(
            ((models.UserModel.username == data.username) | (models.UserModel.email == data.email))
            & (models.UserModel.id != user_id)
            & (models.UserModel.trashed == False)
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        return 400, "Username or email already taken"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.id == user_id and models.UserModel.trashed == False)
    )
    user = result.scalars().first()
    if not user:
        return 404, "User not found"

    user.trashed = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
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
        select(models.MessageModel).where(models.MessageModel.user_id == user_id and models.MessageModel.trashed == False)
    )
    return result.scalars().all()


async def get_message(db: AsyncSession, message_id: int):
    result = await db.execute(
        select(models.MessageModel).where(models.MessageModel.id == message_id and models.MessageModel.trashed == False)
    )
    return result.scalars().first()


async def delete_message(db: AsyncSession, message_id: int):
    result = await db.execute(
        select(models.MessageModel).where(models.MessageModel.id == message_id and models.MessageModel.trashed == False)
    )
    msg = result.scalars().first()
    if not msg:
        return 404, "Message not found"

    msg.trashed = True
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
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
    result = await db.execute(select(models.ToolModel).where(models.ToolModel.trashed == False))
    return result.scalars().all()


async def get_tool(db: AsyncSession, tool_id: int):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id and models.ToolModel.trashed == False)
    )
    return result.scalars().first()


async def get_tool_by_name(db: AsyncSession, tool_name: str):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.name == tool_name and models.ToolModel.trashed == False)
    )
    return result.scalars().first()


async def get_enabled_tools(db: AsyncSession):
    """Return all tools where status=='enable'"""
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.status == "enable" and models.ToolModel.trashed == False)
    )
    return result.scalars().all()


async def update_tool(db: AsyncSession, tool_id: int, data: schemas.ToolUpdate):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id and models.ToolModel.trashed == False)
    )
    tool = result.scalars().first()
    if not tool:
        return 404, "Tool not found"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tool, key, value)

    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def delete_tool(db: AsyncSession, tool_id: int):
    result = await db.execute(
        select(models.ToolModel).where(models.ToolModel.id == tool_id and models.ToolModel.trashed == False)
    )
    tool = result.scalars().first()
    if not tool:
        return 404, "Tool not found"

    tool.trashed = True
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
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
    result = await db.execute(select(models.LLMModel).where(models.LLMModel.trashed == False))
    return result.scalars().all()

async def get_enabled_llms(db: AsyncSession):
    result = await db.execute(select(models.LLMModel).where(models.LLMModel.status == "enable" and models.LLMModel.trashed == False))
    return result.scalars().all()

async def get_llm(db: AsyncSession, llm_id: int):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id and models.LLMModel.trashed == False)
    )
    return result.scalars().first()

async def get_llm_by_name(db: AsyncSession, llm_name: str):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.name == llm_name and models.LLMModel.trashed == False)
    )
    return result.scalars().first()

async def update_llm(db: AsyncSession, llm_id: int, data: schemas.LLMUpdate):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id and models.LLMModel.trashed == False)
    )
    llm = result.scalars().first()
    if not llm:
        return 404, "LLM not found"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(llm, key, value)

    db.add(llm)
    await db.commit()
    await db.refresh(llm)
    return llm


async def delete_llm(db: AsyncSession, llm_id: int):
    result = await db.execute(
        select(models.LLMModel).where(models.LLMModel.id == llm_id and models.LLMModel.trashed == False)
    )
    llm = result.scalars().first()
    if not llm:
        return 404, "LLM not found"

    llm.trashed = True
    db.add(llm)
    await db.commit()
    await db.refresh(llm)
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
    result = await db.execute(select(models.AgentModel).where(models.AgentModel.trashed == False))
    return result.scalars().all()


async def get_agent(db: AsyncSession, agent_id: int):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id and models.AgentModel.trashed == False)
    )
    return result.scalars().first()

async def get_agent_by_name(db: AsyncSession, agent_name: str):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.name == agent_name and models.AgentModel.trashed == False)
    )
    return result.scalars().first()

async def update_agent(db: AsyncSession, agent_id: int, data: schemas.AgentUpdate):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id and models.AgentModel.trashed == False)
    )
    agent = result.scalars().first()
    if not agent:
        return 404, "Agent not found"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(agent, key, value)

    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def delete_agent(db: AsyncSession, agent_id: int):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.id == agent_id and models.AgentModel.trashed == False)
    )
    agent = result.scalars().first()
    if not agent:
        return 404, "Agent not found"

    agent.trashed = True
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return True

async def get_default_agent(db: AsyncSession):
    result = await db.execute(
        select(models.AgentModel).where(models.AgentModel.default_agent == True and models.AgentModel.trashed == False)
    )
    return result.scalars().first()

# -------------------  TAGS  -------------------

async def create_tag(db: AsyncSession, data: schemas.TagCreate):
    tag_data = data.model_dump()
    tag = models.TagModel(**tag_data)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

async def get_tags(db: AsyncSession):
    result = await db.execute(select(models.TagModel).where(models.TagModel.trashed == False))
    return result.scalars().all()

async def get_tag(db: AsyncSession, tag_id: int):
    result = await db.execute(
        select(models.TagModel).where(models.TagModel.id == tag_id and models.TagModel.trashed == False)
    )
    return result.scalars().first()

async def get_enabled_tags(db: AsyncSession):
    result = await db.execute(select(models.TagModel).where(models.TagModel.status == "enable" and models.TagModel.trashed == False))
    return result.scalars().all()
    
async def get_tag_by_name(db: AsyncSession, tag_name: str):
    result = await db.execute(
        select(models.TagModel).where(models.TagModel.tag == tag_name and models.TagModel.trashed == False)
    )
    return result.scalars().first()

async def update_tag(db: AsyncSession, tag_id: int, data: schemas.TagUpdate):
    result = await db.execute(
        select(models.TagModel).where(models.TagModel.id == tag_id and models.TagModel.trashed == False)
    )
    tag = result.scalars().first()
    if not tag:
        return 404, "Tag not found"

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tag, key, value)

    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

async def delete_tag(db: AsyncSession, tag_id: int):
    result = await db.execute(
        select(models.TagModel).where(models.TagModel.id == tag_id and models.TagModel.trashed == False)
    )
    tag = result.scalars().first()
    if not tag:
        return 404, "Tag not found"

    tag.trashed = True
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag
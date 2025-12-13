from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# ------------------- User Schemas -------------------

class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    fullname: Optional[str] = None
    changed_password: bool
    active_status: str
    trashed: bool
    role_id: int

class UserCreate(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    fullname: Optional[str] = None
    hashed_password: Optional[str] = None
    active_status: str
    trashed: bool

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}

# ------------------- Message Schemas -------------------

class MessageBase(BaseModel):
    role: str
    content: str
    feedback: Optional[bool] = None
    status: str
    trashed: bool

class MessageCreate(MessageBase):
    user_id: int

class MessageUpdate(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class MessageRead(MessageBase):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}

class MessageOut(MessageBase):
    id: int

    model_config = {"from_attributes": True}

# ------------------- Tool Schemas -------------------

class ToolBase(BaseModel):
    name: str
    display_name: str
    status: str
    logo: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    trashed: bool
    host: Optional[str] = None
    api_key: Optional[str] = None
    cse_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: Optional[str] = None

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    trashed: Optional[bool] = None
    host: Optional[str] = None
    api_key: Optional[str] = None
    cse_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: Optional[str] = None

class ToolRead(ToolBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class ToolOut(ToolBase):
    id: int

    model_config = {"from_attributes": True}

# ------------------- LLM Schemas -------------------

class LLMBase(BaseModel):
    name: str
    display_name: str
    description: str
    logo: str
    provider: str
    region: str
    model_id: str
    model_max_tokens: str
    model_temperature: str
    guardrail_id: Optional[str] = None
    guardrail_version: Optional[str] = None
    system_prompt: str
    status: str
    trashed: bool

class LLMCreate(LLMBase):
    pass

class LLMUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    provider: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = None
    trashed: Optional[bool] = None
    model_id: Optional[str] = None
    model_max_tokens: Optional[str] = None
    model_temperature: Optional[str] = None
    guardrail_id: Optional[str] = None
    guardrail_version: Optional[str] = None
    system_prompt: Optional[str] = None
    status: Optional[str] = None

class LLMRead(LLMBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class LLMOut(LLMBase):
    id: int

    model_config = {"from_attributes": True}

# ------------------- Agent Schemas -------------------

class AgentBase(BaseModel):
    name: str
    status: str
    trashed: bool
    default_agent: bool
    knowledge_base_id: Optional[str] = None
    llm_id: int
    system_prompt: Optional[str] = None
    tools: Optional[List[Any]] = None  # stored JSON

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    trashed: Optional[bool] = None
    default_agent: Optional[bool] = None
    knowledge_base_id: Optional[str] = None
    llm_id: Optional[int] = None
    system_prompt: Optional[str] = None
    tools: Optional[List[Any]] = None

class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class AgentOut(AgentBase):
    id: int

    model_config = {"from_attributes": True}
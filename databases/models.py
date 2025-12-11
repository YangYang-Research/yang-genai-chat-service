from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from databases.base import Base
from sqlalchemy.types import JSON

class LLMModel(Base):
    __tablename__ = "llms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    name = Column(String(64), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=False, default="yang.png")
    provider = Column(String(64), nullable=True)  # e.g., "aws", "openai", "azure"
    
    # AWS Region
    region = Column(String(64), nullable=False, default="ap-southeast-1")

    # Model
    model_id = Column(String(255), nullable=False)
    model_max_tokens = Column(String(16), nullable=False, default="2048")
    model_temperature = Column(String(8), nullable=False, default="0.7")

    # Guardrails
    guardrail_id = Column(String(255), nullable=True)
    guardrail_version = Column(String(64), nullable=True)
    
    # System prompt
    system_prompt = Column(Text, nullable=True)

    status = Column(String(16), default="enable")
    trashed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agents = relationship("AgentModel", back_populates="llms")

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String(100), nullable=False, unique=True)

    # Knowledge Base
    knowledge_base_id = Column(String(255), nullable=True)

    # LLM id
    llm_id = Column(Integer, ForeignKey("llms.id"))

    # System prompt
    system_prompt = Column(Text, nullable=True)

    # List tools
    tools = Column(JSON, nullable=True)

    status = Column(String(16), default="enable")
    trashed = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    llms = relationship("LLMModel", back_populates="agents")

class ToolModel(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Tool identification
    name = Column(String(64), nullable=False, unique=True)  # e.g., "duckduckgo", "arxiv"
    display_name = Column(String(100), nullable=True)  # e.g., "DuckDuckGo Search"
    status = Column(String(16), default="disable") # "enable" or "disable"
    logo = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # e.g., ["search", "knowledge"]
    trashed = Column(Boolean, default=False) 
    
    # Optional authentication / API credentials
    host = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    cse_id = Column(String(255), nullable=True)
    client_id = Column(String(255), nullable=True)
    client_secret = Column(String(255), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    status = Column(String(16), default="enable")
    trashed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One-to-many relationship — A role can have many users
    users = relationship("UserModel", back_populates="roles")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    fullname = Column(String(100), nullable=True)
    changed_password = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    active_status = Column(String(16), default="enable")
    trashed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    roles = relationship("RoleModel", back_populates="users")
    messages = relationship("MessageModel", back_populates="users")

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(10))  # "user" or "assistant"
    content = Column(Text)
    feedback = Column(Boolean, nullable=True)
    status = Column(String(16), default="enable")
    trashed = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("UserModel", back_populates="messages")

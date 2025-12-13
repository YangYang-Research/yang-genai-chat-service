from pydantic import BaseModel
from typing import List, Optional, Literal, Union, Dict, Any

class ImageSource(BaseModel):
    type: Literal["base64"]
    media_type: str
    data: str

class DocumentSource(BaseModel):
    bytes: Optional[str] = None # base64 string from frontend

class DocumentContent(BaseModel):
    format: str
    name: str
    source: DocumentSource

class ContentBlock(BaseModel):
    type: Optional[Literal["text", "image"]] = None
    text: Optional[str] = None
    source: Optional[ImageSource] = None
    document: Optional[DocumentContent] = None

class ChatAgentMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[ContentBlock]]

class ChatAgentRequest(BaseModel):
    chat_session_id: str
    agent_name: str
    model_name: str
    messages: List[ChatAgentMessage]

class ChatLLMMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[ContentBlock]]

class ChatLLMRequest(BaseModel):
    chat_session_id: str
    model_name: str
    messages: List[ChatLLMMessage]
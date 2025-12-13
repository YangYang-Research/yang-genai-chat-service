from fastapi import Request, APIRouter, Depends, HTTPException
from helpers.authentication import verify_yang_auth_token
from helpers.config import AppConfig
from helpers.datamodel import ChatAgentRequest, ChatLLMRequest
from helpers.utils import Utils
from fastapi.responses import StreamingResponse, JSONResponse
from bedrock.stream import Streaming
import traceback
from helpers.loog import logger

streaming = Streaming()
app_conf = AppConfig()

router = APIRouter(prefix=f"/{app_conf.api_version_web}/chat", tags=["Chats"])

@router.post(f"/agent/completions", dependencies=[Depends(verify_yang_auth_token)])
async def chat_agent_completions(req: ChatAgentRequest, http_req: Request):
    try:
        formatted_messages = Utils.format_agent_messages(req.messages)

        if not formatted_messages:
            return JSONResponse(status_code=400, content={"error": "No messages provided"})

        message_payload = {"messages": formatted_messages}
        
        return StreamingResponse(streaming.agent_astreaming(chat_id=req.chat_session_id, message=message_payload, agent_name=req.agent_name, model_name=req.model_name, stream_mode="messages"), media_type="text/html")

    except Exception as e:
        logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.post(f"/llm/completions", dependencies=[Depends(verify_yang_auth_token)])
async def chat_llm_completions(req: ChatLLMRequest, http_req: Request):
    try:
        formatted_messages = Utils.format_agent_messages(req.messages)

        if not formatted_messages:
            return JSONResponse(status_code=400, content={"error": "No messages provided"})
        
        message_payload = {"messages": formatted_messages}

        return StreamingResponse(streaming.llm_astreaming(chat_id=req.chat_session_id, message=message_payload, model_name=req.model_name), media_type="text/html")

    except Exception as e:
        logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
import uvicorn
import traceback
from fastapi import FastAPI, Request, Depends
from helpers.utils import Utils
from databases.base import Base
from helpers.loog import logger
from bedrock.stream import Streaming
import databases.models as db_models
from contextlib import asynccontextmanager
from helpers.config import AppConfig, AWSConfig, DatabaseConfig
from fastapi.middleware.cors import CORSMiddleware
from helpers.datamodel import ChatAgentRequest, ChatLLMRequest
from fastapi.responses import StreamingResponse, JSONResponse
from databases.database import engine, create_database_if_not_exists
from helpers.authentication import verify_yang_auth_token, verify_user_admin_auth_token
from sqlalchemy.ext.asyncio import async_sessionmaker
from databases.seeds import seed_initial_data

from routers.user import router as user_router
from routers.message import router as message_router
from routers.tools import router as tool_router
from routers.llm import router as llm_router
from routers.agent import router as agent_router

app_conf = AppConfig()
aws_conf = AWSConfig()
db_conf = DatabaseConfig()
streaming = Streaming()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# --- Startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if db_conf.db_enable == "enable":
            try:
                await create_database_if_not_exists()
                async with engine.begin() as conn:
                    await conn.run_sync(db_models.Base.metadata.create_all)
                logger.info("✅ Tables synchronized with models.")

                # --- Seeding initial data ---
                async with SessionLocal() as session:
                    await seed_initial_data(session)
                logger.info("🌱 Database seeding completed successfully.")
            except Exception as e:
                logger.error(f"❌ Database initialization failed: {e}")
        else:
            logger.warning("⚠️ Database initialization skipped.")

        yield  # <-- always yield, even if startup fails

    finally:
        try:
            if db_conf.db_enable == "enable":
                await engine.dispose()
                logger.info("🧹 Database connection closed.")
        except Exception as e:
            logger.error(f"⚠️ Error during shutdown cleanup: {e}")
        
# ------------------- FastAPI App -------------------
app = FastAPI(title=app_conf.app_name, version=app_conf.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(message_router)
app.include_router(tool_router)
app.include_router(llm_router)
app.include_router(agent_router)

# ------------------- API Endpoint -------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(f"/{app_conf.api_version_web}/chat/agent/completions", dependencies=[Depends(verify_yang_auth_token)])
async def chat_agent_completions(req: ChatAgentRequest, http_req: Request):
    try:
        authorization_header = http_req.headers.get("Authorization")
        if not authorization_header:
            return JSONResponse(status_code=401, content={
                "msg": "Missing authorization header"
            })
        
        if Utils.check_api_authentication(authorization_header):

            formatted_messages = Utils.format_agent_messages(req.messages)

            if not formatted_messages:
                return JSONResponse(status_code=400, content={"error": "No messages provided"})

            message_payload = {"messages": formatted_messages}
            
            return StreamingResponse(streaming.agent_astreaming(chat_id=req.chat_session_id, message=message_payload, model_name=req.model_name, stream_mode="messages"), media_type="text/html")
        else:
            return JSONResponse(status_code=403, content={
                "msg": "Invalid credential",
            })
    except Exception as e:
        logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post(f"/{app_conf.api_version_web}/chat/llm/completions", dependencies=[Depends(verify_yang_auth_token)])
async def chat_llm_completions(req: ChatLLMRequest, http_req: Request):
    try:
        authorization_header = http_req.headers.get("Authorization")
        if not authorization_header:
            return JSONResponse(status_code=401, content={
                "msg": "Missing authorization header"
            })
        
        if Utils.check_api_authentication(authorization_header):
            formatted_messages = Utils.format_agent_messages(req.messages)

            if not formatted_messages:
                return JSONResponse(status_code=400, content={"error": "No messages provided"})
            
            message_payload = {"messages": formatted_messages}

            return StreamingResponse(streaming.llm_astreaming(chat_id=req.chat_session_id, message=message_payload, model_name=req.model_name), media_type="text/html")
        else:
            return JSONResponse(status_code=403, content={
                "msg": "Invalid credential",
            })
    except Exception as e:
        logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

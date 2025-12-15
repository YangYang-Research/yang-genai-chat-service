import uvicorn
import traceback
from fastapi import FastAPI
from helpers.loog import logger
from bedrock.stream import Streaming
import databases.models as db_models
from contextlib import asynccontextmanager
from helpers.config import AppConfig, AWSConfig, DatabaseConfig
from fastapi.middleware.cors import CORSMiddleware
from databases.database import engine, create_database_if_not_exists
from sqlalchemy.ext.asyncio import async_sessionmaker
from databases.seeds import seed_initial_data

from routers.user import router as user_router
from routers.role import router as role_router
from routers.message import router as message_router
from routers.tool import router as tool_router
from routers.llm import router as llm_router
from routers.agent import router as agent_router
from routers.login import router as login_router
from routers.chat import router as chat_router
from routers.tag import router as tag_router

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
            logger.error(f"⚠️ Error during shutdown cleanup: {e} \n TRACEBACK: ", traceback.format_exc())
        
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
app.include_router(role_router)
app.include_router(message_router)
app.include_router(tool_router)
app.include_router(llm_router)
app.include_router(agent_router)
app.include_router(login_router)
app.include_router(chat_router)
app.include_router(tag_router)

# ------------------- API Endpoint -------------------
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

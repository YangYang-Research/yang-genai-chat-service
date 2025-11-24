from sqlalchemy import text
from helpers.loog import logger
from urllib.parse import urlparse
from sqlalchemy.orm import sessionmaker
from helpers.config import DatabaseConfig
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from helpers.secret import AWSSecretManager
from contextlib import asynccontextmanager

db_conf = DatabaseConfig()
aws_secret_manager = AWSSecretManager()

db_username = aws_secret_manager.get_secret(db_conf.db_username_key)
db_pwd = aws_secret_manager.get_secret(db_conf.db_pwd_key)

DATABASE_URL = f"postgresql+asyncpg://{db_username}:{db_pwd}@{db_conf.db_host}:{db_conf.db_port}/{db_conf.db_name}"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def create_database_if_not_exists():
    """
    Connects to the default 'postgres' DB and creates the target database if missing.
    Works for PostgreSQL only.
    """
    url = urlparse(DATABASE_URL)
    db_name = url.path.lstrip("/")
    db_user = url.username
    db_pass = url.password
    db_host = url.hostname
    db_port = url.port or 5432

    default_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/postgres"
    default_engine = create_async_engine(default_url, isolation_level="AUTOCOMMIT")

    async with default_engine.begin() as conn:
        # Check if the database already exists
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": db_name}
        )
        exists = result.scalar() is not None

        if not exists:
            logger.info(f"🆕 Creating database '{db_name}'...")
            await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            logger.info("✅ Database initialized.")
        else:
            logger.info(f"✅ Database '{db_name}' already exists.")

    await default_engine.dispose()
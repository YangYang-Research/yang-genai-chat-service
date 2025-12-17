from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

@dataclass
class AppConfig(object):
    """Base configuration class."""
    
    app_name: str = os.getenv("APP_NAME", "Yang GenAI Chat Service")
    app_version: str = os.getenv("APP_VERSION", "0.0.0")
    api_version_web: str = "v1"
    api_version_mobile: str = "v2"
    api_auth_key_name: str = os.getenv("API_AUTH_KEY_NAME", "")
    app_jwt_secret_key: str = os.getenv("APP_JWT_SECRET_KEY", "")
    app_admin_email: str =  os.getenv("APP_ADMIN_EMAIL", "administrator@yang.app")

@dataclass
class AWSConfig(object):
    """AWS configuration class."""

    aws_region: str = os.getenv("AWS_REGION", "ap-southeast-1")
    
    aws_secret_name: str = os.getenv("AWS_SECRET_NAME", "")


@dataclass
class DatabaseConfig(object):
    """Database configuration class."""

    db_name: str = os.getenv("DB_NAME", "yang_genai_db")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_username_key: str = os.getenv("DB_USERNAME_KEY", "")
    db_pwd_key: str = os.getenv("DB_PWD_KEY", "")

@dataclass
class LogConfig(object):
    """Logging configuration class."""

    log_max_size: str = os.getenv("LOG_MAX_SIZE", "10485760")  # 10 MB
    log_max_backups: str = os.getenv("LOG_MAX_BACKUPS", "5")    # 5 backup files
import jwt
from fastapi import Header, HTTPException, status
from helpers.secret import AWSSecretManager
from helpers.config import AppConfig
from passlib.context import CryptContext

app_conf = AppConfig()
aws_secret_manager = AWSSecretManager()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def verify_user_admin_auth_token(authorization: str = Header(None)):
    """
    Validate Bearer token from Authorization header.
    Raises HTTPException on failure.
    """

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        scheme, credential = authorization.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Authorization format",
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization must start with Bearer",
        )

    # Load secret from AWS Secrets Manager
    jwt_secret = aws_secret_manager.get_secret(app_conf.app_jwt_secret_key)

    try:
        decoded = jwt.decode(credential, jwt_secret, algorithms=["HS256"])
        return decoded  # you can return user_id, roles, etc.
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

async def verify_yang_auth_token(
    x_yang_auth: str = Header(None, alias="x-yang-auth")
):
    """
    Validate Yang Bacsic authentication via the 'x-yang-auth' header.
    Raises HTTPException on failure.
    """

    if x_yang_auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-yang-auth header",
        )

    try:
        scheme, credential = x_yang_auth.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Authorization format",
        )

    if scheme.lower() != "basic":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization must start with Basic",
        )
    
    # Load secret from AWS Secrets Manager
    api_credential = aws_secret_manager.get_secret(app_conf.api_auth_key_name)

    if credential != api_credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
        )

    return True

def verify_user_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_jwt_token(payload: dict, expires_delta: int = None):
    to_encode = payload.copy()
    jwt_secret = aws_secret_manager.get_secret(app_conf.app_jwt_secret_key)

    if expires_delta:
        to_encode.update({"exp": expires_delta})

    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm="HS256")
    return encoded_jwt
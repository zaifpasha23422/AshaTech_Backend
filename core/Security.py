from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from core.Config import settings
from jose import jwt
from pydantic import UUID4

JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes = ["argon2"], deprecated = "auto")

def get_password_hash(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password:str, hash_password:str):
    return pwd_context.verify(plain_password, hash_password)



def create_access_token(data: dict, expires_delta:Optional[timedelta]= None):
    to_encode = data.copy()
    now = datetime.now(tz =timezone.utc)
    expire = now + (expires_delta or timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=JWT_ALGORITHM)
    return token


def loginTokens(uuid :UUID4) ->dict:
    access_token_expires = timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days = settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": str(uuid), "type":"access"},expires_delta =access_token_expires
    )
    refresh_token = create_access_token(
        data = {"sub": str(uuid),"type":"refresh"}, expires_delta = refresh_token_expires
    )
    return {
        "access_token" : access_token,
        "refresh_token" : refresh_token,
        "token_type": "bearer"
    }
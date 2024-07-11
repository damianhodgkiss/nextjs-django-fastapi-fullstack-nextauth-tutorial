from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Any, Annotated
from .models import User


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
ACCESS_TOKEN_VALID_MINUTES = 1

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_exception
    try:
        return credentials.credentials
    except JWTError:
        raise credentials_exception


async def get_token_payload(
    token: Annotated[str, Depends(get_access_token)]
) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str | None = payload.get("sub")
        if id is None:
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception


async def get_current_user(
    payload: Annotated[dict[str, Any], Depends(get_token_payload)]
) -> User:
    try:
        id: str | None = payload.get("sub")
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_model().objects.filter(id=id, is_active=True).afirst()
    if user is None:
        raise credentials_exception
    return user


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(optional_security)]
) -> User | None:
    if not credentials:
        return None
    try:
        payload = await get_token_payload(credentials.credentials)
        return await get_current_user(payload)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

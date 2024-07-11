from fastapi import FastAPI, APIRouter, Depends
from django.contrib.auth import authenticate
from typing import Annotated, Any
from datetime import timedelta
from .schemas import LoginRequest, Token
from datetime import datetime
from .utils import (
    create_access_token,
    get_access_token,
    get_token_payload,
    get_current_active_user,
    credentials_exception,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ACCESS_TOKEN_VALID_MINUTES,
)
from .models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login/")
def login(login: LoginRequest):
    user = authenticate(email=login.username, password=login.password)
    if not user:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="Bearer", user=user)


@router.post("/session/")
async def check_session(
    token: Annotated[str, Depends(get_access_token)],
    payload: Annotated[dict[str, Any], Depends(get_token_payload)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Token:
    exp_time = datetime.fromtimestamp(payload["exp"])
    current_time = datetime.now()
    time_difference = exp_time - current_time
    difference_in_minutes = time_difference.total_seconds() / 60

    # if the token is still valid, return the same token
    if difference_in_minutes >= ACCESS_TOKEN_VALID_MINUTES:
        return Token(access_token=token, token_type="Bearer", user=current_user)

    # return a new rolled access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", user=current_user)


def register_routers(app: FastAPI):
    app.include_router(router)

from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    is_staff: bool
    is_active: bool
    is_superuser: bool
    last_login: datetime | None
    date_joined: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema

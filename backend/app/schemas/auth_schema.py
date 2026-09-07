from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class UserRegister(BaseModel):
    email:     EmailStr
    password:  str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    email:        str
    full_name:    Optional[str]
    is_active:    bool
    is_superuser: bool


class UserOrgsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:   int
    name: str
    role: str

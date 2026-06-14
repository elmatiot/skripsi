from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterIn(BaseModel):
    email: EmailStr
    nama: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    nama: str


class UpdateProfileIn(BaseModel):
    nama: Optional[str] = Field(default=None, min_length=2, max_length=255)


TokenOut.model_rebuild()

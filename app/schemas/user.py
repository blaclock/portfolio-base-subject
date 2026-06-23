from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 20:
            raise ValueError("ユーザ名は3〜20文字で入力してください")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("ユーザ名は英数字とアンダースコアのみ使用できます")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上で入力してください")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 50:
            raise ValueError("表示名は50文字以内で入力してください")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None

    model_config = {"from_attributes": True}


class UserDetailResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    followers_count: int
    following_count: int
    is_following: bool


class AuthResponse(BaseModel):
    token: str
    user: UserResponse

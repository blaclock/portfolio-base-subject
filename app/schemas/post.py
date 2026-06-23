from datetime import datetime

from pydantic import BaseModel, field_validator


class PostCreateRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v) == 0:
            raise ValueError("投稿内容を入力してください")
        if len(v) > 280:
            raise ValueError("投稿は280文字以内で入力してください")
        return v


class PostUpdateRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v) == 0:
            raise ValueError("投稿内容を入力してください")
        if len(v) > 280:
            raise ValueError("投稿は280文字以内で入力してください")
        return v


class PostResponse(BaseModel):
    id: int
    user_id: int
    content: str
    username: str
    display_name: str | None
    like_count: int
    is_liked: bool
    created_at: datetime
    updated_at: datetime

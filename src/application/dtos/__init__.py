"""Data Transfer Objects for the application layer."""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    bio: str = Field(default="", max_length=500)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── User ──────────────────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    bio: str
    avatar_url: Optional[str]
    is_active: bool
    follower_count: int
    following_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


# ── Post ──────────────────────────────────────────────────────────────────────


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)
    parent_id: Optional[UUID] = None


class PostResponse(BaseModel):
    id: UUID
    author_id: UUID
    author_username: str
    content: str
    status: str
    like_count: int
    is_liked_by_me: bool = False
    is_reply: bool
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EditPostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)


# ── Pagination ─────────────────────────────────────────────────────────────────


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int

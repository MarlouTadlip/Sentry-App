"""Loved one schema."""

from datetime import datetime

from ninja import Schema

from .user_schema import UserSchema


class LovedOneSchema(Schema):
    """Loved one relationship schema."""

    id: int
    user_id: int
    loved_one: UserSchema
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LovedOneListResponse(Schema):
    """Loved one list response schema."""

    message: str
    loved_ones: list[LovedOneSchema]
    count: int

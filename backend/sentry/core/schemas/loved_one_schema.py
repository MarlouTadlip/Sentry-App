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
    is_alerted: bool
    created_at: datetime
    updated_at: datetime


class AddLovedOneRequest(Schema):
    """Request schema for adding a loved one."""

    loved_one_email: str
    is_alerted: bool = True


class UpdateLovedOneRequest(Schema):
    """Request schema for updating loved one settings."""

    is_alerted: bool | None = None
    is_active: bool | None = None


class LovedOneResponse(Schema):
    """Response schema for loved one operations."""

    message: str
    loved_one: LovedOneSchema | None = None


class LovedOneListResponse(Schema):
    """Loved one list response schema."""

    message: str
    loved_ones: list[LovedOneSchema]
    count: int

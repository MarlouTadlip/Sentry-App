"""User schema."""

from datetime import datetime

from django.contrib.auth import get_user_model
from ninja import Schema

User = get_user_model()


class UserSchema(Schema):
    """User schema."""

    id: int
    username: str
    first_name: str
    middle_name: str
    last_name: str
    email: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    last_login: datetime | None = None
    date_joined: datetime


class UserUpdateRequest(Schema):
    """User update request schema."""

    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    email: str | None = None

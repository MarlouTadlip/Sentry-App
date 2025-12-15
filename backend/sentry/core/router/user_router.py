"""User router."""

from django.http import HttpRequest
from ninja import Router

from core.auth.jwt import JwtAuth
from core.controllers.core_controller import update_user_info
from core.schemas import UserSchema, UserUpdateRequest

user_router = Router(tags=["user"])


@user_router.put("/me", auth=JwtAuth)
def update_user_endpoint(
    request: HttpRequest,  # noqa: ARG001
    user: UserSchema,
    data: UserUpdateRequest,
) -> UserSchema:
    """Update current user information endpoint."""
    return update_user_info(user, data)

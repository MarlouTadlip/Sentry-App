"""User router."""

from typing import Any

from django.http import HttpRequest
from ninja import File, Router
from ninja.files import UploadedFile

from core.auth.jwt import JwtAuth
from core.controllers.user_controller import (
    get_user_info,
    search_users,
    update_user_info,
    update_user_profile_picture,
)
from core.controllers.user_settings_controller import (
    get_user_settings,
    update_user_settings,
)
from core.schemas import UserUpdateRequest, UserSettingsUpdateRequest

user_router = Router(tags=["user"])


@user_router.get("/me/info", auth=JwtAuth())
def user_info_endpoint(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get current user information endpoint."""
    return get_user_info(request)


@user_router.put("/me/update", auth=JwtAuth())
def update_user_endpoint(
    request: HttpRequest,
    data: UserUpdateRequest,
) -> dict[str, Any]:
    """Update current user's information endpoint."""
    return update_user_info(request, data)


@user_router.put("/me/profile-picture/update", auth=JwtAuth())
def update_profile_picture_endpoint(
    request: HttpRequest,
    profile_picture: File[UploadedFile],
) -> dict[str, Any]:
    """Update current user's profile picture endpoint."""
    return update_user_profile_picture(request, profile_picture)


@user_router.get("/settings", auth=JwtAuth())
def get_user_settings_endpoint(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get user settings endpoint."""
    return get_user_settings(request)


@user_router.put("/settings", auth=JwtAuth())
def update_user_settings_endpoint(
    request: HttpRequest,
    data: UserSettingsUpdateRequest,
) -> dict[str, Any]:
    """Update user settings endpoint."""
    return update_user_settings(request, data.model_dump())


@user_router.get("/search", auth=JwtAuth())
def search_users_endpoint(
    request: HttpRequest,
    q: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for users by email, username, first name, or last name.

    Args:
        request: The HTTP request object
        q: Search query string
        limit: Maximum number of results (default: 10, max: 50)

    Returns:
        Dictionary containing list of matching users and count

    """
    return search_users(request, q, limit)

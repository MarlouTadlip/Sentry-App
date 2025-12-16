"""Loved one router."""

from typing import Any

from django.http import HttpRequest
from ninja import Router

from core.auth.jwt import JwtAuth
from core.controllers.loved_one_controller import get_user_loved_ones

loved_one_router = Router(tags=["loved_one"])


@loved_one_router.get("/me", auth=JwtAuth())
def get_loved_ones_endpoint(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get current user's loved ones endpoint."""
    return get_user_loved_ones(request)


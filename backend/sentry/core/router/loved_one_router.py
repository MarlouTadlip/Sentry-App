"""Loved one router."""

from typing import Any

from django.http import HttpRequest
from ninja import Router

from core.auth.jwt import JwtAuth
from core.controllers.loved_one_controller import (
    add_loved_one,
    delete_loved_one,
    get_user_loved_ones,
    toggle_loved_one_alerted,
    update_loved_one,
)
from core.schemas import AddLovedOneRequest, UpdateLovedOneRequest

loved_one_router = Router(tags=["loved_one"])


@loved_one_router.get("/me", auth=JwtAuth())
def get_loved_ones_endpoint(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get current user's loved ones endpoint."""
    return get_user_loved_ones(request)


@loved_one_router.post("/", auth=JwtAuth())
def add_loved_one_endpoint(
    request: HttpRequest,
    data: AddLovedOneRequest,
) -> dict[str, Any]:
    """Add a loved one contact endpoint."""
    return add_loved_one(request, data)


@loved_one_router.delete("/{loved_one_id}", auth=JwtAuth())
def delete_loved_one_endpoint(
    request: HttpRequest,
    loved_one_id: int,
) -> dict[str, Any]:
    """Delete a loved one relationship endpoint."""
    return delete_loved_one(request, loved_one_id)


@loved_one_router.patch("/{loved_one_id}", auth=JwtAuth())
def update_loved_one_endpoint(
    request: HttpRequest,
    loved_one_id: int,
    data: UpdateLovedOneRequest,
) -> dict[str, Any]:
    """Update loved one settings (is_alerted, is_active) endpoint."""
    return update_loved_one(request, loved_one_id, data)


@loved_one_router.post("/{loved_one_id}/toggle-alerted", auth=JwtAuth())
def toggle_loved_one_alerted_endpoint(
    request: HttpRequest,
    loved_one_id: int,
) -> dict[str, Any]:
    """Toggle is_alerted status for a loved one endpoint."""
    return toggle_loved_one_alerted(request, loved_one_id)


"""Core router."""

from ninja import Router

from .auth_router import auth_router
from .user_router import user_router

core_router = Router(tags=["core"])

core_router.add_router("auth", auth_router)
core_router.add_router("user", user_router)

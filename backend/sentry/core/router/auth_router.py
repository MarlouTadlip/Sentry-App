"""Auth router."""

from django.http import HttpRequest
from ninja import Router

from core.auth.jwt import JwtAuth
from core.controllers.auth_controller import get_current_user, login, refresh_token, register
from core.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UserSchema,
)

auth_router = Router(tags=["auth"])


@auth_router.post("/login")
def login_endpoint(
    request: HttpRequest,
    credentials: LoginRequest,
) -> LoginResponse:
    """Login endpoint wrapper."""
    return login(request, credentials)


@auth_router.post("/register")
def register_endpoint(
    request: HttpRequest,
    data: RegisterRequest,
) -> LoginResponse:
    """Register endpoint wrapper."""
    return register(request, data)


@auth_router.post("/refresh")
def refresh_token_endpoint(
    request: HttpRequest,
    data: RefreshTokenRequest,
) -> LoginResponse:
    """Refresh token endpoint wrapper."""
    return refresh_token(request, data)


@auth_router.get("/current", auth=JwtAuth())
def current_user_endpoint(
    request: HttpRequest,
    user: UserSchema,
) -> UserSchema:
    """Get current authenticated user endpoint."""
    return get_current_user(user)

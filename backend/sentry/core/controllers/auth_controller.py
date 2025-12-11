"""Auth router controller."""

from common.constants.messages import AuthMessages
from common.exceptions.core import BaseAuthError, BaseValidationError
from django.contrib.auth import authenticate
from django.http import HttpRequest

from core.auth.jwt import create_token_pair
from core.schemas import LoginRequest, LoginResponse, UserSchema


def login(
    request: HttpRequest,
    credentials: LoginRequest,
) -> LoginResponse:
    """Login controller.

    Args:
        request (HttpRequest): The request object
        credentials (LoginRequest): The credentials of the user to login

    Returns:
        A dictionary containing the access token and refresh token

    """
    identifier = credentials.username or credentials.email

    if not identifier:
        raise BaseValidationError(message=AuthMessages.Login.EITHER_CREDS)

    user = authenticate(request, username=identifier, password=credentials.password)

    if not user:
        raise BaseAuthError(message=AuthMessages.Login.WRONG_CREDS)

    if not user.is_active:
        raise BaseAuthError(message=AuthMessages.Login.INACTIVE_USER)

    user_schema = UserSchema.model_validate(user)
    tokens = create_token_pair(user_schema)
    return LoginResponse(**tokens)

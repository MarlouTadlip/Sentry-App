"""Authentication utilities."""

from datetime import UTC, datetime

from common.constants.messages import AuthMessages
from django.http import HttpRequest
from jose import JWTError
from ninja.errors import AuthenticationError, HttpError

from core.auth.jwt import decode_jwt_token


def validate_access_token(access_token_str: str) -> None:
    """Validate access token and check if it's expired.

    Args:
        access_token_str: The access token string

    Raises:
        HttpError: If access token is not expired (400)
        AuthenticationError: If access token is invalid

    """
    try:
        access_payload = decode_jwt_token(access_token_str)
        # Check if access token type is correct
        if access_payload.get("type") != "access":
            raise AuthenticationError(
                message=AuthMessages.JwtAuth.INVALID_TOKEN,
            )

        # Check if access token is expired
        exp = access_payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=UTC)
            if exp_datetime > datetime.now(UTC):
                # Access token is NOT expired - return bad request
                raise HttpError(
                    status_code=400,
                    message="Access token is not expired. No need to refresh.",
                )
    except JWTError:
        # Access token is expired or invalid - this is expected, continue
        pass


def get_access_token_from_header(request: HttpRequest) -> str | None:
    """Extract access token from Authorization header.

    Args:
        request: The HTTP request object

    Returns:
        Access token string if present, None otherwise

    """
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    return None

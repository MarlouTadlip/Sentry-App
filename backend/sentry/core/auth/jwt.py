"""JWT authentication."""

from datetime import UTC, datetime, timedelta

from common.constants.messages import AuthMessages, EnvMessages
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from jose import JWTError, jwt
from ninja.errors import AuthenticationError
from ninja.security import HttpBearer
from sentry.settings.config import settings

from core.schemas import UserSchema

User = get_user_model()


class JwtAuth(HttpBearer):
    """JWT authentication."""

    def authenticate(self, request: HttpRequest, token: str) -> UserSchema | None:  # noqa: ARG002
        """Authenticate the user."""
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get("sub")
            user = User.objects.get(id=user_id)

            if not user.is_active:
                raise AuthenticationError(
                    message=AuthMessages.JwtAuth.INACTIVE_USER,
                )

            return UserSchema.model_validate(user)
        except User.DoesNotExist as e:
            raise AuthenticationError(
                message=AuthMessages.JwtAuth.USER_NOT_FOUND,
            ) from e
        except JWTError as e:
            raise AuthenticationError(
                message=AuthMessages.JwtAuth.INVALID_TOKEN,
            ) from e


def decode_jwt_token(token: str) -> dict:
    """Decode the JWT token."""
    # jwt.decode returns a dictionary of the payload
    try:
        decoded_jwt = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as e:
        raise AuthenticationError(
            message=AuthMessages.JwtAuth.INVALID_TOKEN,
        ) from e

    return decoded_jwt


def create_access_token(data: dict, expires_in_mins: timedelta) -> str:
    """Create an access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_in_mins
    to_encode.update({"exp": expire, "type": "access"})
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except JWTError as e:
        raise AuthenticationError(
            message=AuthMessages.JwtAuth.INVALID_TOKEN,
        ) from e
    return encoded_jwt


def create_refresh_token(data: dict, expires_in_mins: timedelta) -> str:
    """Create a refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_in_mins
    to_encode.update({"exp": expire, "type": "refresh"})
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    except JWTError as e:
        raise AuthenticationError(
            message=AuthMessages.JwtAuth.INVALID_TOKEN,
        ) from e
    return encoded_jwt


def create_access_token_from_refresh_token(refresh_token_payload: dict) -> str:
    """Create a new access token from refresh token payload.

    Args:
        refresh_token_payload: Decoded refresh token payload

    Returns:
        New access token string

    """
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_in_mins)
    if not access_token_expires:
        raise ValueError(EnvMessages.Jwt.MISSING_ENV_ACCESS_TOKEN_EXPIRE_IN_MINS)

    return create_access_token(
        data={"sub": refresh_token_payload.get("sub"), "username": refresh_token_payload.get("username")},
        expires_in_mins=access_token_expires,
    )


def create_token_pair(user: UserSchema) -> dict[str, str]:
    """Create a token pair."""
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_in_mins)
    if not access_token_expires:
        raise ValueError(EnvMessages.Jwt.MISSING_ENV_ACCESS_TOKEN_EXPIRE_IN_MINS)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_in_mins=access_token_expires,
    )

    refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_in_days)
    if not refresh_token_expires:
        raise ValueError(EnvMessages.Jwt.MISSING_ENV_REFRESH_TOKEN_EXPIRE_IN_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.id, "username": user.username},
        expires_in_mins=refresh_token_expires * 24,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }

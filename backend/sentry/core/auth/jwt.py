"""JWT authentication."""

from datetime import UTC, datetime, timedelta

from common.constants.messages import EnvMessages
from common.exceptions.core import (
    InactiveUserError,
    InvalidTokenError,
    UserNotFoundError,
)
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from jose import JWTError, jwt
from ninja.security import HttpBearer
from sentry.settings.config import settings

from core.schemas import UserSchema

User = get_user_model()


class JwtAuth(HttpBearer):
    """JWT authentication."""

    def jwt_authenticate(self, _request: HttpRequest, token: str) -> UserSchema | None:
        """Authenticate the user."""
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidTokenError

            user = User.objects.get(id=user_id)
            if not user.is_active:
                raise InactiveUserError

            # Convert django object to a pydantic model
            return UserSchema.model_validate(user)

        except User.DoesNotExist as ue:
            raise UserNotFoundError from ue
        except JWTError as e:
            raise InvalidTokenError from e


def decode_jwt_token(token: str) -> dict:
    """Decode the JWT token."""
    # jwt.decode returns a dictionary of the payload
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def create_access_token(data: dict, expires_in_mins: timedelta) -> str:
    """Create an access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_in_mins
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(data: dict, expires_in_mins: timedelta) -> str:
    """Create a refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_in_mins
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
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

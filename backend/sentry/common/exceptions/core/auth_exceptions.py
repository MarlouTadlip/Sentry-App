"""Authentication exceptions."""

from common.exceptions.core.base_exceptions import BaseAuthError


class InvalidTokenError(BaseAuthError):
    """Raised when JWT token is invalid."""

    default_message = "Invalid or expired token"
    default_code = 401


class MissingTokenError(BaseAuthError):
    """Raised when JWT token is missing from request."""

    default_message = "Authentication token is required"
    default_code = 401


class ExpiredTokenError(BaseAuthError):
    """Raised when JWT token has expired."""

    default_message = "Token has expired"
    default_code = 401

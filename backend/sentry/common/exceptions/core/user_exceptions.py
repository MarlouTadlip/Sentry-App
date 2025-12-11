"""User exceptions."""

from common.exceptions.core.base_exceptions import BaseAuthError, BaseNotFoundError


class UserNotFoundError(BaseNotFoundError):
    """Raised when user is not found."""

    default_message = "User not found"
    default_code = 404


class InactiveUserError(BaseAuthError):
    """Raised when user account is inactive."""

    default_message = "User account is inactive"
    default_code = 403

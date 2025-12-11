"""Base exceptions for custom exceptions."""

from typing import Any, ClassVar

from ninja.errors import AuthenticationError, HttpError, ValidationError


class BaseAuthError(AuthenticationError):
    """Base class for authentication errors."""

    default_message: str = "Authentication failed"
    default_code: int = 401
    default_details: dict[str, str] | None = None

    def __init__(
        self,
        code: int | None = None,
        message: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize authentication error.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional details about the error

        """
        self.message = message or self.default_message
        self.status_code = code or self.default_code
        self.details = details or self.default_details
        super().__init__(self.status_code, self.message)

    def __str__(self) -> str:  # noqa: D105
        return self.message


class BaseNotFoundError(HttpError):
    """Base class for not found errors."""

    default_message: str = "Not found"
    default_code: int = 404
    default_details: dict[str, str] | None = None

    def __init__(
        self,
        code: int | None = None,
        message: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize a not found error.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional details about the error

        """
        self.message = message or self.default_message
        self.status_code = code or self.default_code
        self.details = details or self.default_details
        super().__init__(self.status_code, self.message)

    def __str__(self) -> str:  # noqa: D105
        return self.message


class BaseValidationError(ValidationError):
    """Base class for validation errors."""

    default_message: str = "Validation failed"
    default_code: int = 400
    default_details: ClassVar[list[dict[str, Any]]] = [
        {
            "field": "root",
            "message": "Validation failed",
        },
    ]

    def __init__(
        self,
        code: int | None = None,
        message: str | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize a validation error.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
            details: Additional details about the error

        """
        self.message = message or self.default_message
        self.status_code = code or self.default_code
        self.details = details or self.default_details
        super().__init__(self.details)

    def __str__(self) -> str:  # noqa: D105
        return self.message

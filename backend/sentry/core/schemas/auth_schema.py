"""Authentication schemas."""

from ninja import Schema


class LoginRequest(Schema):
    """Login request schema."""

    username: str | None = None
    email: str | None = None
    password: str


class RegisterRequest(Schema):
    """Register request schema."""

    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    middle_name: str | None = ""


class LoginResponse(Schema):
    """Login response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    message: str


class RefreshTokenRequest(Schema):
    """Refresh token request schema."""

    refresh_token: str


class EmailVerificationRequest(Schema):
    """Email verification request schema."""

    email: str


class VerifyEmailRequest(Schema):
    """Verify email request schema."""

    token: str


class ForgotPasswordRequest(Schema):
    """Forgot password request schema."""

    email: str


class ResetPasswordRequest(Schema):
    """Reset password request schema."""

    token: str
    new_password: str


class MessageResponse(Schema):
    """Generic message response schema."""

    message: str


class IsUserVerifiedResponse(Schema):
    """Is user verified response schema."""

    is_verified: bool
    message: str

"""Environment messages."""

from typing import Final


class EnvMessages:
    """Environment messages."""

    class Jwt:
        """JWT environment messages."""

        MISSING_ENV_ACCESS_TOKEN_EXPIRE_IN_MINS: Final[str] = (
            "Missing environment variable: JWT_ACCESS_TOKEN_EXPIRE_IN_MINS"  # noqa: S105
        )
        MISSING_ENV_REFRESH_TOKEN_EXPIRE_IN_DAYS: Final[str] = (
            "Missing environment variable: JWT_REFRESH_TOKEN_EXPIRE_IN_DAYS"  # noqa: S105
        )

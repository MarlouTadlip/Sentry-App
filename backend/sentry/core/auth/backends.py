"""Customized authentication backends."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from core.schemas import UserSchema

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """Customized authentication backend that allows users to login with email or username."""

    def authenticate(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> UserSchema | None:
        """Authenticate the user by email or username."""
        try:
            user = User.objects.get(Q(username=username) | Q(email=email))
        except User.DoesNotExist:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

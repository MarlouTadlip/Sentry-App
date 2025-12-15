"""Core controller."""

from common.constants.messages import AuthMessages
from django.contrib.auth import get_user_model
from django.db.models import Q
from ninja.errors import ValidationError

from core.schemas import UserSchema, UserUpdateRequest

User = get_user_model()


def update_user_info(
    user: UserSchema,
    data: UserUpdateRequest,
) -> UserSchema:
    """Update user information.

    Args:
        user: The authenticated user from JWT token (injected by Django Ninja)
        data: The user update data

    Returns:
        Updated UserSchema

    Raises:
        ValidationError: If email already exists

    """
    # Get the user instance from database
    user_instance = User.objects.get(id=user.id)

    # Check if email is being updated and if it already exists
    if data.email and data.email != user.email and User.objects.filter(Q(email=data.email) & ~Q(id=user.id)).exists():
        raise ValidationError(
            errors=[
                {
                    "field": "email",
                    "message": AuthMessages.Register.USER_EXISTS,
                },
            ],
        )

    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user_instance, field, value)

    user_instance.save()

    return UserSchema.model_validate(user_instance)

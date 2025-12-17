"""Core controller."""

import contextlib
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.http import HttpRequest

from core.schemas import UserSchema, UserUpdateRequest

User = get_user_model()


def update_user_info(
    request: HttpRequest,
    data: UserUpdateRequest,
) -> dict[str, Any]:
    """Update user information.

    Args:
        request: The HTTP request object
        data: The user update data

    Returns:
        Dictionary containing the success/error message

    Raises:
        ValidationError: If email already exists

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]

    # Update fields if provided - use update() for efficiency
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    if update_data:
        User.objects.filter(id=user_id).update(**update_data)

    return {
        "message": "User information updated successfully",
    }


def update_user_profile_picture(
    request: HttpRequest,
    profile_picture: UploadedFile,
) -> dict[str, Any]:
    """Update user profile picture.

    Args:
        request: The HTTP request object
        profile_picture: The profile picture file to upload

    Returns:
        Dictionary containing the success/error message

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]

    # Get the ImageField's storage and upload_to path
    profile_picture_field = User._meta.get_field("profile_picture")  # noqa: SLF001
    storage = profile_picture_field.storage
    upload_to = profile_picture_field.upload_to  # "user/images/profile_pictures/"

    # Wrap everything in an atomic transaction
    with transaction.atomic():  # type: ignore[call-overload]
        # Fetch only the profile_picture field value (efficient - minimal query)
        user_data = User.objects.filter(id=user_id).values("profile_picture").first()
        current_picture_path = user_data.get("profile_picture") if user_data else None

        # Delete old picture if it exists
        if current_picture_path:
            with contextlib.suppress(Exception):
                storage.delete(str(current_picture_path))

        # Generate the file path Django would use
        # upload_to is a static string, not a callable
        file_path = f"{upload_to}{profile_picture.name}"

        # Ensure unique filename if needed
        filename = storage.get_available_name(file_path, None)

        # Save the new file using Django's storage
        saved_path = storage.save(filename, profile_picture)

        # Update only the profile_picture field in the database (bulk update, no instance fetch!)
        User.objects.filter(id=user_id).update(profile_picture=saved_path)

    return {
        "message": "Profile picture updated successfully",
    }


def get_user_info(request: HttpRequest) -> dict[str, Any]:
    """Get current user information.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)

    Returns:
        Dictionary containing the current user information

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]

    # Fetch fresh user object from database
    user = User.objects.get(id=user_id)

    # Convert to UserSchema and return as dict
    user_schema = UserSchema.model_validate(user)
    return {
        "message": "User information fetched successfully",
        "user": user_schema.model_dump(),
    }


def search_users(
    request: HttpRequest,
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for users by email, username, first name, or last name.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)
        query: Search query string (searches email, username, first_name, last_name)
        limit: Maximum number of results to return (default: 10, max: 50)

    Returns:
        Dictionary containing list of matching users and count

    """
    from django.db.models import Q  # noqa: PLC0415

    current_user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]

    # Limit the search results
    limit = min(max(limit, 1), 50)  # Between 1 and 50

    # If query is empty or too short, return empty results
    if not query or len(query.strip()) < 2:
        return {
            "users": [],
            "count": 0,
        }

    # Search across email, username, first_name, and last_name
    # Exclude the current user from results
    search_query = Q(
        Q(email__icontains=query)
        | Q(username__icontains=query)
        | Q(first_name__icontains=query)
        | Q(last_name__icontains=query),
    ) & ~Q(id=current_user_id)  # Exclude current user

    # Fetch matching users (only active users)
    users_queryset = (
        User.objects.filter(search_query, is_active=True)  # pyright: ignore[reportAttributeAccessIssue]
        .order_by("email")[:limit]
    )

    # Convert to schemas
    user_schemas = [UserSchema.model_validate(user) for user in users_queryset]

    return {
        "users": [user.model_dump() for user in user_schemas],
        "count": len(user_schemas),
    }
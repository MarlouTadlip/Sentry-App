"""Loved one controller."""

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from ninja.errors import HttpError, ValidationError

from core.models import LovedOne
from core.schemas import (
    AddLovedOneRequest,
    LovedOneListResponse,
    LovedOneResponse,
    LovedOneSchema,
    UpdateLovedOneRequest,
    UserSchema,
)

User = get_user_model()
logger = logging.getLogger("core")


def get_user_loved_ones(
    request: HttpRequest,
) -> dict[str, Any]:
    """Get all loved ones for the current user.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)

    Returns:
        Dictionary containing the list of loved ones and count

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]

    # Use select_related to prevent N+1 queries when accessing loved_one user fields
    # This fetches the related User objects in a single query
    loved_ones_queryset = (
        LovedOne.objects.filter(user_id=user_id, is_active=True)  # pyright: ignore[reportAttributeAccessIssue]
        .select_related("loved_one")
        .order_by("-created_at")
    )

    # Convert to schemas
    loved_ones_schemas = []
    for loved_one_rel in loved_ones_queryset:
        # Access loved_one user (already prefetched via select_related - no extra query)
        loved_one_user = loved_one_rel.loved_one
        user_schema = UserSchema.model_validate(loved_one_user)
        loved_one_schema = LovedOneSchema(
            id=loved_one_rel.id,
            user_id=loved_one_rel.user_id,
            loved_one=user_schema,
            is_active=loved_one_rel.is_active,
            is_alerted=loved_one_rel.is_alerted,
            created_at=loved_one_rel.created_at,
            updated_at=loved_one_rel.updated_at,
        )
        loved_ones_schemas.append(loved_one_schema)

    response = LovedOneListResponse(
        message="Loved ones fetched successfully",
        loved_ones=loved_ones_schemas,
        count=len(loved_ones_schemas),
    )

    return response.model_dump()


def add_loved_one(
    request: HttpRequest,
    data: AddLovedOneRequest,
) -> dict[str, Any]:
    """Add a loved one contact.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)
        data: The request data containing loved_one_email and is_alerted

    Returns:
        Dictionary containing the created loved one and success message

    Raises:
        HttpError: If user not found, self-addition attempted, or relationship already exists

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]
    current_user = request.user  # pyright: ignore[reportAttributeAccessIssue]

    # Validate email format (basic check)
    if not data.loved_one_email or "@" not in data.loved_one_email:
        raise ValidationError(
            errors=[{"field": "loved_one_email", "message": "Invalid email format"}],
        )

    # Find the user to add as loved one
    try:
        loved_one_user = User.objects.get(email=data.loved_one_email)  # pyright: ignore[reportAttributeAccessIssue]
    except User.DoesNotExist as e:  # pyright: ignore[reportAttributeAccessIssue]
        raise HttpError(
            status_code=404,
            message=f"User with email '{data.loved_one_email}' not found",
        ) from e

    # Prevent self-addition
    if loved_one_user.id == user_id:
        raise HttpError(
            status_code=400,
            message="Cannot add yourself as a loved one",
        )

    # Check if relationship already exists
    existing_relationship = LovedOne.objects.filter(  # pyright: ignore[reportAttributeAccessIssue]
        user_id=user_id,
        loved_one_id=loved_one_user.id,
    ).first()

    if existing_relationship:
        if existing_relationship.is_active:
            raise HttpError(
                status_code=400,
                message=f"'{data.loved_one_email}' is already in your loved ones list",
            )
        # If relationship exists but is inactive, reactivate it
        with transaction.atomic():  # pyright: ignore[reportGeneralTypeIssues]
            existing_relationship.is_active = True
            existing_relationship.is_alerted = data.is_alerted
            existing_relationship.save()

            loved_one_user_schema = UserSchema.model_validate(loved_one_user)
            loved_one_schema = LovedOneSchema(
                id=existing_relationship.id,
                user_id=existing_relationship.user_id,
                loved_one=loved_one_user_schema,
                is_active=existing_relationship.is_active,
                is_alerted=existing_relationship.is_alerted,
                created_at=existing_relationship.created_at,
                updated_at=existing_relationship.updated_at,
            )

            response = LovedOneResponse(
                message=f"'{data.loved_one_email}' has been re-added to your loved ones list",
                loved_one=loved_one_schema,
            )
            return response.model_dump()

    # Create new relationship
    try:
        with transaction.atomic():  # pyright: ignore[reportGeneralTypeIssues]
            loved_one_rel = LovedOne.objects.create(  # pyright: ignore[reportAttributeAccessIssue]
                user_id=user_id,
                loved_one_id=loved_one_user.id,
                is_alerted=data.is_alerted,
            )

            loved_one_user_schema = UserSchema.model_validate(loved_one_user)
            loved_one_schema = LovedOneSchema(
                id=loved_one_rel.id,
                user_id=loved_one_rel.user_id,
                loved_one=loved_one_user_schema,
                is_active=loved_one_rel.is_active,
                is_alerted=loved_one_rel.is_alerted,
                created_at=loved_one_rel.created_at,
                updated_at=loved_one_rel.updated_at,
            )

            logger.info(
                "User %s added %s as loved one (is_alerted=%s)",
                current_user.email,
                data.loved_one_email,
                data.is_alerted,
            )

            response = LovedOneResponse(
                message=f"'{data.loved_one_email}' has been added to your loved ones list",
                loved_one=loved_one_schema,
            )
            return response.model_dump()

    except IntegrityError as e:
        logger.exception("Error creating loved one relationship")
        raise HttpError(
            status_code=500,
            message="Failed to add loved one. Please try again.",
        ) from e


def delete_loved_one(
    request: HttpRequest,
    loved_one_id: int,
) -> dict[str, Any]:
    """Delete a loved one relationship.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)
        loved_one_id: The ID of the loved one relationship to delete

    Returns:
        Dictionary containing success message

    Raises:
        HttpError: If loved one relationship not found or doesn't belong to user

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]
    current_user = request.user  # pyright: ignore[reportAttributeAccessIssue]

    # Find and validate the relationship belongs to current user
    try:
        loved_one_rel = LovedOne.objects.get(id=loved_one_id, user_id=user_id)  # pyright: ignore[reportAttributeAccessIssue]
    except LovedOne.DoesNotExist as e:  # pyright: ignore[reportAttributeAccessIssue]
        raise HttpError(
            status_code=404,
            message="Loved one relationship not found",
        ) from e

    # Soft delete (set is_active=False) to preserve history
    with transaction.atomic():  # pyright: ignore[reportGeneralTypeIssues]
        loved_one_email = loved_one_rel.loved_one.email  # pyright: ignore[reportAttributeAccessIssue]
        loved_one_rel.is_active = False
        loved_one_rel.save()

        logger.info(
            "User %s removed %s from loved ones list",
            current_user.email,
            loved_one_email,
        )

    return {
        "message": f"'{loved_one_email}' has been removed from your loved ones list",
    }


def update_loved_one(
    request: HttpRequest,
    loved_one_id: int,
    data: UpdateLovedOneRequest,
) -> dict[str, Any]:
    """Update loved one settings.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)
        loved_one_id: The ID of the loved one relationship to update
        data: The update data (is_alerted, is_active)

    Returns:
        Dictionary containing updated loved one and success message

    Raises:
        HttpError: If loved one relationship not found or doesn't belong to user

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]
    current_user = request.user  # pyright: ignore[reportAttributeAccessIssue]

    # Find and validate the relationship belongs to current user
    try:
        loved_one_rel = LovedOne.objects.get(id=loved_one_id, user_id=user_id)  # pyright: ignore[reportAttributeAccessIssue]
    except LovedOne.DoesNotExist as e:  # pyright: ignore[reportAttributeAccessIssue]
        raise HttpError(
            status_code=404,
            message="Loved one relationship not found",
        ) from e

    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HttpError(
            status_code=400,
            message="No fields to update",
        )

    with transaction.atomic():  # pyright: ignore[reportGeneralTypeIssues]
        if "is_alerted" in update_data:
            loved_one_rel.is_alerted = update_data["is_alerted"]
        if "is_active" in update_data:
            loved_one_rel.is_active = update_data["is_active"]
        loved_one_rel.save()

        # Fetch updated relationship with related user
        loved_one_rel.refresh_from_db()
        loved_one_user = loved_one_rel.loved_one
        loved_one_user_schema = UserSchema.model_validate(loved_one_user)

        loved_one_schema = LovedOneSchema(
            id=loved_one_rel.id,
            user_id=loved_one_rel.user_id,
            loved_one=loved_one_user_schema,
            is_active=loved_one_rel.is_active,
            is_alerted=loved_one_rel.is_alerted,
            created_at=loved_one_rel.created_at,
            updated_at=loved_one_rel.updated_at,
        )

        logger.info(
            "User %s updated loved one %s settings: %s",
            current_user.email,
            loved_one_user.email,
            update_data,
        )

        response = LovedOneResponse(
            message="Loved one settings updated successfully",
            loved_one=loved_one_schema,
        )
        return response.model_dump()


def toggle_loved_one_alerted(
    request: HttpRequest,
    loved_one_id: int,
) -> dict[str, Any]:
    """Toggle is_alerted status for a loved one.

    Args:
        request: The HTTP request object (contains authenticated user via request.user)
        loved_one_id: The ID of the loved one relationship to toggle

    Returns:
        Dictionary containing updated loved one and success message

    Raises:
        HttpError: If loved one relationship not found or doesn't belong to user

    """
    user_id = request.user.id  # pyright: ignore[reportAttributeAccessIssue]
    current_user = request.user  # pyright: ignore[reportAttributeAccessIssue]

    # Find and validate the relationship belongs to current user
    try:
        loved_one_rel = LovedOne.objects.get(id=loved_one_id, user_id=user_id)  # pyright: ignore[reportAttributeAccessIssue]
    except LovedOne.DoesNotExist as e:  # pyright: ignore[reportAttributeAccessIssue]
        raise HttpError(
            status_code=404,
            message="Loved one relationship not found",
        ) from e

    # Toggle is_alerted status
    with transaction.atomic():  # pyright: ignore[reportGeneralTypeIssues]
        loved_one_rel.is_alerted = not loved_one_rel.is_alerted
        loved_one_rel.save()

        # Fetch updated relationship with related user
        loved_one_rel.refresh_from_db()
        loved_one_user = loved_one_rel.loved_one
        loved_one_user_schema = UserSchema.model_validate(loved_one_user)

        loved_one_schema = LovedOneSchema(
            id=loved_one_rel.id,
            user_id=loved_one_rel.user_id,
            loved_one=loved_one_user_schema,
            is_active=loved_one_rel.is_active,
            is_alerted=loved_one_rel.is_alerted,
            created_at=loved_one_rel.created_at,
            updated_at=loved_one_rel.updated_at,
        )

        status_text = "will be alerted" if loved_one_rel.is_alerted else "will not be alerted"
        logger.info(
            "User %s toggled is_alerted for loved one %s to %s",
            current_user.email,
            loved_one_user.email,
            loved_one_rel.is_alerted,
        )

        response = LovedOneResponse(
            message=f"'{loved_one_user.email}' {status_text} when crash is detected",
            loved_one=loved_one_schema,
        )
        return response.model_dump()

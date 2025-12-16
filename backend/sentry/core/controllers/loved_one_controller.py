"""Loved one controller."""

from typing import Any

from django.http import HttpRequest

from core.models import LovedOne
from core.schemas import LovedOneListResponse, LovedOneSchema, UserSchema


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
        LovedOne.objects.filter(user_id=user_id, is_active=True)  # pyright: ignore[reportAttributeAccessIssue].select_related("loved_one").order_by("-created_at")
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

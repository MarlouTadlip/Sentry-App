"""Loved one model."""

from typing import ClassVar

from django.db import models

from .user import User


class LovedOne(models.Model):
    """Loved one relationship model.

    Represents the relationship between a device owner (user) and their
    loved one contact (also a user). This enables device owners to add
    contacts who will be notified in case of emergency.

    Note: A User can be both a device owner and a loved one for other users.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loved_ones",
        help_text="The device owner who added this loved one contact",
    )
    loved_one = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loved_one_for",
        help_text="The user who is a loved one contact for the device owner",
    )
    is_active = models.BooleanField(
        default=True,  # pyright: ignore[reportArgumentType]
        help_text="Whether this loved one relationship is active",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this loved one relationship was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this loved one relationship was last updated",
    )

    class Meta:  # noqa: D106
        verbose_name = "Loved One"
        verbose_name_plural = "Loved Ones"
        ordering: ClassVar[list[str]] = ["-created_at"]
        constraints: ClassVar[list[models.UniqueConstraint]] = [
            models.UniqueConstraint(
                fields=["user", "loved_one"],
                name="unique_user_loved_one",
            ),
        ]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["user"]),
            models.Index(fields=["loved_one"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:  # noqa: D105
        return f"{self.user.email} -> {self.loved_one.email}"  # pyright: ignore[reportAttributeAccessIssue]

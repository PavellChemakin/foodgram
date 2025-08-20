"""Custom user model for Foodgram.

Extends Django's AbstractUser to enforce unique email addresses and
use email as the login field. Additional fields (first_name,
last_name and username) mirror those on the base class and are
required for registration. The ``related_name`` values on the
``groups`` and ``user_permissions`` relationships are overridden to
avoid clashes when referencing them through the user model.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model which uses email as the unique identifier."""

    email = models.EmailField(
        unique=True,
        verbose_name='Email address',
        help_text='A unique email address used for authentication',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self) -> str:
        return self.email
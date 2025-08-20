from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь с уникальным e‑mail."""

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='Уникальный адрес для аутентификации',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self) -> str:
        return self.email

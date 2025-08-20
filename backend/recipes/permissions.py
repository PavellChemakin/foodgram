"""Custom permission classes for the recipes app."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Allow authors to edit their objects; read‑only for others."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, 'author', None) == request.user
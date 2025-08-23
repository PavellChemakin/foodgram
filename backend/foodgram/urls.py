from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Djoser provides a complete set of user management endpoints.
    # Mount them under the ``/api/`` prefix.  This exposes paths
    # such as ``/api/users/``, ``/api/users/me/``, ``/api/users/set_password/``
    # and friends.  See the Djoser documentation for the full list.
    path('api/', include('djoser.urls')),

    # Token authentication endpoints.  We mount the same set of
    # endpoints twice: once under ``/api/`` (resulting in
    # ``/api/token/login/`` and ``/api/token/logout/``) and once under
    # ``/api/auth/`` (``/api/auth/token/login/`` and ``/api/auth/token/logout/``).
    # The latter is kept for backward compatibility with some front‑end
    # clients and is also mapped in the gateway nginx configuration.
    path('api/', include('djoser.urls.authtoken')),
    path('api/auth/', include('djoser.urls.authtoken')),

    # Application-specific API modules.  Recipes and user subscriptions
    # are exposed under the same ``/api/`` prefix.
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

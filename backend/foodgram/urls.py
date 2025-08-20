"""URL configuration for the Foodgram project.

Routes incoming HTTP requests to the appropriate views. The API is
mounted at ``/api/`` and is split across multiple apps. Djoser is
responsible for registration and authentication of users, while the
``recipes`` app handles recipe, ingredient, tag and shopping cart
endpoints. Static and media files are served by Django in
development; in production these should be handled by nginx.
"""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    # Djoser provides ``/users/`` and related endpoints for user
    # registration, activation, password reset and profile retrieval.
    path('api/', include('djoser.urls')),  # user registration & management
    path('api/', include('djoser.urls.authtoken')),  # token auth
    # Application API endpoints
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),  # subscription endpoints
]

# During development serve static and media files from Django.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

"""URL routing for user‑related endpoints beyond djoser."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import SubscriptionViewSet


router = DefaultRouter()
# Register the subscriptions endpoint under the ``users`` prefix
router.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')

subscription_view = SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'})

urlpatterns = [
    # Expose list and creation of subscriptions at /api/users/subscriptions/
    path('', include(router.urls)),
    # Subscribe/unsubscribe to a specific author
    path('users/<int:pk>/subscribe/', subscription_view, name='subscribe'),
]
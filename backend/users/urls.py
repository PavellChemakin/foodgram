from __future__ import annotations

from django.urls import include, path
from recipes.views import SubscriptionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users/subscriptions', SubscriptionViewSet,
                basename='subscriptions')

subscription_view = SubscriptionViewSet.as_view({'post': 'create',
                                                 'delete': 'destroy'})

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:pk>/subscribe/', subscription_view, name='subscribe'),
]

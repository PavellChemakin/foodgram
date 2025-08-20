"""Viewsets and API views for the recipes application.

The viewsets defined here expose model data via RESTful endpoints.
Custom actions support favouriting recipes, adding them to a shopping
cart and downloading aggregated shopping lists. Permissions are
enforced to ensure that only authors can modify their own recipes
while unauthenticated users may read data.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable

from django.db.models import F, Sum
from django.http import HttpResponse
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides read‑only access to tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides read‑only access to ingredients with search support."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            # filter by startswith case‑insensitively
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Create, update, delete and list recipes, with custom actions."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):  # type: ignore[override]
        if self.request.method in ('POST', 'PATCH'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):  # type: ignore[override]
        """Return queryset filtered by tags, author and favourites/shopping cart flags."""
        queryset = Recipe.objects.all()
        request = self.request
        # Filter by tags (slug). Multiple tags combine with OR semantics
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        # Filter by author id
        author_id = request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        # Filter by whether recipe is favourited by current user
        user = request.user
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited is not None and user.is_authenticated:
            try:
                flag = bool(int(is_favorited))
            except ValueError:
                flag = False
            fav_ids = Favorite.objects.filter(user=user).values_list('recipe_id', flat=True)
            if flag:
                queryset = queryset.filter(id__in=fav_ids)
            else:
                queryset = queryset.exclude(id__in=fav_ids)
        # Filter by whether recipe is in shopping cart for current user
        is_in_cart = request.query_params.get('is_in_shopping_cart')
        if is_in_cart is not None and user.is_authenticated:
            try:
                flag_cart = bool(int(is_in_cart))
            except ValueError:
                flag_cart = False
            cart_ids = ShoppingCart.objects.filter(user=user).values_list('recipe_id', flat=True)
            if flag_cart:
                queryset = queryset.filter(id__in=cart_ids)
            else:
                queryset = queryset.exclude(id__in=cart_ids)
        return queryset

    def perform_create(self, serializer: RecipeWriteSerializer) -> None:  # type: ignore[override]
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Add a recipe to the current user's favourites."""
        recipe = self.get_object()
        user = request.user
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Recipe already in favourites.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):  # type: ignore[override]
        """Remove a recipe from the current user's favourites."""
        recipe = self.get_object()
        user = request.user
        deleted, _ = Favorite.objects.filter(user=user, recipe=recipe).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Recipe not in favourites.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Add a recipe to the user's shopping cart."""
        recipe = self.get_object()
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Recipe already in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):  # type: ignore[override]
        """Remove a recipe from the user's shopping cart."""
        recipe = self.get_object()
        user = request.user
        deleted, _ = ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Recipe not in shopping cart.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Generate a plain‑text shopping list and return it as a file."""
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)
        if not cart_items.exists():
            return Response(
                {'errors': 'Shopping cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Aggregate ingredient amounts across all recipes in the cart
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in=cart_items.values_list('recipe', flat=True))
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )
        lines: list[str] = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total']
            lines.append(f'{name} ({unit}) — {amount}')
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class SubscriptionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Allow users to subscribe to authors and view their subscriptions."""

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):  # type: ignore[override]
        return Subscription.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        author_id = request.data.get('author') or kwargs.get('pk')
        if author_id is None:
            return Response({'errors': 'Author id required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            author = request.user.__class__.objects.get(pk=author_id)
        except Exception:
            return Response({'errors': 'Author not found.'}, status=status.HTTP_404_NOT_FOUND)
        if author == request.user:
            return Response({'errors': 'Cannot subscribe to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(user=request.user, author=author).exists():
            return Response({'errors': 'Already subscribed.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.create(user=request.user, author=author)
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):  # type: ignore[override]
        author_id = kwargs.get('pk')
        try:
            author = request.user.__class__.objects.get(pk=author_id)
        except Exception:
            return Response({'errors': 'Author not found.'}, status=status.HTTP_404_NOT_FOUND)
        deleted, _ = Subscription.objects.filter(user=request.user, author=author).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Not subscribed.'}, status=status.HTTP_400_BAD_REQUEST)
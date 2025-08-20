"""Serialisers for converting model instances to and from JSON.

These classes define how recipes, ingredients and tags are exposed via
the REST API. Nested representations are used for recipe retrieval,
while write operations accept flat JSON that is converted into the
appropriate related objects. A custom field handles base64‑encoded
images produced by the SPA frontend.
"""

from __future__ import annotations

import base64
import imghdr
import uuid
from typing import Any, Dict, Iterable, List, Tuple

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Exists, OuterRef
from rest_framework import serializers

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    """A field that decodes base64‑encoded images into Django files.

    The SPA frontend sends images as base64 strings. This custom field
    intercepts those strings and decodes them into a ``ContentFile`` so
    that Django's ``ImageField`` can process and store them correctly.
    If the input is not a base64 string it is passed through to the
    default ``ImageField`` for validation.
    """

    def to_internal_value(self, data: Any) -> Any:
        # Check if the incoming data is a base64 encoded string
        if isinstance(data, str) and data.startswith('data:image'):
            format_str, img_str = data.split(';base64,')
            img_format = format_str.split('/')[-1]
            decoded = base64.b64decode(img_str)
            # Attempt to detect file extension if not provided
            file_ext = imghdr.what(None, decoded) or img_format
            file_name = f'{uuid.uuid4()}.{file_ext}'
            data = ContentFile(decoded, name=file_name)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Serialises tag objects for read‑only operations."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serialises ingredients for list and detail views."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Represents ingredients within a recipe including their amount."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """A compact representation of a recipe used in subscriptions."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Read‑only serialiser for retrieving recipe details."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Helper serialiser for creating and updating recipe ingredients."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serialiser for creating and updating recipes."""

    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not value:
            raise serializers.ValidationError('At least one ingredient is required.')
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('Duplicate ingredients are not allowed.')
        return value

    def validate_tags(self, value: List[Tag]) -> List[Tag]:
        if not value:
            raise serializers.ValidationError('At least one tag is required.')
        return value

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Recipe:
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance: Recipe, validated_data: Dict[str, Any]) -> Recipe:
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def _save_ingredients(self, recipe: Recipe, ingredients_data: Iterable[Dict[str, Any]]) -> None:
        objs: List[RecipeIngredient] = []
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(pk=item['id'])
            objs.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=item['amount'],
                )
            )
        RecipeIngredient.objects.bulk_create(objs)

    def to_representation(self, instance: Recipe) -> Dict[str, Any]:
        serializer = RecipeReadSerializer(
            instance,
            context=self.context,
        )
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serialises user subscriptions with nested recipes."""

    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj: Subscription) -> List[Dict[str, Any]]:
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if limit is not None and limit.isdigit():
            queryset = queryset[: int(limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj: Subscription) -> int:
        return obj.author.recipes.count()
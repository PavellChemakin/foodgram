from __future__ import annotations

import base64
import imghdr
import uuid
from typing import Any, Dict, Iterable, List

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


class Base64ImageField(serializers.ImageField):
    """Поле для base64‑изображений."""

    def to_internal_value(self, data: Any) -> Any:
        if isinstance(data, str) and data.startswith('data:image'):
            format_str, img_str = data.split(';base64,')
            img_format = format_str.split('/')[-1]
            decoded = base64.b64decode(img_str)
            file_ext = imghdr.what(None, decoded) or img_format
            file_name = f'{uuid.uuid4()}.{file_ext}'
            data = ContentFile(decoded, name=file_name)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткий рецепт."""

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецепта."""

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
    """Сериализатор ингредиента при записи."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше нуля.')
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецепта."""

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

    def validate_ingredients(self,
                             value: List[Dict[str,
                                              Any]]) -> List[Dict[str, Any]]:
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Дубли ингредиентов не допускаются.')
        return value

    def validate_tags(self, value: List[Tag]) -> List[Tag]:
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
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
    def update(self, instance: Recipe,
               validated_data: Dict[str, Any]) -> Recipe:
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def _save_ingredients(self, recipe: Recipe,
                          ingredients_data: Iterable[Dict[str, Any]]) -> None:
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
    """Сериализатор пользовательских подпискок с вложенными рецептами."""

    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='author.last_name',
                                      read_only=True)
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

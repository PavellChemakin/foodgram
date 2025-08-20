"""Database models for the recipes app.

This module defines the core data structures used throughout the
Foodgram service: recipes, tags, ingredients, ingredient amounts,
favourites, shopping carts and subscriptions. Relationships are set
up to ensure consistency and enforce uniqueness where appropriate.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """A categorical label applied to recipes.

    Tags allow recipes to be grouped by common themes such as
    breakfast, lunch or dinner. Each tag has a human‑readable name,
    a colour (represented as a hex code beginning with ``#``) and a
    slug used for filtering via the API. All fields are unique.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Name',
        help_text='Short descriptive name of the tag',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Colour',
        help_text='HEX colour code (e.g. #E26C2D)',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug',
        help_text='Unique slug used in recipe filters',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """An item used in a recipe along with its unit of measure.

    Each ingredient has a name and a measurement unit (such as grams,
    pieces or tablespoons). The combination of name and unit must be
    unique to avoid duplication in the database. Searching for
    ingredients via the API is case‑insensitive and matches the
    beginning of the name.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Ingredient name (e.g. Sugar)',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Measurement unit',
        help_text='Unit of measurement (e.g. g, ml, pieces)',
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """A user‑authored recipe with ingredients and tags.

    Recipes link a user (author) to a collection of ingredients and
    tags. Each recipe stores an image, a textual description, the
    cooking time in minutes and a publication timestamp. Deleting
    the author cascades to delete all of their recipes.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Image',
    )
    text = models.TextField(
        verbose_name='Description',
        help_text='Detailed cooking instructions',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time (min)',
        help_text='Total preparation and cooking time in minutes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Through model for linking ingredients to recipes.

    Stores the amount of a particular ingredient required for a
    recipe. The combination of recipe and ingredient is unique.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Amount',
        help_text='Quantity of ingredient required',
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ingredient amount'
        verbose_name_plural = 'Ingredient amounts'

    def __str__(self) -> str:
        return f'{self.ingredient} – {self.amount}'


class Favorite(models.Model):
    """Many‑to‑many relationship between users and recipes they like."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'

    def __str__(self) -> str:
        return f'{self.user} likes {self.recipe}'


class ShoppingCart(models.Model):
    """Recipes a user intends to cook, aggregated into a shopping list."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
    )
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Shopping cart item'
        verbose_name_plural = 'Shopping cart items'

    def __str__(self) -> str:
        return f'{self.recipe} in cart of {self.user}'


class Subscription(models.Model):
    """Represents a user subscribing to an author's recipes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self) -> str:
        return f'{self.user} subscribes to {self.author}'
from django.core.management.base import BaseCommand
from django.db import transaction
from recipes.models import Ingredient, Recipe, Recipe_ingredient, Tag
from users.models import User


class Command(BaseCommand):
    help = "Load test users and recipes into the database"

    @transaction.atomic
    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'testuser1',
                'email': 'test1@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь 1',
            },
            {
                'username': 'testuser2',
                'email': 'test2@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь 2',
            },
        ]
        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'], defaults=data
            )
            if created:
                user.set_password('testpassword')
                user.save()
                created_users.append(user)
            else:
                changed = False
                for field, value in data.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        changed = True
                if changed:
                    user.save()
        tag, _ = Tag.objects.get_or_create(
            name='Завтрак',
            defaults={'slug': 'breakfast', 'color': '#00FF00'}
        )
        ingredient, _ = Ingredient.objects.get_or_create(
            name='Соль',
            defaults={'measurement_unit': 'г'}
        )
        author = User.objects.get(username='testuser1')
        recipe, created = Recipe.objects.get_or_create(
            name='Тестовый рецепт',
            defaults={
                'text': 'Это тестовый рецепт для демонстрации',
                'cooking_time': 10,
                'author': author,
            },
        )
        if created:
            Recipe_ingredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=1
            )
            recipe.tags.add(tag)
        self.stdout.write(
            self.style.SUCCESS('Test data created successfully.')
        )

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Configuration for the ``recipes`` app.

    Provides a human‑readable name for the app and sets the default
    auto field type.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Recipes'
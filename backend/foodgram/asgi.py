"""ASGI entry point for Foodgram.

This module exposes an ASGI application for asynchronous servers. It sets
the default settings module for the project before instantiating
the ASGI application via Django's ``get_asgi_application`` helper.
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = get_asgi_application()
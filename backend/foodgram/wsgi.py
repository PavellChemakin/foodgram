"""WSGI entry point for Foodgram.

This module exposes a WSGI callable which can be used by WSGI
servers such as Gunicorn to serve the Django application. It sets
the default settings module for the 'foodgram' project and creates
the WSGI application via Django's ``get_wsgi_application`` helper.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = get_wsgi_application()
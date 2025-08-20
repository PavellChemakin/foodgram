#!/usr/bin/env python
"""
Utility script for administrative tasks.

This entry point allows you to interact with the Django management
commands within the ``foodgram`` project. It sets the default
``DJANGO_SETTINGS_MODULE`` environment variable so that Django knows
which settings to use. When executed, it passes any supplied
command‑line arguments to Django's ``execute_from_command_line``
function.

Running this script with no arguments will display the list of
available commands. To perform database migrations, create a
superuser or run the development server, invoke the appropriate
command:

    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

The project is designed around Django 4.x and uses Python 3.11 or
later. See the README for further details on project structure and
deployment instructions.
"""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
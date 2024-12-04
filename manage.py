#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Ejecuta tareas administrativas.

    Establece la variable de entorno DJANGO_SETTINGS_MODULE a 'tuniforme.settings'.
    Intenta importar y ejecutar 'execute_from_command_line' desde 'django.core.management'.
    Si la importación falla, lanza un ImportError con un mensaje explicativo.

    Raises:
        ImportError: Si Django no está instalado o no está disponible en la variable de entorno PYTHONPATH.
    """
    # tuniforme/manage.py
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuniforme.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

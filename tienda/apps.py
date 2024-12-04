# tienda/apps.py

from django.apps import AppConfig

# Configuración de la aplicación 'tienda'
class TiendaConfig(AppConfig):
    # Campo auto incremental por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación
    name = 'tienda'

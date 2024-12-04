# carro/apps.py

from django.apps import AppConfig

# Configuración de la aplicación 'carro'
class CarroConfig(AppConfig):
    # Campo auto incremental por defecto para los modelos
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación
    name = 'carro'

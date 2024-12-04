from django.apps import AppConfig

# raiz/apps.py
class RaizConfig(AppConfig):
    # Especifica el campo auto incremental por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación
    name = 'raiz'

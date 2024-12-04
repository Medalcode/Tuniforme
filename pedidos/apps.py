# pedidos/apps.py

from django.apps import AppConfig

# Configuración de la aplicación 'pedidos'
class PedidosConfig(AppConfig):
    # Campo auto incrementable por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación
    name = 'pedidos'

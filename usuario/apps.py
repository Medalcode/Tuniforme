#Aqui realizamos la importación de las librerías necesarias

from django.apps import AppConfig

# Configuración de la aplicación 'usuario'
class UsuarioConfig(AppConfig):
    # Campo auto incrementable por defecto
    default_auto_field = 'django.db.models.BigAutoField'
    # Nombre de la aplicación
    name = 'usuario'



class UsuarioConfig(AppConfig):
    name = 'usuario'

    def ready(self):
        import usuario.signals

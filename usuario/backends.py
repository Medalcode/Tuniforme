# usuario/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Persona

class RUTAuthBackend(BaseBackend):
    def authenticate(self, request, rut=None, password=None):
        print(f"Autenticando usuario con RUT: {rut}")
        if rut:
            rut = rut.replace(".", "").replace("-", "").upper()  # Limpiar el RUT
            print(f"RUT limpio: {rut}")
        try:
            user = Persona.objects.get(rut=rut)
            print(f"Usuario encontrado: {user}")
            if user.check_password(password):
                print("Contraseña correcta")
                return user
            else:
                print("Contraseña incorrecta")
        except Persona.DoesNotExist:
            print("Usuario no encontrado")
            return None

    def get_user(self, user_id):
        print(f"Obteniendo usuario con ID: {user_id}")
        try:
            return Persona.objects.get(pk=user_id)
        except Persona.DoesNotExist:
            print("Usuario no encontrado")
            return None
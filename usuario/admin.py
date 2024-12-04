#Aqui realizamos la importación de las librerías necesarias

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Persona

# Definición de la clase PersonaAdmin para la administración del modelo Persona
class PersonaAdmin(UserAdmin):
    model = Persona
    list_display = ('email', 'rut', 'nombre', 'apellido', 'region', 'comuna', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    
    # Configuración de los campos que se mostrarán en el formulario de edición
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('rut', 'nombre', 'apellido', 'telefono', 'direccion', 'comuna', 'region')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Configuración de los campos que se mostrarán en el formulario de creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'rut', 'nombre', 'apellido', 'telefono', 'direccion', 'comuna', 'region', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    # Configuración de los campos de búsqueda
    search_fields = ('email', 'rut', 'nombre', 'apellido', 'comuna', 'region',)
    ordering = ('email',)

# Registro del modelo Persona en el sitio de administración
admin.site.register(Persona, PersonaAdmin)
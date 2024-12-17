#Aqui realizamos la importación de las librerías necesarias
from django.urls import path
from .views import registro_view, login_view, logout_view, perfil, actualizar_perfil, eliminar_cuenta
from django.urls import path
from django.contrib.auth import views as auth_views


# Nombre de la aplicación
app_name = 'nsusuario'

# Definición de las rutas de la aplicación nsusuario
urlpatterns = [


    # Esta es la Ruta para el registro de usuarios
    path('registro/', registro_view, name='registro'),  # usuario/registro.html
    
    # Esta es la Ruta para el inicio de sesión
    path('login/', login_view, name='login'),  # usuario/login.html
    
    # Esta es la Ruta para el cierre de sesión
    path('logout/', logout_view, name='logout'),  # usuario/logout.html
    
    # Esta es la Ruta para ver el perfil del usuario
    path('perfil/', perfil, name='perfil'),  # usuario/perfil.html
    
    # Esta es la Ruta para actualizar el perfil del usuario
    path('actualizar_perfil/', actualizar_perfil, name='actualizar_perfil'),  # usuario/actualizar_perfil.html
    
    # Esta es la Ruta para eliminar la cuenta del usuario
    path('eliminar_cuenta/', eliminar_cuenta, name='eliminar_cuenta'),  # usuario/eliminar_cuenta.html
    # Otras rutas de la aplicación usuario...
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='usuario/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuario/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuario/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/password_reset_complete.html'), name='password_reset_complete'),
]
from django.urls import path
from .views import registro_view, login_view, logout_view, perfil, actualizar_perfil, eliminar_cuenta
from django.contrib.auth import views as auth_views

app_name = 'nsusuario'

urlpatterns = [
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil, name='perfil'),
    path('actualizar_perfil/', actualizar_perfil, name='actualizar_perfil'),
    path('eliminar_cuenta/', eliminar_cuenta, name='eliminar_cuenta'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='usuario/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuario/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuario/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/password_reset_complete.html'), name='password_reset_complete'),
]
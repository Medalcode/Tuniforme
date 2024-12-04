# tuniforme/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import admin_views  # Importar la nueva vista de cierre de sesión del administrador

urlpatterns = [
    # Admin site
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),  # Nueva ruta de cierre de sesión del administrador
    path('admin/', admin.site.urls),  # admin/admin.py

    # La ruta se redirige a la app raiz
    path('raiz/', include('raiz.urls', namespace='nsraiz')),  # raiz/urls.py

    # Ruta para la app usuario
    path('usuario/', include('usuario.urls', namespace='nsusuario')),  # usuario/urls.py

    # Ruta para la app tienda
    path('tienda/', include('tienda.urls', namespace='nstienda')),  # tienda/urls.py

    # Ruta para la app carro
    path('carro/', include('carro.urls', namespace='carro')),  # carro/urls.py

    # Ruta para la app pedidos
    path('pedidos/', include('pedidos.urls', namespace='nspedidos')),  # pedidos/urls.py

    # Rutas para autenticación de usuarios
    path('usuarios/login/', auth_views.LoginView.as_view(), name='login'),  # usuario/templates/registration/login.html
    path('usuarios/logout/', auth_views.LogoutView.as_view(), name='logout'),  # usuario/templates/registration/logged_out.html
]

# Configuración para servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # settings.py
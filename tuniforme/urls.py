# tuniforme/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import admin_views  # Importar la nueva vista de cierre de sesión del administrador

urlpatterns = [
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),  # Nueva ruta de cierre de sesión del administrador
    path('admin/', admin.site.urls),  # admin/admin.py
    path('raiz/', include('raiz.urls', namespace='nsraiz')),  # raiz/urls.py
    path('usuario/', include('usuario.urls', namespace='nsusuario')),  # usuario/urls.py
    path('tienda/', include('tienda.urls', namespace='nstienda')),  # tienda/urls.py
    path('carro/', include('carro.urls', namespace='carro')),  # carro/urls.py
    path('pedidos/', include('pedidos.urls', namespace='nspedidos')),  # pedidos/urls.py
    path('usuarios/login/', auth_views.LoginView.as_view(), name='login'),  # usuario/templates/registration/login.html
    path('usuarios/logout/', auth_views.LogoutView.as_view(), name='logout'),  # usuario/templates/registration/logged_out.html
    path('api/', include('coreapi.urls')),
    path('', RedirectView.as_view(url='/raiz/index', permanent=True)),  # Redirigir la URL raíz a /raiz/index
]

# Configuración para servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # settings.py
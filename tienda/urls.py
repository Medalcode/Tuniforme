# Aqui realizamos la importación de las librerías necesarias
from django.urls import path
from . import views  
from .views import detalle_producto, comprar_producto

app_name = 'nstienda'

urlpatterns = [
    # Ruta para la vista de la tienda
    path('', views.tienda, name='tienda'),  # tienda/views.py

    # Ruta para confirmar el pedido
    path('confirmar_pedido/', views.confirmar_pedido, name='confirmar_pedido'),  # tienda/views.py

    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'),
    path('producto/<int:producto_id>/comprar/', comprar_producto, name='comprar_producto'),
]
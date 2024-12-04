# carro/urls.py
from django.urls import path
from . import views

app_name = 'carro'

urlpatterns = [
    # URL para agregar un producto al carro
    path('agregar/<int:producto_id>/', views.agregar_producto, name='agregar'),  # carro/views.py
    
    # URL para restar un producto del carro
    path('restar/<int:producto_id>/', views.restar_producto, name='restar'),  # carro/views.py

    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar'),

    path('limpiar/', views.limpiar_carro, name='limpiar'),
    

    # URL para finalizar el pedido
    path('fin_pedido/', views.fin_pedido, name='fin_pedido'),  # carro/views.py
]
from . import views
from django.urls import path

app_name = 'nsraiz'

urlpatterns = [
    # Ruta para la vista base
    path('base/', views.base, name='base'),  # raiz/views.py

    # Ruta para la vista index
    path('index/', views.index, name='index'),  # raiz/views.py

    # Ruta para la vista contacto
    path('contacto/', views.contacto, name='contacto'),  # raiz/views.py

    # Ruta para la vista confirmacion
    path('confirmacion/', views.confirmacion, name='confirmacion'),  # raiz/views.py
]

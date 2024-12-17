# filepath: /C:/Users/forge/Documents/GitHub/Tuniforme/coreapi/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import ProductoViewSet
from.import views
from .api import ProductoViewSet

router = routers.DefaultRouter()
router.register('api/productos', ProductoViewSet, 'productos')

urlpatterns = [
    path('', include(router.urls)),
    
]
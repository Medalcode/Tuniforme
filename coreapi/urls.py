# filepath: /C:/Users/forge/Documents/GitHub/Tuniforme/coreapi/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
# filepath: /C:/Users/forge/Documents/GitHub/Tuniforme/coreapi/serializers.py
from rest_framework import serializers
from tienda.models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
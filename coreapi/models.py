from rest_framework import serializers
from tienda.models import Producto


#Es el modelo producto de la app tienda 
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
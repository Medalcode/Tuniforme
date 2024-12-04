# carro/appcarro.py

from decimal import Decimal
from tienda.models import Producto

class Carro:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carro = self.session.get('carro')
        if not carro:
            carro = self.session['carro'] = {}
        self.carro = carro

    def agregar(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carro:
            self.carro[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'preciounitario': str(producto.precio),
                'cantidad': 1,
                'imagen': producto.imagen.url if producto.imagen else None
            }
        else:
            self.carro[producto_id]['cantidad'] += 1
        self.guardar_carro()

    def guardar_carro(self):
        self.session['carro'] = self.carro
        self.session.modified = True

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carro:
            del self.carro[producto_id]
            self.guardar_carro()

    def restar_producto(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carro:
            self.carro[producto_id]['cantidad'] -= 1
            if self.carro[producto_id]['cantidad'] <= 0:
                self.eliminar(producto)
            else:
                self.guardar_carro()

    def limpiar_carro(self):
        self.session['carro'] = {}
        self.session.modified = True

    def contar_productos(self):
        return sum(item['cantidad'] for item in self.carro.values())
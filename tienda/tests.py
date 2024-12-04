# tienda/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Producto

class CarritoTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(nombre='Producto 1', descripcion='Descripción', precio=10.00, stock=10)
        self.client.post(reverse('carro:agregar', args=[self.producto.id]))

    def test_fin_pedido_resta_stock(self):
        response = self.client.post(reverse('carro:fin_pedido'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 9)
        self.assertRedirects(response, reverse('tienda:productos'))
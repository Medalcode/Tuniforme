#Limonatur/pedidos/models.py
from django.db import models
from django.contrib.auth import get_user_model
from tienda.models import Producto
from django.db.models import F, Sum, FloatField
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models.signals import post_save


User = get_user_model()

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    finalizado = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)  # Asegúrate de que este campo esté definido

    def __str__(self):
        return f"Pedido {self.id} - Usuario {self.usuario.username}"

    class Meta:
        db_table = 'tPedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    @property
    def recalcular_total(self):
        total = self.detalles.aggregate(
            total=Sum(F('precio') * F('cantidad'), output_field=FloatField())
        )['total'] or 0.0
        self.total = total

@receiver(post_save, sender=Pedido)
def validate_pedido_id(sender, instance, created, **kwargs):
    print(f"Post-save signal triggered for Pedido with ID: {instance.id}")
    if created and instance.id is None:
        raise ValueError("El ID del pedido no fue generado correctamente.")

class DetallePedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    finalizado = models.BooleanField(default=False)  # Campo para indicar si el pedido está finalizado
    comision = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    total_fabricante = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def calcular_comision(self):
        return self.precio * self.cantidad * Decimal('0.30')

    def save(self, *args, **kwargs):
        total_pedido = self.precio * self.cantidad
        self.comision = total_pedido * Decimal('0.30')
        self.total_fabricante = total_pedido * Decimal('0.70')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cantidad} unidades de {self.producto.nombre}'

    class Meta:
        db_table = 'tDetallePedidos'
        verbose_name = 'DetallePedido'
        verbose_name_plural = 'DetallePedidos'
        ordering = ['id']
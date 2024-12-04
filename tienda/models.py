from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver 

User = get_user_model()

class Fabricante(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Cat_Colegio(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cat_colegio'
        verbose_name_plural = 'cats_colegios'

    def __str__(self):
        return self.nombre

class Cat_Tipo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cat_tipo'
        verbose_name_plural = 'cat_tipos'

    def __str__(self):
        return self.nombre

class Cat_Sexo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cat_sexo'
        verbose_name_plural = 'cat_sexos'

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cat_colegio = models.ForeignKey(Cat_Colegio, on_delete=models.CASCADE, default=1)
    cat_tipo = models.ForeignKey(Cat_Tipo, on_delete=models.CASCADE, default=1)
    cat_sexo = models.ForeignKey(Cat_Sexo, on_delete=models.CASCADE, default=1)
    imagen = models.ImageField(upload_to='productos', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    disponibilidad = models.BooleanField(default=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='productos')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        db_table = 'tProductos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def reducir_stock(self, cantidad):
        if self.stock >= cantidad:
            self.stock -= cantidad
            self.save()
            return True
        return False

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.precio < 0:
            raise ValidationError('El precio no puede ser negativo.')

@receiver(pre_save, sender=Producto)
def set_sku(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = f"{instance.cat_colegio.codigo}-{instance.cat_sexo.codigo}-{instance.cat_tipo.codigo}-{instance.id or ''}"
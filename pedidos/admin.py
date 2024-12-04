from django.contrib import admin
from .models import Pedido, DetallePedido
from tienda.models import Fabricante, Producto, Cat_Tipo, Cat_Colegio, Cat_Sexo
from tienda.admin import ProductoAdmin, Cat_TipoAdmin, Cat_ColegioAdmin, Cat_SexoAdmin  # Importar ProductoAdmin

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    readonly_fields = ('comision', 'total_fabricante')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'finalizado', 'total')
    list_filter = ('finalizado',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            fabricante = Fabricante.objects.get(usuario=request.user)
            print(f"Fabricante: {fabricante.nombre}")  # Depuración
            pedidos = qs.filter(detalles__producto__fabricante=fabricante).distinct()
            print(f"Pedidos encontrados: {pedidos.count()}")  # Depuración
            for pedido in pedidos:
                print(f"Pedido ID: {pedido.id}, Usuario: {pedido.usuario}, Total: {pedido.total}")  # Depuración
            return pedidos
        except Fabricante.DoesNotExist:
            return qs.none()
        
    def get_comision_total(self, obj):
        comision_total = sum(detalle.calcular_comision() for detalle in obj.detalles.all())
        print(f"Comisión Total para Pedido {obj.id}: {comision_total}")  # Depuración
        return comision_total
    get_comision_total.short_description = 'Comisión Total'

@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    
admin.site.register(Pedido, PedidoAdmin)
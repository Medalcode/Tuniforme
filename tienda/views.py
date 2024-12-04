from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView
from .models import Producto, Cat_Colegio, Cat_Tipo, Cat_Sexo

def tienda(request):
    productos = Producto.objects.all()
    categorias_colegio = Cat_Colegio.objects.all()
    categorias_tipo = Cat_Tipo.objects.all()
    categorias_sexo = Cat_Sexo.objects.all()

    # Filtrar productos por categorías
    categoria_colegio_id = request.GET.get('cat_colegio')
    categoria_tipo_id = request.GET.get('cat_tipo')
    categoria_sexo_id = request.GET.get('cat_sexo')

    if categoria_colegio_id:
        productos = productos.filter(cat_colegio_id=categoria_colegio_id)
    if categoria_tipo_id:
        productos = productos.filter(cat_tipo_id=categoria_tipo_id)
    if categoria_sexo_id:
        productos = productos.filter(cat_sexo_id=categoria_sexo_id)

    return render(request, 'tienda/tienda.html', {
        'productos': productos,
        'categorias_colegio': categorias_colegio,
        'categorias_tipo': categorias_tipo,
        'categorias_sexo': categorias_sexo,
    })

def confirmar_pedido(request):
    return render(request, 'tienda/confirmar_pedido.html')

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def comprar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.stock > 0:
        producto.stock -= 1
        producto.save()
        messages.success(request, 'Compra realizada con éxito.')
    else:
        messages.error(request, 'Lo sentimos, este producto está agotado.')
    return redirect('nstienda:detalle_producto', producto_id=producto.id)

class ProductoListView(ListView):
    model = Producto
    template_name = 'tienda/tienda.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_colegio_id = self.request.GET.get('categoria_colegio')
        categoria_tipo_id = self.request.GET.get('categoria_tipo')
        categoria_sexo_id = self.request.GET.get('categoria_sexo')

        if categoria_colegio_id:
            queryset = queryset.filter(cat_colegio_id=categoria_colegio_id)
        if categoria_tipo_id:
            queryset = queryset.filter(cat_tipo_id=categoria_tipo_id)
        if categoria_sexo_id:
            queryset = queryset.filter(cat_sexo_id=categoria_sexo_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias_colegio'] = Cat_Colegio.objects.all()
        context['categorias_tipo'] = Cat_Tipo.objects.all()
        context['categorias_sexo'] = Cat_Sexo.objects.all()
        return context
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.management import call_command
from django.http import HttpResponse
from .models import Producto, Cat_Colegio, Cat_Tipo, Cat_Sexo

def tienda(request):
    productos_list = Producto.objects.all()
    categorias_colegio = Cat_Colegio.objects.all()
    categorias_tipo = Cat_Tipo.objects.all()
    categorias_sexo = Cat_Sexo.objects.all()

    # Filtrar productos por categorías
    categoria_colegio_id = request.GET.get('cat_colegio')
    categoria_tipo_id = request.GET.get('cat_tipo')
    categoria_sexo_id = request.GET.get('cat_sexo')

    if categoria_colegio_id:
        productos_list = productos_list.filter(cat_colegio_id=categoria_colegio_id)
    if categoria_tipo_id:
        productos_list = productos_list.filter(cat_tipo_id=categoria_tipo_id)
    if categoria_sexo_id:
        productos_list = productos_list.filter(cat_sexo_id=categoria_sexo_id)

    # Implementar paginación
    paginator = Paginator(productos_list, 4)  # 12 productos por página
    page = request.GET.get('page')

    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    context = {
        'productos': productos,
        'categorias_colegio': categorias_colegio,
        'categorias_tipo': categorias_tipo,
        'categorias_sexo': categorias_sexo,
    }

    return render(request, 'tienda/tienda.html', context)

def confirmar_pedido(request):
    return render(request, 'tienda/confirmar_pedido.html')

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def poblar_tienda(request):
    """
    Vista de emergencia para poblar la base de datos en producción.
    Solo funciona si se pasa la clave correcta para evitar abusos.
    """
    if request.GET.get('key') == 'demo2024':
        try:
            call_command('migrate') # Asegurar que las tablas existan
            call_command('seed_tienda')
            return HttpResponse("<h1>¡Éxito!</h1><p>Tienda poblada correctamente. <a href='/tienda/'>Ir a la Tienda</a></p>")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")
    return HttpResponse("Acceso Denegado. Falta key.")

def comprar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.stock > 0:
        producto.stock -= 1
        producto.save()
        messages.success(request, 'Compra realizada con éxito.')
    else:
        messages.error(request, 'Lo sentimos, este producto está agotado.')
    return redirect('tienda:detalle_producto', producto_id=producto.id)
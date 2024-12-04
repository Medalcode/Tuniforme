# carro/views.py

from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404

from pedidos.views import enviar_email
from .appcarro import Carro
from tienda.models import Producto
from django.utils import timezone
from django.contrib import messages
from pedidos.models import Pedido, DetallePedido

# Función para agregar un producto al carro
def agregar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    if producto.stock > 0:
        carro.agregar(producto)
        producto.stock -= 1
        producto.save()
    else:
        messages.error(request, "No hay suficiente stock disponible.")
    return redirect('nstienda:tienda')

# Función para restar un producto del carro
def restar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.restar_producto(producto)
    return redirect('nstienda:tienda')

# Función para eliminar un producto del carro
def eliminar_producto(request, producto_id):
    carro = Carro(request)
    producto = Producto.objects.get(id=producto_id)
    carro.eliminar(producto=producto)
    return redirect('nstienda:tienda')

# Función para limpiar el carro
def limpiar_carro(request):
    carro = Carro(request)
    carro.limpiar_carro()
    return redirect('nstienda:tienda')

# Función para finalizar el pedido y mostrar el resumen
def fin_pedido(request):
    if not request.user.is_authenticated:
        return redirect('usuarios/login/')
    
    carro = Carro(request)
    if not carro.carro:
        messages.error(request, "El carro está vacío.")
        return render(request, 'carro/fin_pedido.html', {
            'usuario': request.user,
            'carro_vacio': True,
            'fecha_actual': timezone.now()
        })

    # Crear el pedido
    pedido = Pedido(usuario=request.user)
    try:
        pedido.save()  # Guardar para generar el ID
        print(f"Pedido creado con ID: {pedido.id}")
    except Exception as e:
        print(f"Error al guardar el pedido: {e}")
        return JsonResponse({"error": "Error al crear el pedido"}, status=500)

    detalle_pedido = []
    for key, value in carro.carro.items():
        producto = get_object_or_404(Producto, id=key)
        detalle = DetallePedido(
            producto=producto,
            cantidad=value['cantidad'],
            usuario=request.user,
            pedido=pedido,
            precio_unitario=producto.precio,
            precio=value['cantidad'] * producto.precio,
            comision=0.0,
            total_fabricante=0.0
        )
        detalle.save()
        detalle_pedido.append(detalle)

    # Calcular el total del pedido
    pedido.total = sum(item.precio for item in detalle_pedido)
    pedido.save()

    # Verificar y guardar en la sesión
    request.session['pedido_id'] = pedido.id
    request.session.modified = True
    print(f"ID del pedido guardado en la sesión: {request.session['pedido_id']}")

    context = {
        'pedido': pedido,
        'detalle_pedido': detalle_pedido,
        'usuario': request.user,
        'fecha_actual': timezone.now(),
        'valor_total_carro': pedido.total,
        'carro_vacio': False
    }

    return render(request, 'carro/fin_pedido.html', context)
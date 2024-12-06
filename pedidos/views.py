# Limonatura/pedidos/views.py
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from carro.appcarro import Carro
from .models import Pedido, DetallePedido
from tienda.models import Fabricante, Producto, Cat_Tipo, Cat_Colegio, Cat_Sexo  # Asegúrate de importar Cat_Tipo, Cat_Colegio, Cat_Sexo
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.apps import apps
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from django.http import JsonResponse
from django.http import HttpResponseRedirect
import logging
from django.urls import reverse
from django.db.models import Sum, F
import openpyxl
from django.http import HttpResponse
from .models import Pedido, DetallePedido
from django.utils import timezone


logger = logging.getLogger(__name__)

# Limonatura/pedidos/views.py

# views.py
# views.py
def reporte_pedidos(request):
    pedidos = Pedido.objects.all()
    detalles = DetallePedido.objects.all()
    fabricantes = Fabricante.objects.all()
    productos = Producto.objects.all()
    categorias_tipo = Cat_Tipo.objects.all()  # Asegúrate de usar Cat_Tipo

    # Filtrar por fabricante
    fabricante_id = request.GET.get('fabricante')
    if fabricante_id:
        pedidos = pedidos.filter(detalles__producto__fabricante_id=fabricante_id).distinct()
        detalles = detalles.filter(producto__fabricante_id=fabricante_id)

    # Filtrar por producto
    producto_id = request.GET.get('producto')
    if producto_id:
        pedidos = pedidos.filter(detalles__producto_id=producto_id).distinct()
        detalles = detalles.filter(producto_id=producto_id)

    # Filtrar por tipo
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        pedidos = pedidos.filter(detalles__producto__cat_tipo_id=tipo_id).distinct()  # Asegúrate de usar cat_tipo
        detalles = detalles.filter(producto__cat_tipo_id=tipo_id)  # Asegúrate de usar cat_tipo

    total_pedidos = pedidos.count()
    pedidos_por_cliente = pedidos.values('usuario__nombre').annotate(total=Sum(F('detalles__precio')))

    context = {
        'total_pedidos': total_pedidos,
        'pedidos_por_cliente': pedidos_por_cliente,
        'detalles': detalles,
        'fabricantes': fabricantes,
        'productos': productos,
        'categorias_tipo': categorias_tipo,
        'pedidos': pedidos,
    }
    return render(request, 'pedidos/reporte_pedidos.html', context)

# Crear un pedido y guardarlo en la sesión
def crear_pedido(request):
    if request.user.is_authenticated:
        # Crear el pedido
        pedido = Pedido.objects.create(usuario=request.user)
        
        # Almacenar el ID del pedido en la sesión
        request.session['pedido_id'] = pedido.id

        # Obtener los datos del carrito
        carro = Carro(request)
        productos_carro = carro.carro

        # Calcular el valor total del carrito
        valor_total_carro = sum(Decimal(item['precio']) * item['cantidad'] for item in productos_carro.values())

        # Pasar los datos al contexto de la plantilla
        context = {
            'pedido': pedido,
            'usuario': request.user,
            'carro': productos_carro,
            'valor_total_carro': valor_total_carro,
            'fecha_actual': timezone.now(),
            'carro_vacio': len(productos_carro) == 0,
        }

        return render(request, 'carro/fin_pedido.html', context)
    else:
        # Manejo para cuando el usuario no está autenticado
        return redirect('login')

def obtener_pedido(request):
    pedido_id = request.session.get('pedido_id')

    if pedido_id:
        pedido = Pedido.objects.get(id=pedido_id)
        return render(request, 'pedido_detalle.html', {'pedido': pedido})
    else:
        # Manejo para cuando el ID del pedido no está en la sesión
        raise ValueError("Pedido ID no encontrado en la sesión")

##########################################################################



# Limonatura/pedidos/views.py

@login_required(login_url='usuarios/login/')
def procesar_pedido(request):
    if not request.user.is_authenticated:
        return redirect('usuarios/login/')
    
    Producto = apps.get_model('tienda', 'Producto')
    pedido = Pedido.objects.create(usuario=request.user)
    carro = Carro(request)
    detalle_pedido = []

    if not carro.carro:
        print("El carro está vacío")
        return redirect('nstienda:carrito')  # Redirigir al carrito o manejar el caso

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
        print(f"Detalle guardado: {detalle.id}, producto: {detalle.producto.nombre}, cantidad: {detalle.cantidad}")

    # Calcular el total del pedido
    pedido.total = sum(item.precio for item in detalle_pedido)
    pedido.save()

    # Verificar que el ID del pedido no sea None
    if pedido.id is None:
        print("Error: El ID del pedido es None")
        return JsonResponse({"error": "Error al crear el pedido"}, status=500)

    # Almacenar el ID del pedido en la sesión
    request.session['pedido_id'] = pedido.id
    request.session.modified = True  # Forzar que Django guarde cambios en la sesión
    print(f"ID del pedido guardado en la sesión: {request.session['pedido_id']}")

    enviar_email(
        pedido=pedido,
        detalle_pedido=detalle_pedido,
        usuario=request.user.username,
        emailusuario=request.user.email
    )

    # Redirigir a la vista create_transaction
    return redirect('pedidos:create_transaction')

#########################################################################

def enviar_email(**kwargs):
    pedido = kwargs['pedido']
    detalle_pedido = kwargs['detalle_pedido']
    usuario = kwargs['usuario']
    emailusuario = kwargs['emailusuario']
    subject = 'Confirmación de pedido'
    message = render_to_string('pedidos/email_pedido.html', {
        'pedido': pedido,
        'detalle_pedido': detalle_pedido,
        'usuario': usuario
    })
    mensaje_texto = strip_tags(message)
    from_email = 'jonatthan.medalla@gmail.com'
    to = emailusuario

    send_mail(subject, mensaje_texto, from_email, [to], html_message=message)
    print(f"Correo enviado a {emailusuario} con asunto '{subject}'")


###############################################################################

# Limonatura/pedidos/views.py

def create_transaction(request):
    # Obtener el ID del pedido desde la sesión
    print(f"Contenido de la sesión: {request.session.items()}")
    pedido_id = request.session.get('pedido_id')
    logger.info(f"Pedido ID en la sesión: {pedido_id}")

    if not pedido_id:
        logger.error("Pedido ID no encontrado en la sesión.")
        print("No se encontró el ID del pedido en la sesión")
        return JsonResponse({"error": "No se encontró el ID del pedido en la sesión"}, status=400)

    # Obtener el pedido
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        print(f"Pedido encontrado: {pedido}")
    except Pedido.DoesNotExist:
        print("Pedido no encontrado")
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)

    # Obtener el total del carro
    carro = Carro(request)
    amount = sum(float(item['precio']) * item['cantidad'] for item in carro.carro.values())
    print(f"Total del carro: {amount}")

    # Definir la URL de retorno
    return_url = "https://tuniforme.onrender.com/pedidos/transaction/commit"  # Actualiza esta línea

    # Crear la transacción con Webpay
    try:
        buy_order = str(pedido.id)  # Asegúrate de que buy_order sea una cadena de texto
        session_id = str(request.session.session_key)  # Asegúrate de que session_id sea una cadena de texto
        response = Transaction().create(buy_order, session_id, amount, return_url)
        print(f"Transacción creada: {response}")
    except Exception as e:
        print(f"Error al crear la transacción: {e}")
        return JsonResponse({"error": "Error al crear la transacción"}, status=500)

    # Redirigir al usuario a la URL de pago
    return HttpResponseRedirect(f"{response['url']}?token_ws={response['token']}")

################################################################################

# Limonatura/pedidos/views.py

def confirmar_pago(request, token_ws):
    transaction = Transaction().commit(token_ws)
    if transaction['response_code'] == 0:  # Pago exitoso
        pedido = Pedido.objects.get(id=transaction['buy_order'])
        pedido.finalizado = True
        pedido.save()
        print(f"Pedido {pedido.id} finalizado correctamente.")

        # Actualizar el stock de los productos
        for detalle in pedido.detalles.all():
            producto = detalle.producto
            print(f"Producto antes de actualizar stock: {producto.nombre}, stock actual: {producto.stock}, cantidad a restar: {detalle.cantidad}")
            producto.stock -= detalle.cantidad
            producto.save()
            print(f"Producto después de actualizar stock: {producto.nombre}, stock actualizado: {producto.stock}")

        return redirect('pedidos:detalle', pedido.id)
    else:
        # Manejar el caso de transacción rechazada
        print("Transacción rechazada")
        return redirect('pedidos:fallido')

##############################################################################

# Limonatura/pedidos/views.py

def commit_transaction(request):
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    if not token:
        print("Token no encontrado")
        return JsonResponse({"error": "Token no encontrado"}, status=400)

    transaction = Transaction(WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    ))

    response = transaction.commit(token)
    print(f"Respuesta de la transacción: {response}")

    if response['status'] == 'AUTHORIZED':
        # Limpiar el carrito después de que la transacción se haya completado con éxito
        carro = Carro(request)
        carro.limpiar_carro()
        print("Carrito limpiado después de la transacción exitosa")

        # Marcar el pedido como finalizado y actualizar el stock
        pedido_id = request.session.get('pedido_id')
        print(f"ID del pedido en la sesión: {pedido_id}")
        if pedido_id:
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                pedido.finalizado = True
                pedido.save()
                print(f"Pedido {pedido.id} finalizado correctamente.")

                # Actualizar el stock de los productos
                for detalle in pedido.detalles.all():
                    producto = detalle.producto
                    print(f"Producto antes de actualizar stock: {producto.nombre}, stock actual: {producto.stock}, cantidad a restar: {detalle.cantidad}")
                    producto.stock -= detalle.cantidad
                    producto.save()
                    print(f"Producto después de actualizar stock: {producto.nombre}, stock actualizado: {producto.stock}")

                del request.session['pedido_id']
                print(f"Pedido {pedido_id} finalizado correctamente.")
            except Pedido.DoesNotExist:
                print(f"Pedido {pedido_id} no encontrado.")
        else:
            print("No se encontró el ID del pedido en la sesión.")

    # Redirigir al usuario a la página de confirmación
    return HttpResponseRedirect(reverse('nstienda:confirmar_pedido'))

#############################################################################


# Limonatura/pedidos/views.py

def exportar_reporte_pedidos(request):
    # Crear un libro de trabajo y una hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Pedidos"

    # Agregar encabezados
    headers = ["Pedido ID", "Cliente", "Producto", "Cantidad", "Precio Unitario", "Precio Total", "Comisión", "Total Fabricante"]
    ws.append(headers)

    # Obtener los datos
    detalles = DetallePedido.objects.select_related('pedido', 'producto').all()

    # Agregar datos a la hoja
    for detalle in detalles:
        row = [
            detalle.pedido.id,
            detalle.pedido.usuario.nombre,  # Cambia a 'email' si es necesario
            detalle.producto.nombre,
            detalle.cantidad,
            detalle.precio_unitario,
            detalle.precio,
            detalle.comision,
            detalle.total_fabricante
        ]
        ws.append(row)

    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reporte_pedidos.xlsx'

    # Guardar el libro de trabajo en la respuesta
    wb.save(response)
    return response
# Limonatura/pedidos/views.py
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from carro.appcarro import Carro
from .models import Pedido, DetallePedido
from tienda.models import Fabricante, Producto, Cat_Tipo, Cat_Colegio, Cat_Sexo
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.apps import apps
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Sum, F
from django.utils import timezone
import logging
import openpyxl

# Transbank imports
from .transbank_helper import get_transbank_transaction, get_transbank_options
from transbank.common.integration_type import IntegrationType

logger = logging.getLogger('pedidos')

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
    """
    Procesa el pedido del usuario con validación de stock y manejo de errores.
    """
    if not request.user.is_authenticated:
        return redirect('usuarios/login/')
    
    Producto = apps.get_model('tienda', 'Producto')
    carro = Carro(request)

    if not carro.carro:
        logger.warning(f"Usuario {request.user.id} intentó procesar pedido con carro vacío")
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('carro:carro')

    try:
        # Validar stock ANTES de crear el pedido
        for key, value in carro.carro.items():
            producto = get_object_or_404(Producto, id=key)
            
            if producto.stock < value['cantidad']:
                messages.error(
                    request, 
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Disponible: {producto.stock}, Solicitado: {value['cantidad']}"
                )
                logger.warning(
                    f"Stock insuficiente - Producto: {producto.id}, "
                    f"Stock: {producto.stock}, Solicitado: {value['cantidad']}"
                )
                return redirect('carro:carro')
        
        # Usar transacción atómica para garantizar consistencia
        with transaction.atomic():
            # Crear el pedido
            pedido = Pedido.objects.create(usuario=request.user)
            detalle_pedido = []

            # Crear detalles del pedido con bloqueo pesimista
            for key, value in carro.carro.items():
                producto = Producto.objects.select_for_update().get(id=key)
                
                # Validar stock nuevamente dentro de la transacción
                if producto.stock < value['cantidad']:
                    raise ValueError(
                        f"Stock insuficiente para {producto.nombre} durante la transacción"
                    )
                
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
                
                logger.info(
                    f"Detalle creado: {detalle.id}, producto: {detalle.producto.nombre}, "
                    f"cantidad: {detalle.cantidad}"
                )

            # Calcular el total del pedido
            pedido.total = sum(item.precio for item in detalle_pedido)
            pedido.save()
            
            logger.info(f"Pedido {pedido.id} creado exitosamente para usuario {request.user.id}")

        # Almacenar el ID del pedido en la sesión
        request.session['pedido_id'] = pedido.id
        request.session.modified = True
        logger.info(f"ID del pedido {pedido.id} guardado en sesión")

        # Enviar email de confirmación
        try:
            enviar_email(
                pedido=pedido,
                detalle_pedido=detalle_pedido,
                usuario=request.user.rut or request.user.email,
                emailusuario=request.user.email
            )
            logger.info(f"Email de confirmación enviado para pedido {pedido.id}")
        except Exception as e:
            logger.error(f"Error al enviar email para pedido {pedido.id}: {e}")
            # No bloqueamos el proceso si falla el email

        # Redirigir a la vista create_transaction
        return redirect('pedidos:create_transaction')
        
    except ValueError as e:
        logger.error(f"Error de validación al procesar pedido: {e}")
        messages.error(request, str(e))
        return redirect('carro:carro')
    except Exception as e:
        logger.exception(f"Error inesperado al procesar pedido: {e}")
        messages.error(request, "Error al procesar el pedido. Por favor intenta nuevamente.")
        return redirect('carro:carro')

#########################################################################

def enviar_email(**kwargs):
    """
    Envía email de confirmación de pedido.
    """
    from django.conf import settings
    
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
    from_email = settings.DEFAULT_FROM_EMAIL
    to = emailusuario

    send_mail(subject, mensaje_texto, from_email, [to], html_message=message)
    logger.info(f"Correo enviado a {emailusuario} para pedido {pedido.id}")


###############################################################################

# Limonatura/pedidos/views.py

def create_transaction(request):
    """
    Crea una transacción con Transbank Webpay Plus.
    """
    from django.conf import settings
    
    # Obtener el ID del pedido desde la sesión
    pedido_id = request.session.get('pedido_id')
    logger.info(f"Iniciando transacción - Pedido ID: {pedido_id}")

    if not pedido_id:
        logger.error("Pedido ID no encontrado en la sesión")
        messages.error(request, "No se encontró información del pedido")
        return redirect('carro:carro')

    # Obtener el pedido
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        logger.info(f"Pedido encontrado: {pedido.id}, Total: {pedido.total}")
    except Pedido.DoesNotExist:
        logger.error(f"Pedido {pedido_id} no encontrado en la base de datos")
        messages.error(request, "Pedido no encontrado")
        return redirect('carro:carro')

    # Obtener el total del carro
    carro = Carro(request)
    amount = sum(float(item['precio']) * item['cantidad'] for item in carro.carro.values())
    logger.info(f"Monto total de la transacción: {amount}")

    # Obtener configuración de Transbank
    config = settings.TRANSBANK_CONFIG
    return_url = config['return_url']

    # Crear la transacción con Webpay usando el helper
    try:
        buy_order = str(pedido.id)
        session_id = str(request.session.session_key)
        
        # Usar el helper de Transbank
        tb_transaction = get_transbank_transaction()
        response = tb_transaction.create(buy_order, session_id, amount, return_url)
        
        logger.info(
            f"Transacción creada - Token: {response.get('token', 'N/A')}, "
            f"URL: {response.get('url', 'N/A')}"
        )
    except Exception as e:
        logger.exception(f"Error al crear la transacción con Transbank: {e}")
        messages.error(request, "Error al procesar el pago. Por favor intenta nuevamente.")
        return redirect('carro:carro')

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
    """
    Procesa el callback de Transbank después del pago.
    Actualiza el estado del pedido y el stock de productos de forma atómica.
    """
    token = request.POST.get("token_ws") or request.GET.get("token_ws")
    
    if not token:
        logger.error("Token de Transbank no encontrado en la petición")
        messages.error(request, "Error en la transacción. Token no encontrado.")
        return redirect('carro:carro')

    try:
        # Obtener la transacción usando el helper
        tb_transaction = get_transbank_transaction()
        response = tb_transaction.commit(token)
        
        logger.info(
            f"Respuesta de Transbank - Status: {response.get('status')}, "
            f"Response Code: {response.get('response_code')}"
        )
        
        # Verificar si el pago fue autorizado
        if response.get('status') != 'AUTHORIZED':
            logger.warning(f"Pago no autorizado - Response: {response}")
            messages.error(
                request, 
                f"Pago rechazado. Código: {response.get('response_code', 'desconocido')}"
            )
            return redirect('carro:carro')
        
        # Obtener el ID del pedido desde la sesión
        pedido_id = request.session.get('pedido_id')
        
        if not pedido_id:
            logger.error("No se encontró el ID del pedido en la sesión después del pago")
            messages.error(request, "Error: Pedido no encontrado en la sesión")
            return redirect('carro:carro')
        
        # Procesar el pedido de forma atómica
        with transaction.atomic():
            # Obtener el pedido con lock pesimista
            try:
                pedido = Pedido.objects.select_for_update().get(id=pedido_id)
            except Pedido.DoesNotExist:
                logger.error(f"Pedido {pedido_id} no encontrado en la base de datos")
                messages.error(request, "Pedido no encontrado")
                return redirect('carro:carro')
            
            # Actualizar el stock de los productos con validación
            for detalle in pedido.detalles.select_related('producto'):
                producto = Producto.objects.select_for_update().get(id=detalle.producto.id)
                
                logger.info(
                    f"Actualizando stock - Producto: {producto.nombre}, "
                    f"Stock actual: {producto.stock}, Cantidad vendida: {detalle.cantidad}"
                )
                
                # Validar que hay stock suficiente
                if producto.stock < detalle.cantidad:
                    error_msg = (
                        f"Stock insuficiente para {producto.nombre} al confirmar pago. "
                        f"Stock: {producto.stock}, Requerido: {detalle.cantidad}"
                    )
                    logger.error(error_msg)
                    # IMPORTANTE: Aquí se debería implementar un proceso de reembolso
                    messages.error(
                        request, 
                        "Error: Stock insuficiente. Se procesará el reembolso. "
                        "Contacta a soporte."
                    )
                    # TODO: Implementar proceso de reembolso con Transbank
                    return redirect('carro:carro')
                
                # Actualizar stock
                producto.stock -= detalle.cantidad
                producto.save()
                
                logger.info(
                    f"Stock actualizado - Producto: {producto.nombre}, "
                    f"Nuevo stock: {producto.stock}"
                )
            
            # Marcar el pedido como finalizado
            pedido.finalizado = True
            pedido.save()
            logger.info(f"Pedido {pedido.id} marcado como finalizado")
        
        # Limpiar el carrito después de que todo fue exitoso
        carro = Carro(request)
        carro.limpiar_carro()
        logger.info(f"Carrito limpiado para pedido {pedido.id}")
        
        # Limpiar sesión
        if 'pedido_id' in request.session:
            del request.session['pedido_id']
        
        messages.success(request, "¡Pago procesado exitosamente!")
        logger.info(f"Transacción completada exitosamente para pedido {pedido.id}")
        
        # Redirigir a la página de confirmación
        return HttpResponseRedirect(reverse('nstienda:confirmar_pedido'))
        
    except Pedido.DoesNotExist:
        logger.error(f"Pedido {pedido_id} no encontrado")
        messages.error(request, "Pedido no encontrado")
        return redirect('carro:carro')
        
    except ValueError as e:
        logger.error(f"Error de validación en commit_transaction: {e}")
        messages.error(request, str(e))
        return redirect('carro:carro')
        
    except Exception as e:
        logger.exception(f"Error inesperado en commit_transaction: {e}")
        messages.error(
            request, 
            "Error al procesar el pago. Por favor contacta a soporte con tu número de orden."
        )
        return redirect('carro:carro')

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
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.core.mail import send_mail

# raiz/views.py
def base(request):
    # Renderiza la plantilla base
    return render(request, 'raiz/base.html')

# raiz/views.py
def index(request):
    # Inicializar el carrito de compras si no está presente en la sesión
    if 'carro' not in request.session:
        request.session['carro'] = {}

    # Calcular el valor total del carrito
    for item in request.session['carro'].values():
        print(f"Precio: {item['precio']}, Cantidad: {item['cantidad']}")  # Agrega este punto de depuración

    valor_total_carro = sum(float(item['precio']) * item['cantidad'] for item in request.session['carro'].values())

    # Renderiza la plantilla del índice con el valor total del carrito
    return render(request, 'raiz/index.html', {'valor_total_carro': valor_total_carro})

# raiz/views.py
def contacto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            asunto = form.cleaned_data['asunto']
            
            # Enviar correo electrónico
            send_mail(
                nombre,
                asunto,
                email,
                ['jonatthan.medalla@gmail.com'],  # Cambia esto por el correo del destinatario
                fail_silently=False,
            )
            # Redirige a la página de confirmación
            return redirect('nsraiz:confirmacion')
    else:
        form = ContactForm()
    
    # Renderiza la plantilla de contacto con el formulario
    return render(request, 'raiz/contacto.html', {'form': form})

# raiz/views.py
def confirmacion(request):
    # Renderiza la plantilla de confirmación
    return render(request, 'raiz/confirmacion.html')
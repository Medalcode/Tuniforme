#Aqui se realizan las importaciones necesarias
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import FormularioCreacionUsuario, FormularioAutenticacion
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

#Aqui creamos las vistas de usuario

# usuario/views.py
from django.contrib import messages

def login_view(request):
    print("Entrando a la vista de login")
    if request.method == 'POST':
        print("Método POST recibido")
        form = FormularioAutenticacion(data=request.POST)
        if form.is_valid():
            print("Formulario válido")
            rut = form.cleaned_data.get('rut')
            password = form.cleaned_data.get('password')
            print(f"Datos recibidos - RUT: {rut}, Contraseña: {password}")
            user = authenticate(request, rut=rut, password=password)
            if user is not None:
                print("Usuario autenticado correctamente")
                login(request, user)
                # Redirigir al usuario a la tienda con un parámetro de éxito en la URL
                return redirect('nsraiz:index') + '?login_success=1'
            else:
                print("Error de autenticación")
                form.add_error(None, 'RUT o contraseña incorrectos')
        else:
            print("Formulario no válido")
            print(f"Errores del formulario: {form.errors}")
    else:
        print("Método GET recibido")
        form = FormularioAutenticacion()
    return render(request, 'usuario/login.html', {'form': form})



#Aqui creamos la vista de cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('nsraiz:index')  # Redirige a la página de inicio después de cerrar sesión

# views.py

# usuario/views.py
def registro_view(request):
    if request.method == 'POST':
        form = FormularioCreacionUsuario(request.POST)
        if form.is_valid():
            form.save()
            # Agrega un mensaje de éxito en el contexto
            return render(request, 'usuario/registro.html', {'form': form, 'registro_exitoso': True})
        else:
            print(f"Errores del formulario de registro: {form.errors}")
    else:
        form = FormularioCreacionUsuario()
    return render(request, 'usuario/registro.html', {'form': form})

#Aqui creamos la vista de perfil
@login_required
def perfil(request):
    return render(request, 'usuario/perfil.html')  # usuario/templates/usuario/perfil.html

#Aqui creamos la vista de actualizar perfil
@login_required
def actualizar_perfil(request):
    if request.method == 'POST':
        user = request.user
        user.rut = request.POST.get('rut', user.rut)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.telefono = request.POST.get('telefono', user.telefono)
        user.direccion = request.POST.get('direccion', user.direccion)
        user.region = request.POST.get('region', user.region)
        user.comuna = request.POST.get('comuna', user.comuna)
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('nsusuario:perfil')  # Redirige a la página de perfil después de actualizar
    return render(request, 'usuario/perfil.html')  # usuario/templates/usuario/perfil.html

#Aqui creamos la vista de eliminar cuenta
@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        # Agrega un mensaje de éxito en el contexto
        return render(request, 'usuario/perfil.html', {'cuenta_eliminada': True})
    return render(request, 'usuario/perfil.html')


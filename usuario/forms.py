# usuario/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Persona

class FormularioCreacionUsuario(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    rut = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Persona
        fields = ('rut', 'nombre', 'apellido', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut'].label = 'RUT'
        self.fields['nombre'].label = 'Nombre'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.rut  # Asigna el RUT como username
        if commit:
            user.save()
        return user

class FormularioAutenticacion(forms.Form):
    rut = forms.CharField(max_length=12, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))  # Campo RUT obligatorio
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))  # Campo contraseña obligatorio

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get('rut')
        password = cleaned_data.get('password')
        print(f"Formulario limpiado - RUT: {rut}, Contraseña: {password}")
        if not rut:
            raise forms.ValidationError('Debe proporcionar un RUT')
        if not password:
            raise forms.ValidationError('Debe proporcionar una contraseña')
        return cleaned_data

    def is_valid(self):
        valid = super().is_valid()
        print(f"Formulario es válido: {valid}")
        if not valid:
            print(f"Errores del formulario: {self.errors}")
        return valid
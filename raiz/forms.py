from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# tuniforme/raiz/forms.py

# Definición del formulario de contacto
class ContactForm(forms.Form):
    # Campo para el nombre del usuario
    nombre = forms.CharField(
        label='Nombre', 
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Campo para el correo electrónico del usuario
    email = forms.EmailField(
        label='Correo electrónico', 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    # Campo para el asunto del mensaje
    asunto = forms.CharField(
        label='Asunto', 
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

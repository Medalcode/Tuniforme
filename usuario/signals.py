#Aqui realizamos la importación de las librerías necesarias
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Señal para enviar un correo de bienvenida al usuario
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Bienvenido a nuestro sitio'
        message = 'Gracias por registrarte en nuestro sitio.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        send_mail(subject, message, from_email, recipient_list)
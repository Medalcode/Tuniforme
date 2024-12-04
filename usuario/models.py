# usuario/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

class PersonaManager(BaseUserManager):
    def create_user(self, email, password=None, rut=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not email:
            raise ValueError('El correo electrónico debe ser proporcionado para administradores')
        return self.create_user(email, password, **extra_fields)

class Persona(AbstractUser):
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateTimeField(default=timezone.now)
    telefono = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    comuna = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']

    username = None  # Eliminar el campo username

    class Meta:
        db_table = 'tPersona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    objects = PersonaManager()

    def __str__(self) -> str:
        return f'{self.nombre} {self.apellido}'

    # Añade related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='persona_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='persona',
    )
    # Añade related_name para evitar conflictos
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='persona_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='persona',
    )
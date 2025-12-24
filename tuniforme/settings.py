import os
from pathlib import Path
import dj_database_url 
from dotenv import load_dotenv 

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CHANGE-THIS-IN-PRODUCTION')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Asegúrate de que esto esté incluido
    'raiz.apps.RaizConfig',
    'tienda.apps.TiendaConfig',
    'usuario.apps.UsuarioConfig',
    'carro.apps.CarroConfig',
    'pedidos.apps.PedidosConfig',
    'coreapi.apps.CoreapiConfig',
    'rest_framework',  # Añadir Django REST framework
]

SITE_ID = 1

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Seguridad
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Añadir whitenoise aquí
    'django.middleware.common.CommonMiddleware',  # Común
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Autenticación
    'django.contrib.messages.middleware.MessageMiddleware',  # Mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking
]

# Configuración de URLs
ROOT_URLCONF = 'tuniforme.urls'

# Configuración de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # Procesador de contexto de depuración
                'django.template.context_processors.request',  # Procesador de contexto de solicitud
                'django.contrib.auth.context_processors.auth',  # Procesador de contexto de autenticación
                'django.contrib.messages.context_processors.messages',  # Procesador de contexto de mensajes
                'carro.context_processor.valor_total_carro',  # Procesador de contexto del carro
            ],
        },
    },
]

# Aplicación WSGI
WSGI_APPLICATION = 'tuniforme.wsgi.application'

# Configuración de la base de datos
# Usa DATABASE_URL si está disponible (PostgreSQL en producción),
# de lo contrario usa SQLite para desarrollo local
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'usuario.Persona'

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # Validador de similitud de atributos de usuario
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # Validador de longitud mínima
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # Validador de contraseñas comunes
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # Validador de contraseñas numéricas
    },
]

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración del campo de auto incremento por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración del motor de sesiones
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = True  # Para desarrollo; asegúrate de usar True en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 semanas

# URLs de inicio y cierre de sesión
LOGIN_URL = 'nsusuario:login'
LOGOUT_REDIRECT_URL = 'nsraiz:login'

# Configuración del backend de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your_email@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'your_email@gmail.com')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directorio de archivos multimedia

# Configuración de autenticación
AUTHENTICATION_BACKENDS = [
    'usuario.backends.RUTAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # Opcional para compatibilidad con autenticación por username
]

# Configuración de Transbank
TRANSBANK_CONFIG = {
    'commerce_code': os.getenv('TRANSBANK_API_KEY', '597055555532'),
    'api_key': os.getenv('TRANSBANK_API_SECRET', '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'),
    'environment': os.getenv('TRANSBANK_ENVIRONMENT', 'integration'),
    'return_url': os.getenv('TRANSBANK_RETURN_URL', 'https://tuniforme.onrender.com/pedidos/transaction/commit'),
    'final_url': os.getenv('TRANSBANK_FINAL_URL', 'https://tuniforme.onrender.com/pedidos/transaction/final'),
}

# Security settings for production
if not DEBUG:
    # SSL/HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Security headers
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            'class': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            'class': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'tuniforme.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'pedidos': {
            'handlers': ['console', 'file', 'file_error'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'tienda': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuario': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
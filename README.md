# Tuniforme - Plataforma de Ventas de Uniformes Escolares

## 🚀 Mejoras Críticas Implementadas (Diciembre 2025)

Este proyecto ha recibido **mejoras críticas de seguridad y estabilidad**. Ver `MEJORAS_IMPLEMENTADAS.md` para detalles completos.

## ⚙️ Configuración Inicial Requerida

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto copiando `.env.example`:

```bash
cp .env.example .env
```

Luego edita `.env` con tus valores reales:

#### Generar SECRET_KEY

```python
python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#\$%^&*(-_=+)') for i in range(50)))"
```

#### Obtener Gmail App Password

1. Ve a https://myaccount.google.com/apppasswords
2. Genera una nueva contraseña de aplicación
3. Copia el código de 16 caracteres
4. Agrégalo a `EMAIL_HOST_PASSWORD` en `.env`

#### Configurar Transbank

- Para **testing**: Usa las credenciales de integración (ya están en .env.example)
- Para **producción**: Obtén credenciales reales de Transbank y actualiza `.env`

### 2. Base de Datos

#### Desarrollo Local (SQLite)

```bash
python manage.py migrate
python manage.py createsuperuser
```

#### Producción (PostgreSQL en Render.com)

1. Crea una base de datos PostgreSQL en Render.com
2. Copia el `DATABASE_URL` interno
3. Agrégalo a las variables de entorno en Render.com
4. Ejecuta migraciones: `python manage.py migrate`

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Servidor de Desarrollo

```bash
# Asegúrate de tener DEBUG=True en .env para desarrollo
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
tuniforme/
├── tuniforme/          # Configuración principal
│   ├── settings.py     # ✅ Refactorizado con variables de entorno
│   └── urls.py
├── usuario/            # Autenticación por RUT
├── tienda/             # Catálogo de productos
├── carro/              # Carrito de compras
├── pedidos/            # ✅ Procesamiento mejorado con validación
│   ├── views.py        # ✅ Stock validation + atomic transactions
│   └── transbank_helper.py  # ✅ Nuevo - Configuración centralizada
├── coreapi/            # API REST
├── raiz/               # Página principal
├── logs/               # ✅ Nuevo - Archivos de log
├── .env                # ⚠️ CREAR - Variables de entorno (NO commit)
├── .env.example        # ✅ Plantilla de variables
└── requirements.txt
```

## 🔒 Seguridad

### ⚠️ CRÍTICO - Antes de Producción

1. **NUNCA** hagas commit de `.env` - Ya está en `.gitignore`
2. **Rota las credenciales** expuestas anteriormente
3. Configura `DEBUG=False` en producción
4. Restringe `ALLOWED_HOSTS` a tu dominio real
5. Verifica que HTTPS está habilitado en Render.com

### Credenciales a Rotar

- [x] SECRET_KEY (generar nueva)
- [x] EMAIL_HOST_PASSWORD (nueva app password de Gmail)
- [ ] TRANSBANK credentials (si se están usando de producción)

## 🧪 Testing

```bash
pytest
```

_Nota: Suite de tests pendiente de implementación completa_

## 📊 Logging

Los logs se generan automáticamente en:

- `logs/tuniforme.log` - Log general (INFO y superior)
- `logs/error.log` - Solo errores (ERROR y superior)

Ver configuración completa en `settings.py` sección `LOGGING`.

## 🚀 Deployment en Render.com

### Variables de Entorno Requeridas

Configura en Render.com > Environment:

```
SECRET_KEY=<tu_secret_key>
DEBUG=False
ALLOWED_HOSTS=tuniforme.onrender.com
EMAIL_HOST_USER=<tu_email>
EMAIL_HOST_PASSWORD=<tu_app_password>
TRANSBANK_API_KEY=<commerce_code>
TRANSBANK_API_SECRET=<api_key>
TRANSBANK_ENVIRONMENT=production
DATABASE_URL=<postgresql_url>
```

### Build Command

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### Start Command

```bash
gunicorn tuniforme.wsgi:application
```

## ☁️ Deployment en Google Cloud Run (Recomendado)

### 🆓 **Tier Gratuito Disponible**

Cloud Run ofrece un generoso tier gratuito:

- **2 millones de peticiones/mes**
- **360,000 GB-segundos de memoria**
- **180,000 vCPU-segundos**

### Deployment Rápido (Opción 1)

```bash
# Script interactivo que hace todo automáticamente
./deploy_cloud_run.sh
```

El script te guiará para:

1. Configurar el proyecto GCP
2. Habilitar APIs necesarias
3. Crear Cloud SQL (o usar base de datos gratuita externa)
4. Construir y desplegar la aplicación
5. Configurar secrets seguros

### Deployment Manual (Opción 2)

Ver guía completa en: [DEPLOYMENT_CLOUD_RUN.md](DEPLOYMENT_CLOUD_RUN.md)

```bash
# 1. Habilitar APIs
gcloud services enable run.googleapis.com sql-component.googleapis.com

# 2. Construir imagen
gcloud builds submit --tag gcr.io/PROJECT_ID/tuniforme

# 3. Deploy
gcloud run deploy tuniforme \
    --image gcr.io/PROJECT_ID/tuniforme \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Opciones de Base de Datos para Cloud Run

| Opción                 | Costo/mes | Almacenamiento | Notas                             |
| ---------------------- | --------- | -------------- | --------------------------------- |
| **Supabase**           | $0        | 500 MB         | ✅ Recomendado para tier gratuito |
| **ElephantSQL**        | $0        | 20 MB          | Bueno para testing                |
| **Neon**               | $0        | 3 GB           | Excelente opción gratuita         |
| **Cloud SQL f1-micro** | ~$7       | 10 GB          | Mejor para producción             |

### Costo Estimado Total

**Con tier gratuito de Cloud Run + Supabase:**

- **$0/mes** para tráfico bajo-moderado (hasta 50k requests/mes)

**Excediendo tier gratuito:**

- Requests adicionales: ~$0.40 por millón
- Muy escalable según demanda

### Ventajas de Cloud Run

- ✅ **Escalado automático** (0 a N instancias)
- ✅ **HTTPS por defecto**
- ✅ **Pago por uso** (no pagas cuando no hay tráfico)
- ✅ **Tier gratuito generoso**
- ✅ **Deployment con zero-downtime**
- ✅ **Integración con Cloud SQL**
- ✅ **Logs centralizados**

## 📖 Documentación Adicional

- **Reporte de Estado**: Ver archivos generados en `.gemini/antigravity/brain/`
- **Mejoras Implementadas**: Ver `MEJORAS_IMPLEMENTADAS.md`
- **Mejoras Pendientes**: Ver documento de mejoras críticas

## 🛠️ Stack Tecnológico

- **Backend**: Django 5.1.3
- **API**: Django REST Framework 3.15.2
- **Base de Datos**: PostgreSQL (producción), SQLite (desarrollo)
- **Pagos**: Transbank SDK 5.0.0 (Webpay Plus)
- **Servidor**: Gunicorn 20.1.0
- **Archivos Estáticos**: WhiteNoise 6.8.2

## 👥 Soporte

Para dudas sobre la configuración de las mejoras implementadas:

1. Revisa `MEJORAS_IMPLEMENTADAS.md`
2. Revisa los logs en `logs/tuniforme.log`
3. Contacta al equipo de desarrollo

## 📝 Licencia

[Especificar licencia]

---

**Última actualización**: Diciembre 23, 2025  
**Versión**: 2.0 (Post-Hardening)

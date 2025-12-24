# 🚀 Guía de Deployment en Google Cloud Run

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Deployment Automático](#deployment-automático)
4. [Deployment Manual](#deployment-manual)
5. [Tier Gratuito de Cloud Run](#tier-gratuito)
6. [Configuración de Base de Datos](#base-de-datos)
7. [Monitoreo y Logs](#monitoreo)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Requisitos Previos

### 1. Google Cloud Platform Setup

1. **Crear cuenta de GCP:**

   - Ve a: https://cloud.google.com/
   - Activa el trial de $300 por 90 días (opcional pero recomendado)

2. **Crear un proyecto:**

   - Nombre sugerido: `tuniforme-prod`
   - Anota el Project ID

3. **Instalar Google Cloud SDK:**

   ```bash
   # Linux/Mac
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL

   # O descarga desde: https://cloud.google.com/sdk/docs/install
   ```

4. **Autenticarse:**
   ```bash
   gcloud auth login
   gcloud config set project TU_PROJECT_ID
   ```

### 2. Preparar Variables de Entorno

Edita tu archivo `.env` local:

```bash
nano .env
```

Asegúrate de tener configurado:

```env
SECRET_KEY=tu_secret_key_generada
DEBUG=False
ALLOWED_HOSTS=tuniforme-xxxx.run.app  # Se actualiza después del deployment
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
TRANSBANK_API_KEY=tu_commerce_code
TRANSBANK_API_SECRET=tu_api_key
TRANSBANK_ENVIRONMENT=integration  # o production
DATABASE_URL=postgresql://...  # Se configura después
```

---

## 🤖 Deployment Automático (Recomendado)

### Opción 1: Script Interactivo

```bash
./deploy_cloud_run.sh
```

El script te guiará paso a paso y:

- ✅ Habilitará las APIs necesarias
- ✅ Creará Cloud SQL (opcional)
- ✅ Construirá la imagen Docker
- ✅ Configurará secrets
- ✅ Desplegará a Cloud Run

---

## 🔧 Deployment Manual (Paso a Paso)

### 1. Habilitar APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Crear Cloud SQL (PostgreSQL)

**Opción A: Instancia f1-micro (Más económica - ~$7/mes)**

```bash
gcloud sql instances create tuniforme-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=TU_PASSWORD_SEGURO \
    --storage-type=HDD \
    --storage-size=10GB \
    --no-backup
```

**Opción B: Base de datos externa gratuita**

Alternativas gratuitas para desarrollo:

- **Supabase:** https://supabase.com (PostgreSQL gratuito)
- **ElephantSQL:** https://www.elephantsql.com (20MB gratis)
- **Neon:** https://neon.tech (3GB gratis)

```bash
# Si usas base de datos externa, solo necesitas el DATABASE_URL
# Ejemplo para Supabase:
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
```

### 3. Crear Base de Datos

```bash
# Solo si usaste Cloud SQL
gcloud sql databases create tuniforme --instance=tuniforme-db

# Obtener connection name
gcloud sql instances describe tuniforme-db --format="value(connectionName)"
# Resultado: project-id:region:instance-name
```

### 4. Construir y Subir Imagen

```bash
# Construir imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/tuniforme

# Verificar imagen
gcloud container images list
```

### 5. Configurar Secrets (Recomendado)

```bash
# Crear secrets para datos sensibles
echo "tu_secret_key" | gcloud secrets create tuniforme-secret-key --data-file=-
echo "tu_email_password" | gcloud secrets create tuniforme-email-password --data-file=-
echo "tu_transbank_secret" | gcloud secrets create tuniforme-transbank-secret --data-file=-

# Dar permisos al servicio de Cloud Run
PROJECT_NUMBER=$(gcloud projects describe TU_PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding tuniforme-secret-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding tuniforme-email-password \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding tuniforme-transbank-secret \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 6. Deploy a Cloud Run

```bash
# Reemplaza los valores según tu configuración

gcloud run deploy tuniforme \
    --image gcr.io/TU_PROJECT_ID/tuniforme \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DEBUG=False,EMAIL_HOST_USER=tu_email@gmail.com,TRANSBANK_API_KEY=tu_commerce_code,TRANSBANK_ENVIRONMENT=integration" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest,EMAIL_HOST_PASSWORD=tuniforme-email-password:latest,TRANSBANK_API_SECRET=tuniforme-transbank-secret:latest" \
    --add-cloudsql-instances TU_CONNECTION_NAME \
    --min-instances 0 \
    --max-instances 3 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --port 8080
```

### 7. Actualizar ALLOWED_HOSTS

```bash
# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe tuniforme --platform managed --region us-central1 --format "value(status.url)")

echo "Tu servicio está en: $SERVICE_URL"

# Actualizar deployment con ALLOWED_HOSTS correcto
gcloud run services update tuniforme \
    --region us-central1 \
    --update-env-vars "ALLOWED_HOSTS=$(echo $SERVICE_URL | sed 's|https://||')"
```

### 8. Ejecutar Migraciones

**Opción A: Usando Cloud Run Jobs (Recomendado)**

```bash
# Crear job para migraciones
gcloud run jobs create tuniforme-migrate \
    --image gcr.io/TU_PROJECT_ID/tuniforme \
    --region us-central1 \
    --set-env-vars "DEBUG=False,DATABASE_URL=tu_database_url" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest" \
    --add-cloudsql-instances TU_CONNECTION_NAME \
    --command "python,manage.py,migrate"

# Ejecutar migraciones
gcloud run jobs execute tuniforme-migrate --region us-central1
```

**Opción B: Manualmente vía Cloud Shell**

```bash
# Conectarse a Cloud SQL desde Cloud Shell
gcloud sql connect tuniforme-db --user=postgres

# En el shell de PostgreSQL:
\c tuniforme

# Luego ejecutar migraciones localmente apuntando a Cloud SQL
# (Requiere configurar Cloud SQL Proxy)
```

### 9. Crear Superusuario

```bash
# Opción 1: Crear job para createsuperuser
gcloud run jobs create tuniforme-createsuperuser \
    --image gcr.io/TU_PROJECT_ID/tuniforme \
    --region us-central1 \
    --set-env-vars "DEBUG=False,DATABASE_URL=tu_database_url,DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=admin@tuniforme.com,DJANGO_SUPERUSER_PASSWORD=cambiar123" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest" \
    --add-cloudsql-instances TU_CONNECTION_NAME \
    --command "python,manage.py,createsuperuser,--noinput"

# Ejecutar
gcloud run jobs execute tuniforme-createsuperuser --region us-central1
```

---

## 💰 Tier Gratuito de Cloud Run

### Límites Gratuitos Mensuales (Always Free)

| Recurso                   | Límite Gratuito      |
| ------------------------- | -------------------- |
| **Requests**              | 2 millones           |
| **CPU-segundos**          | 180,000              |
| **Memoria (GB-segundos)** | 360,000              |
| **Network Egress**        | 1 GB (Norte América) |

### Calculadora de Costos

Para Tuniforme con tráfico bajo-moderado:

**Configuración:**

- 512 MB RAM
- 1 vCPU
- Request duration: ~500ms
- Requests/mes: 50,000

**Costo estimado:** $0 (dentro del free tier)

**Si excedes el free tier:**

- Request adicional: ~$0.40 por millón
- CPU-segundo adicional: ~$0.00002400
- Memoria GB-segundo adicional: ~$0.00000250

### Optimización para Free Tier

1. **Min instances = 0:**

   - No cobro por idle time
   - Cold start de ~10 segundos (aceptable para tráfico bajo)

2. **Reducir memoria si es posible:**

   ```bash
   --memory 256Mi  # En vez de 512Mi
   ```

3. **Timeout apropiado:**

   ```bash
   --timeout 60  # En vez de 300
   ```

4. **Usar solo workers necesarios:**
   - Configurado en Dockerfile: `--workers 1 --threads 8`

---

## 💾 Configuración de Base de Datos

### Opción 1: Cloud SQL (PostgreSQL)

**Costos:**

- **db-f1-micro:** ~$7/mes (no free tier)
- **db-g1-small:** ~$25/mes

**Comando de creación:**

```bash
gcloud sql instances create tuniforme-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=PASSWORD \
    --storage-type=HDD \
    --storage-size=10GB \
    --no-backup  # Ahorra $0.08/GB/mes
```

**Obtener DATABASE_URL:**

```bash
# Para Cloud Run con Unix Socket:
postgresql://postgres:PASSWORD@/tuniforme?host=/cloudsql/PROJECT:REGION:INSTANCE
```

### Opción 2: Supabase (Gratis)

1. Crear cuenta en https://supabase.com
2. Crear nuevo proyecto
3. Copiar connection string:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### Opción 3: ElephantSQL (Gratis - 20MB)

1. Crear cuenta en https://www.elephantsql.com
2. Crear instancia "Tiny Turtle" (gratis)
3. Copiar URL de conexión

### Opción 4: Neon (Gratis - 3GB)

1. Crear cuenta en https://neon.tech
2. Crear proyecto
3. Copiar connection string

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Logs del servicio
gcloud run services logs tail tuniforme --region us-central1

# Logs de jobs
gcloud run jobs logs tail tuniforme-migrate --region us-central1

# Filtrar por nivel
gcloud run services logs tail tuniforme --log-filter "severity>=ERROR"
```

### Consola Web

1. Cloud Run: https://console.cloud.google.com/run
2. Logs Explorer: https://console.cloud.google.com/logs
3. Metrics: En la página del servicio > METRICS tab

### Alertas (Opcional)

Configurar alertas para:

- Errores 5xx
- Alto uso de memoria
- Latencia > 5 segundos

---

## 🐛 Troubleshooting

### Problema: "Module not found"

**Solución:** Verificar que `requirements.txt` está completo

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
# Rebuild y redeploy
```

### Problema: "Database connection failed"

**Solución 1:** Verificar CONNECTION_NAME

```bash
gcloud sql instances describe tuniforme-db --format="value(connectionName)"
```

**Solución 2:** Verificar que Cloud SQL está habilitado

```bash
gcloud run services update tuniforme \
    --add-cloudsql-instances CONNECTION_NAME
```

### Problema: "502 Bad Gateway"

**Causas comunes:**

1. App no escucha en PORT correcto

   - Verificar Dockerfile: `CMD exec gunicorn --bind :$PORT`

2. Timeout muy corto

   - Aumentar: `--timeout 300`

3. Memoria insuficiente
   - Aumentar: `--memory 1Gi`

### Problema: Cold Start lento

**Solución:** Usar min-instances (COSTO EXTRA)

```bash
gcloud run services update tuniforme --min-instances 1
```

### Ver logs de errores específicos:

```bash
gcloud run services logs read tuniforme \
    --region us-central1 \
    --limit 50 \
    --format json | grep ERROR
```

---

## 🔄 Actualizar Deployment

### Actualización Rápida

```bash
# 1. Build nueva imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/tuniforme

# 2. Deployment automático (si usas latest tag)
# Cloud Run detecta y actualiza automáticamente

# o manualmente:
gcloud run deploy tuniforme \
    --image gcr.io/TU_PROJECT_ID/tuniforme \
    --region us-central1
```

### Con Migraciones

```bash
# 1. Build
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/tuniforme

# 2. Ejecutar migraciones
gcloud run jobs execute tuniforme-migrate --region us-central1

# 3. Deploy
gcloud run deploy tuniforme \
    --image gcr.io/TU_PROJECT_ID/tuniforme \
    --region us-central1
```

---

## 📝 Checklist de Deployment

### Pre-Deployment

- [ ] `.env` configurado con credenciales reales
- [ ] `DEBUG=False` en producción
- [ ] SECRET_KEY generada y única
- [ ] Base de datos creada
- [ ] Transbank configurado (test o producción)
- [ ] Email configurado

### Durante Deployment

- [ ] APIs habilitadas en GCP
- [ ] Imagen Docker construida exitosamente
- [ ] Secrets configurados en Secret Manager
- [ ] Cloud SQL configurado (o DB externa)
- [ ] Servicio desplegado correctamente
- [ ] ALLOWED_HOSTS actualizado con URL real

### Post-Deployment

- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Archivos estáticos funcionando
- [ ] Email de prueba enviado
- [ ] Transacción de prueba realizada
- [ ] Logs verificados sin errores
- [ ] Backup configurado (opcional)

---

## 🎉 Conclusión

Con esta configuración, Tuniforme estará:

- ✅ Desplegado en Cloud Run (casi gratis o gratis)
- ✅ Con PostgreSQL (Cloud SQL o alternativa gratuita)
- ✅ Escalable automáticamente
- ✅ Con HTTPS por defecto
- ✅ Con secrets seguros
- ✅ Monitoreado con Cloud Logging

**URL típica:**

```
https://tuniforme-xxxxxxxxxx-uc.a.run.app
```

**Próximos pasos opcionales:**

- Configurar dominio personalizado
- Configurar CI/CD con Cloud Build
- Configurar Cloud CDN para archivos estáticos
- Configurar Cloud Storage para media files

---

**Documentación oficial:**

- Cloud Run: https://cloud.google.com/run/docs
- Cloud SQL: https://cloud.google.com/sql/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs

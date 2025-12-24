# Tuniforme - Deployment Status

## Archivos de Deployment Creados

### ✅ Configuración Docker

- `Dockerfile` - Optimizado para Cloud Run (Python 3.11, non-root user, PORT variable)
- `.dockerignore` - Reduce tamaño de imagen

### ✅ Scripts de Deployment

- `deploy_cloud_run.sh` - Script interactivo completo
- `cloudbuild.yaml` - CI/CD automático con Cloud Build (opcional)

### ✅ Documentación

- `DEPLOYMENT_CLOUD_RUN.md` - Guía completa paso a paso

## Opciones de Base de Datos

### Opción 1: Cloud SQL PostgreSQL (~$7/mes)

- Instancia db-f1-micro
- 10GB HDD
- Sin backups (opcional)

### Opción 2: Servicios Gratuitos

- **Supabase** (Recomendado) - PostgreSQL gratis, 500MB
- **ElephantSQL** - 20MB gratis
- **Neon** - 3GB gratis

## Costos Estimados

### Cloud Run (FREE TIER)

- 0-2M requests/mes: **GRATIS**
- CPU y memoria dentro de límites gratuitos
- Egress 1GB/mes: **GRATIS**

### Total estimado para tráfico bajo-moderado: **$0 - $7/mes**

## Próximo Paso

Ejecuta el script de deployment:

```bash
./deploy_cloud_run.sh
```

O sigue la guía manual en `DEPLOYMENT_CLOUD_RUN.md`

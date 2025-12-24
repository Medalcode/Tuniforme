#!/bin/bash
# deploy_cloud_run.sh - Script para desplegar Tuniforme en Google Cloud Run

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Deployment de Tuniforme a Cloud Run${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar que gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI no está instalado${NC}"
    echo "Instala gcloud desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI detectado${NC}"

# Verificar archivo .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: Archivo .env no encontrado${NC}"
    echo "Ejecuta: python3 setup.py"
    exit 1
fi

echo -e "${GREEN}✅ Archivo .env encontrado${NC}"

# Cargar variables de .env
export $(cat .env | grep -v '^#' | xargs)

# Solicitar información del proyecto
echo ""
echo -e "${YELLOW}📝 Configuración del proyecto GCP${NC}"
read -p "Project ID de GCP: " PROJECT_ID
read -p "Región (default: us-central1): " REGION
REGION=${REGION:-us-central1}
read -p "Nombre del servicio (default: tuniforme): " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-tuniforme}

# Configurar proyecto
echo ""
echo -e "${YELLOW}🔧 Configurando proyecto...${NC}"
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo ""
echo -e "${YELLOW}🔌 Habilitando APIs necesarias...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo -e "${GREEN}✅ APIs habilitadas${NC}"

# Preguntar si quiere crear Cloud SQL
echo ""
read -p "¿Crear instancia de Cloud SQL PostgreSQL? (y/n): " CREATE_DB
if [ "$CREATE_DB" = "y" ]; then
    echo ""
    echo -e "${YELLOW}💾 Creando Cloud SQL PostgreSQL...${NC}"
    read -p "Nombre de la instancia (default: tuniforme-db): " DB_INSTANCE
    DB_INSTANCE=${DB_INSTANCE:-tuniforme-db}
    
    read -p "Contraseña de PostgreSQL: " DB_PASSWORD
    
    echo "Creando instancia (esto puede tomar varios minutos)..."
    gcloud sql instances create $DB_INSTANCE \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$DB_PASSWORD \
        --storage-type=HDD \
        --storage-size=10GB \
        --no-backup
    
    # Crear base de datos
    echo "Creando base de datos tuniforme..."
    gcloud sql databases create tuniforme --instance=$DB_INSTANCE
    
    # Obtener connection name
    CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)")
    
    # Construir DATABASE_URL
    DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@//cloudsql/${CONNECTION_NAME}/tuniforme"
    
    echo -e "${GREEN}✅ Cloud SQL creado${NC}"
    echo "Connection Name: $CONNECTION_NAME"
else
    echo ""
    read -p "DATABASE_URL (PostgreSQL connection string): " DATABASE_URL
    read -p "Cloud SQL Connection Name (formato: project:region:instance): " CONNECTION_NAME
fi

# Build y push de la imagen
echo ""
echo -e "${YELLOW}🐳 Construyendo imagen Docker...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

echo -e "${GREEN}✅ Imagen construida y subida a Container Registry${NC}"

# Crear secrets en Secret Manager (más seguro que env vars)
echo ""
echo -e "${YELLOW}🔐 Configurando secrets...${NC}"

# Función para crear/actualizar secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if gcloud secrets describe $secret_name &> /dev/null; then
        echo "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    else
        echo "$secret_value" | gcloud secrets create $secret_name --data-file=-
    fi
}

create_or_update_secret "tuniforme-secret-key" "$SECRET_KEY"
create_or_update_secret "tuniforme-email-password" "$EMAIL_HOST_PASSWORD"
create_or_update_secret "tuniforme-transbank-secret" "$TRANSBANK_API_SECRET"

echo -e "${GREEN}✅ Secrets configurados${NC}"

# Deploy a Cloud Run
echo ""
echo -e "${YELLOW}🚀 Desplegando a Cloud Run...${NC}"

# Obtener URL que se generará
EXPECTED_URL="${SERVICE_NAME}-$(echo $PROJECT_ID | sed 's/[^a-z0-9-]/-/g')-${REGION//-}.a.run.app"

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "DEBUG=False,ALLOWED_HOSTS=${EXPECTED_URL},EMAIL_HOST_USER=${EMAIL_HOST_USER},TRANSBANK_API_KEY=${TRANSBANK_API_KEY},TRANSBANK_ENVIRONMENT=${TRANSBANK_ENVIRONMENT:-integration},DATABASE_URL=${DATABASE_URL}" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest,EMAIL_HOST_PASSWORD=tuniforme-email-password:latest,TRANSBANK_API_SECRET=tuniforme-transbank-secret:latest" \
    --add-cloudsql-instances $CONNECTION_NAME \
    --min-instances 0 \
    --max-instances 3 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --port 8080

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ¡Deployment completado!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "🌐 URL del servicio: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo "1. Ejecutar migraciones (primera vez):"
echo "   gcloud run jobs execute tuniforme-migrate --region $REGION"
echo ""
echo "2. Crear superusuario (conectarse al contenedor):"
echo "   gcloud run services proxy $SERVICE_NAME --region $REGION"
echo ""
echo "3. Actualizar TRANSBANK_RETURN_URL en .env:"
echo "   TRANSBANK_RETURN_URL=${SERVICE_URL}/pedidos/transaction/commit"
echo ""
echo "4. Si necesitas actualizar el servicio:"
echo "   ./deploy_cloud_run.sh"
echo ""
echo -e "${GREEN}🎉 ¡Tuniforme está en vivo!${NC}"

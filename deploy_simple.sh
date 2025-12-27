#!/bin/bash
# deploy_simple.sh - Deployment simplificado guiado para Cloud Run

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Tuniforme a Cloud Run     ║${NC}"
echo -e "${GREEN}║  Versión Simplificada                 ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo ""

# Paso 1: Verificar autenticación
echo -e "${YELLOW}Paso 1: Verificando autenticación...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}No estás autenticado en GCP${NC}"
    echo "Ejecuta: gcloud auth login"
    echo "Luego vuelve a ejecutar este script"
    exit 1
fi

ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo -e "${GREEN}✓ Autenticado como: $ACTIVE_ACCOUNT${NC}"

# Paso 2: Obtener/configurar proyecto
echo ""
echo -e "${YELLOW}Paso 2: Configurando proyecto...${NC}"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -z "$CURRENT_PROJECT" ] || [ "$CURRENT_PROJECT" = "(unset)" ]; then
    echo "No hay proyecto configurado."
    read -p "Ingresa el Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
else
    echo -e "Proyecto actual: ${GREEN}$CURRENT_PROJECT${NC}"
    read -p "¿Usar este proyecto? (y/n): " USE_CURRENT
    if [ "$USE_CURRENT" != "y" ]; then
        read -p "Ingresa el nuevo Project ID: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    else
        PROJECT_ID=$CURRENT_PROJECT
    fi
fi

echo -e "${GREEN}✓ Proyecto configurado: $PROJECT_ID${NC}"

# Paso 3: Habilitar APIs
echo ""
echo -e "${YELLOW}Paso 3: Habilitando APIs necesarias (esto puede tardar)...${NC}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
echo -e "${GREEN}✓ APIs habilitadas${NC}"

# Paso 4: Configurar región
echo ""
echo -e "${YELLOW}Paso 4: Configurando región...${NC}"
read -p "Región (presiona Enter para us-central1): " REGION
REGION=${REGION:-us-central1}
echo -e "${GREEN}✓ Región configurada: $REGION${NC}"

# Paso 5: Cargar variables del .env
echo ""
echo -e "${YELLOW}Paso 5: Cargando variables de .env...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env no encontrado${NC}"
    exit 1
fi
export $(cat .env | grep -v '^#' | xargs)
echo -e "${GREEN}✓ Variables cargadas${NC}"

# Paso 6: Crear secrets
echo ""
echo -e "${YELLOW}Paso 6: Configurando secrets en Secret Manager...${NC}"

create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if gcloud secrets describe $secret_name &> /dev/null 2>&1; then
        echo "  Actualizando secret: $secret_name"
        echo "$secret_value" | gcloud secrets versions add $secret_name --data-file=- --quiet
    else
        echo "  Creando secret: $secret_name"
        echo "$secret_value" | gcloud secrets create $secret_name --data-file=- --quiet
    fi
}

create_or_update_secret "tuniforme-secret-key" "$SECRET_KEY"
create_or_update_secret "tuniforme-email-password" "$EMAIL_HOST_PASSWORD"
create_or_update_secret "tuniforme-transbank-secret" "$TRANSBANK_API_SECRET"

echo -e "${GREEN}✓ Secrets configurados${NC}"

# Paso 7: Dar permisos a Cloud Run
echo ""
echo -e "${YELLOW}Paso 7: Configurando permisos...${NC}"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

for secret in tuniforme-secret-key tuniforme-email-password tuniforme-transbank-secret; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet 2>/dev/null || true
done

echo -e "${GREEN}✓ Permisos configurados${NC}"

# Paso 8: Base de datos
echo ""
echo -e "${YELLOW}Paso 8: Configuración de base de datos${NC}"
echo "Opciones:"
echo "  1) Supabase (GRATIS - Recomendado)"
echo "  2) Neon (GRATIS)"
echo "  3) ElephantSQL (GRATIS - 20MB)"
echo "  4) Cloud SQL (~$7/mes)"
echo "  5) Ya tengo DATABASE_URL"
read -p "Elige opción (1-5): " DB_OPTION

case $DB_OPTION in
    1)
        echo ""
        echo "=== Configurar Supabase ==="
        echo "1. Ve a: https://supabase.com"
        echo "2. Crea una cuenta gratis"
        echo "3. Crea un nuevo proyecto"
        echo "4. Ve a Settings > Database"
        echo "5. Copia la 'Connection string' con 'Connection pooling'"
        echo ""
        read -p "Pega aquí tu DATABASE_URL: " DATABASE_URL
        ;;
    2)
        echo ""
        echo "=== Configurar Neon ==="
        echo "1. Ve a: https://neon.tech"
        echo "2. Crea una cuenta gratis"
        echo "3. Crea un nuevo proyecto"
        echo "4. Copia la connection string"
        echo ""
        read -p "Pega aquí tu DATABASE_URL: " DATABASE_URL
        ;;
    3)
        echo ""
        echo "=== Configurar ElephantSQL ==="
        echo "1. Ve a: https://www.elephantsql.com"
        echo "2. Crea una cuenta gratis"
        echo "3. Crea instancia 'Tiny Turtle'"
        echo "4. Copia la URL"
        echo ""
        read -p "Pega aquí tu DATABASE_URL: " DATABASE_URL
        ;;
    4)
        echo ""
        echo "Creando Cloud SQL (esto tardará varios minutos)..."
        read -p "Contraseña para PostgreSQL: " DB_PASSWORD
        
        gcloud sql instances create tuniforme-db \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region=$REGION \
            --root-password=$DB_PASSWORD \
            --storage-type=HDD \
            --storage-size=10GB \
            --no-backup \
            --quiet
        
        gcloud sql databases create tuniforme --instance=tuniforme-db --quiet
        
        CONNECTION_NAME=$(gcloud sql instances describe tuniforme-db --format="value(connectionName)")
        DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@//cloudsql/${CONNECTION_NAME}/tuniforme"
        ;;
    5)
        read -p "Pega aquí tu DATABASE_URL: " DATABASE_URL
        ;;
esac

echo -e "${GREEN}✓ Base de datos configurada${NC}"

# Paso 9: Build de la imagen
echo ""
echo -e "${YELLOW}Paso 9: Construyendo imagen Docker (puede tardar 3-5 minutos)...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/tuniforme --quiet

echo -e "${GREEN}✓ Imagen construida y subida${NC}"

# Paso 10: Deploy a Cloud Run
echo ""
echo -e "${YELLOW}Paso 10: Desplegando a Cloud Run...${NC}"

# Obtener URL esperada
SERVICE_URL_SUFFIX="${PROJECT_ID//[^a-z0-9-]/-}-${REGION//-}.a.run.app"

gcloud run deploy tuniforme \
    --image gcr.io/$PROJECT_ID/tuniforme \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "DEBUG=False,EMAIL_HOST_USER=${EMAIL_HOST_USER},TRANSBANK_API_KEY=${TRANSBANK_API_KEY},TRANSBANK_ENVIRONMENT=${TRANSBANK_ENVIRONMENT:-integration},DATABASE_URL=${DATABASE_URL}" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest,EMAIL_HOST_PASSWORD=tuniforme-email-password:latest,TRANSBANK_API_SECRET=tuniforme-transbank-secret:latest" \
    --min-instances 0 \
    --max-instances 3 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --port 8080 \
    --quiet

# Obtener URL real
SERVICE_URL=$(gcloud run services describe tuniforme --platform managed --region $REGION --format "value(status.url)")
SERVICE_HOST=$(echo $SERVICE_URL | sed 's|https://||')

echo -e "${GREEN}✓ Servicio desplegado${NC}"

# Paso 11: Actualizar ALLOWED_HOSTS
echo ""
echo -e "${YELLOW}Paso 11: Actualizando ALLOWED_HOSTS...${NC}"
gcloud run services update tuniforme \
    --region $REGION \
    --update-env-vars "ALLOWED_HOSTS=${SERVICE_HOST}" \
    --quiet

echo -e "${GREEN}✓ ALLOWED_HOSTS actualizado${NC}"

# Paso 12: Ejecutar migraciones
echo ""
echo -e "${YELLOW}Paso 12: Ejecutando migraciones...${NC}"

# Crear job para migraciones
gcloud run jobs create tuniforme-migrate \
    --image gcr.io/$PROJECT_ID/tuniforme \
    --region $REGION \
    --set-env-vars "DEBUG=False,DATABASE_URL=${DATABASE_URL}" \
    --set-secrets "SECRET_KEY=tuniforme-secret-key:latest" \
    --command "python,manage.py,migrate" \
    --quiet 2>/dev/null || true

# Ejecutar migraciones
echo "Ejecutando migrate..."
gcloud run jobs execute tuniforme-migrate --region $REGION --wait --quiet

echo -e "${GREEN}✓ Migraciones ejecutadas${NC}"

# Resultado final
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✓ DEPLOYMENT COMPLETADO ✓         ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo ""
echo -e "🌐 URL del servicio: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo ""
echo "1. Crear superusuario:"
echo "   gcloud run jobs create tuniforme-createsuperuser \\"
echo "     --image gcr.io/$PROJECT_ID/tuniforme \\"
echo "     --region $REGION \\"
echo "     --set-env-vars DATABASE_URL='${DATABASE_URL}',DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=admin@tuniforme.com,DJANGO_SUPERUSER_PASSWORD=ChangeMe123 \\"
echo "     --set-secrets SECRET_KEY=tuniforme-secret-key:latest \\"
echo "     --command python,manage.py,createsuperuser,--noinput"
echo ""
echo "   gcloud run jobs execute tuniforme-createsuperuser --region $REGION"
echo ""
echo "2. Accede al admin:"
echo "   ${SERVICE_URL}/admin"
echo "   Usuario: admin"
echo "   Password: ChangeMe123 (¡CÁMBIALO!)"
echo ""
echo "3. Actualiza TRANSBANK_RETURN_URL en GCP:"
echo "   ${SERVICE_URL}/pedidos/transaction/commit"
echo ""
echo -e "${GREEN}🎉 ¡Tuniforme está en vivo!${NC}"
echo ""

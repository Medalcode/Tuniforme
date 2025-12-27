#!/bin/bash
# Quick deployment script for frontend changes

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying Frontend Changes to Cloud Run${NC}"
echo ""

# Project details
PROJECT_ID="tuniforme-prod"
REGION="us-central1"
SERVICE="tuniforme"

echo -e "${YELLOW}1. Building new image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE --quiet

echo -e "${GREEN}✓ Image built${NC}"
echo ""

echo -e "${YELLOW}2. Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE \
    --image gcr.io/$PROJECT_ID/$SERVICE \
    --region $REGION \
    --quiet

echo -e "${GREEN}✓ Deployed${NC}"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE --platform managed --region $REGION --format "value(status.url)")

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "🌐 URL: ${GREEN}$SERVICE_URL${NC}"
echo ""
echo -e "📝 Changes deployed:"
echo "  - Modern design system (modern.css)"
echo "  - Renovated homepage with hero section"
echo "  - Improved product catalog with filters"
echo ""
echo -e "${YELLOW}⏭️  Next: Visit the site and check the new design!${NC}"

#!/bin/bash

# Deploy NourishAI Frontend to Google Cloud Run
# Usage: ./deploy-frontend.sh [PROJECT_ID] [REGION] [BACKEND_URL]

set -e

# Configuration
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}
BACKEND_URL=${3:-"http://localhost:8000"}
SERVICE_NAME="nourishai-frontend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying NourishAI Frontend to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Backend URL: $BACKEND_URL"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "   Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the container image
echo "🏗️  Building container image..."
gcloud builds submit --tag $IMAGE_NAME -f Dockerfile.frontend .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars "API_URL=$BACKEND_URL"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo ""
echo "✅ Frontend deployed successfully!"
echo "   Service URL: $SERVICE_URL"
echo ""
echo "🎉 Deployment complete!"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $SERVICE_URL"
echo ""
echo "💡 Open the frontend in your browser:"
echo "   $SERVICE_URL"
echo ""

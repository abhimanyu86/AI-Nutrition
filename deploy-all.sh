#!/bin/bash

# Deploy complete NourishAI Platform to Google Cloud Run
# Usage: ./deploy-all.sh [PROJECT_ID] [REGION]

set -e

# Configuration
PROJECT_ID=${1:-"your-gcp-project-id"}
REGION=${2:-"us-central1"}

echo "🚀 Deploying Complete NourishAI Platform to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "   Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Make scripts executable
chmod +x deploy-backend.sh
chmod +x deploy-frontend.sh

# Deploy backend first
echo "📦 Step 1/2: Deploying Backend..."
echo "════════════════════════════════════════"
./deploy-backend.sh $PROJECT_ID $REGION

# Get backend URL
BACKEND_URL=$(gcloud run services describe nourishai-backend --region $REGION --format 'value(status.url)')

echo ""
echo "⏳ Waiting 10 seconds for backend to be ready..."
sleep 10

# Deploy frontend
echo ""
echo "📦 Step 2/2: Deploying Frontend..."
echo "════════════════════════════════════════"
./deploy-frontend.sh $PROJECT_ID $REGION $BACKEND_URL

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe nourishai-frontend --region $REGION --format 'value(status.url)')

echo ""
echo "════════════════════════════════════════════════════════"
echo "🎉 NourishAI Platform Deployed Successfully!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📍 Service URLs:"
echo "   Backend API:  $BACKEND_URL"
echo "   Frontend App: $FRONTEND_URL"
echo ""
echo "🧪 Test the deployment:"
echo "   curl $BACKEND_URL"
echo "   open $FRONTEND_URL"
echo ""
echo "📊 Monitor your services:"
echo "   gcloud run services list --region $REGION"
echo ""
echo "💰 Estimated costs:"
echo "   - Pay per request (very affordable for demos)"
echo "   - Free tier: 2M requests/month"
echo "   - Auto-scales to zero when not in use"
echo ""

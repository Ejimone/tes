#!/bin/bash

# WhatsApp DApp - Google Cloud Deployment Script
# This script deploys the FastAPI backend to Google Cloud Run

set -e

echo "🚀 WhatsApp DApp - Google Cloud Deployment"
echo "=========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK (gcloud) is not installed."
    echo "📥 Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Variables
PROJECT_ID=""
SERVICE_NAME="whatsapp-dapp-backend"
REGION="us-central1"
CONTRACT_ADDRESS=""
BLOCKCHAIN_RPC_URL=""

# Get project ID
echo "📋 Step 1: Configure Google Cloud Project"
echo ""
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID is required!"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID
echo "✅ Project set to: $PROJECT_ID"
echo ""

# Get contract address
echo "📋 Step 2: Configure Smart Contract"
echo ""
read -p "Enter your deployed contract address: " CONTRACT_ADDRESS

if [ -z "$CONTRACT_ADDRESS" ]; then
    echo "❌ Contract address is required!"
    exit 1
fi

# Get blockchain RPC URL
echo ""
read -p "Enter blockchain RPC URL (or press Enter for default testnet): " BLOCKCHAIN_RPC_URL

if [ -z "$BLOCKCHAIN_RPC_URL" ]; then
    BLOCKCHAIN_RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_KEY"
    echo "⚠️  Using default: $BLOCKCHAIN_RPC_URL"
    echo "⚠️  You'll need to update this with your actual RPC URL"
fi

echo ""
echo "📦 Step 3: Building and Deploying to Cloud Run"
echo ""

# Copy contract ABI to backend
echo "📄 Copying contract ABI..."
mkdir -p backend/build/contracts
cp build/contracts/Whatsapp.json backend/build/contracts/ 2>/dev/null || echo "⚠️  Contract ABI not found, make sure it's available"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source ./backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars CONTRACT_ADDRESS=$CONTRACT_ADDRESS,BLOCKCHAIN_RPC_URL=$BLOCKCHAIN_RPC_URL \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "📍 Service URL: $SERVICE_URL"
echo "📚 API Docs: $SERVICE_URL/docs"
echo "💚 Health Check: $SERVICE_URL/api/v1/health"
echo ""
echo "🔧 Configuration:"
echo "   Contract Address: $CONTRACT_ADDRESS"
echo "   RPC URL: $BLOCKCHAIN_RPC_URL"
echo "   Region: $REGION"
echo ""
echo "📝 Next Steps:"
echo "   1. Test your API: curl $SERVICE_URL/api/v1/health"
echo "   2. Visit API docs: $SERVICE_URL/docs"
echo "   3. Update frontend to use: $SERVICE_URL"
echo ""
echo "✨ Your backend is now live!"

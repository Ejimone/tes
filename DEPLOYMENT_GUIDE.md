# 🚀 Google Cloud Deployment Guide

This guide will help you deploy your WhatsApp DApp backend to Google Cloud Run in minutes.

## 📋 Prerequisites

1. **Google Cloud Account** - Sign up at https://cloud.google.com
2. **Google Cloud SDK** - Install from https://cloud.google.com/sdk/docs/install
3. **Project Setup** - Create a new project in Google Cloud Console
4. **Billing Enabled** - Enable billing for your project (Cloud Run has a generous free tier)

## 🎯 Quick Deployment (3 Steps)

### Step 1: Install Google Cloud SDK (if not installed)

**macOS:**

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

**Already installed? Verify:**

```bash
gcloud --version
```

### Step 2: Authenticate and Enable APIs

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Deploy Your Backend

Make the deployment script executable and run it:

```bash
chmod +x deploy-to-gcloud.sh
./deploy-to-gcloud.sh
```

The script will ask you for:

1. **Google Cloud Project ID** - Your project ID from console
2. **Contract Address** - Your deployed smart contract address
3. **Blockchain RPC URL** - Your Ethereum node RPC URL

---

## 🔧 Configuration Options

### Option 1: Using a Public Testnet (Recommended for Development)

**Sepolia Testnet (via Infura):**

```
Contract: Deploy to Sepolia using Brownie
RPC URL: https://sepolia.infura.io/v3/YOUR_INFURA_KEY
```

**Get Infura Key:**

1. Sign up at https://infura.io
2. Create new project
3. Copy project ID
4. Use: `https://sepolia.infura.io/v3/YOUR_PROJECT_ID`

**Sepolia Testnet (via Alchemy):**

```
RPC URL: https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
```

### Option 2: Using Your Own Node

If you have a hosted Ethereum node:

```
RPC URL: https://your-node-url.com:8545
```

### Option 3: Keep Using Ganache (Not Recommended for Production)

You can tunnel your local Ganache to make it accessible:

```bash
# Using ngrok
ngrok http 7545

# Then use the ngrok URL as your RPC_URL
```

---

## 📝 Manual Deployment Steps (Alternative)

If you prefer manual deployment:

### 1. Copy Contract ABI

```bash
mkdir -p backend/build/contracts
cp build/contracts/Whatsapp.json backend/build/contracts/
```

### 2. Deploy to Cloud Run

```bash
cd backend

gcloud run deploy whatsapp-dapp-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars CONTRACT_ADDRESS=0xYourContractAddress,BLOCKCHAIN_RPC_URL=https://your-rpc-url \
  --memory 512Mi \
  --cpu 1 \
  --port 8080
```

### 3. Get Service URL

```bash
gcloud run services describe whatsapp-dapp-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## ✅ Verify Deployment

After deployment, test your API:

```bash
# Replace with your actual service URL
SERVICE_URL="https://whatsapp-dapp-backend-xxxxx-uc.a.run.app"

# Test health endpoint
curl $SERVICE_URL/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "web3_connected": true,
#   "contract_initialized": true,
#   "network": "Sepolia Testnet",
#   "contract_address": "0x..."
# }

# Visit API documentation
open $SERVICE_URL/docs
```

---

## 🔒 Security Best Practices

### 1. Restrict CORS Origins

Update after deploying frontend:

```bash
gcloud run services update whatsapp-dapp-backend \
  --update-env-vars ALLOWED_ORIGINS=https://your-frontend-domain.com \
  --region us-central1
```

### 2. Add Authentication (Optional)

For production, consider adding authentication:

```bash
gcloud run services update whatsapp-dapp-backend \
  --no-allow-unauthenticated \
  --region us-central1
```

### 3. Monitor Your Service

```bash
# View logs
gcloud run services logs read whatsapp-dapp-backend \
  --region us-central1

# View metrics in Console
gcloud run services describe whatsapp-dapp-backend \
  --region us-central1
```

---

## 💰 Cost Estimation

**Cloud Run Pricing (as of 2025):**

- **Free Tier**: 2 million requests/month, 360,000 GB-seconds/month
- **Paid**: ~$0.00002400 per request, ~$0.00001650 per GB-second

**Estimated Monthly Cost for Low Traffic:**

- 10,000 requests/month: **FREE**
- 100,000 requests/month: **~$2-5**
- 1,000,000 requests/month: **~$20-30**

---

## 🐛 Troubleshooting

### Error: "Contract not initialized"

**Solution:**

```bash
# Verify environment variables
gcloud run services describe whatsapp-dapp-backend \
  --region us-central1 \
  --format 'value(spec.template.spec.containers[0].env)'

# Update contract address
gcloud run services update whatsapp-dapp-backend \
  --update-env-vars CONTRACT_ADDRESS=0xYourNewAddress \
  --region us-central1
```

### Error: "Web3 connection failed"

**Solution:**

- Verify your RPC URL is accessible
- Check if you need an API key
- Test RPC URL locally first:

```bash
curl -X POST YOUR_RPC_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Error: "Module not found"

**Solution:**

```bash
# Rebuild with dependencies
gcloud run deploy whatsapp-dapp-backend \
  --source ./backend \
  --region us-central1
```

---

## 🔄 Update Deployment

To update your backend after code changes:

```bash
# Simple update
./deploy-to-gcloud.sh

# Or manually
cd backend
gcloud run deploy whatsapp-dapp-backend \
  --source . \
  --region us-central1
```

---

## 📊 View Your Service

**Google Cloud Console:**

1. Go to https://console.cloud.google.com
2. Navigate to Cloud Run
3. Click on `whatsapp-dapp-backend`
4. View metrics, logs, and configuration

**CLI:**

```bash
# Service details
gcloud run services describe whatsapp-dapp-backend --region us-central1

# Recent logs
gcloud run services logs tail whatsapp-dapp-backend --region us-central1

# Metrics
gcloud run services list
```

---

## 🎉 Next Steps

After successful deployment:

1. ✅ **Save Your Service URL** - You'll need it for frontend
2. ✅ **Test All Endpoints** - Visit `/docs` for interactive testing
3. ✅ **Deploy to Testnet** - Deploy your contract to Sepolia/Goerli
4. ✅ **Start Frontend Development** - Build React frontend with Web3 integration
5. ✅ **Set up CI/CD** - Automate deployments with GitHub Actions

---

## 📞 Support Resources

- **Google Cloud Run Docs**: https://cloud.google.com/run/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Web3.py Docs**: https://web3py.readthedocs.io

---

**Your backend is now ready for production! 🚀**

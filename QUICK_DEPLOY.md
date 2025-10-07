# ⚡ Quick Deploy to Google Cloud

## 🚀 Deploy in 3 Commands

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your project
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy
./deploy-to-gcloud.sh
```

---

## 📋 What You Need

Before running the deployment:

1. **Google Cloud Project ID**

   - Create at: https://console.cloud.google.com
   - Find it: Console → Select Project → Copy Project ID

2. **Contract Address**

   - From local: Check `backend/deployment_info.json`
   - From testnet: Deploy to Sepolia first

3. **RPC URL** (Choose one):
   - **Infura**: `https://sepolia.infura.io/v3/YOUR_KEY` (Get key at infura.io)
   - **Alchemy**: `https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY` (Get key at alchemy.com)
   - **Local (testing)**: Use ngrok to tunnel Ganache

---

## 🎯 Example Deployment

```bash
# When script asks for inputs:

Enter your Google Cloud Project ID: whatsapp-dapp-12345

Enter your deployed contract address: 0xa2691703072E2821b9EE1698F05309289FA226c1

Enter blockchain RPC URL: https://sepolia.infura.io/v3/abc123def456

# Wait for deployment... ☕

# Output:
🎉 Deployment Complete!
📍 Service URL: https://whatsapp-dapp-backend-xxxxx-uc.a.run.app
📚 API Docs: https://whatsapp-dapp-backend-xxxxx-uc.a.run.app/docs
```

---

## ✅ Test After Deployment

```bash
# Copy your service URL from deployment output
SERVICE_URL="https://whatsapp-dapp-backend-xxxxx-uc.a.run.app"

# Test health
curl $SERVICE_URL/api/v1/health

# Open API docs in browser
open $SERVICE_URL/docs
```

---

## 🔧 Update Environment Variables Later

```bash
gcloud run services update whatsapp-dapp-backend \
  --update-env-vars CONTRACT_ADDRESS=0xNewAddress \
  --region us-central1
```

---

## 💡 Pro Tips

1. **Free Tier**: First 2M requests/month are FREE
2. **Logs**: View in Console → Cloud Run → Your Service → Logs
3. **Metrics**: Monitor requests, latency, errors in Console
4. **Redeploy**: Just run `./deploy-to-gcloud.sh` again

---

**Ready? Run:** `./deploy-to-gcloud.sh` 🚀

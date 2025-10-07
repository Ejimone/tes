# 🚀 Quick Start Guide - WhatsApp DApp Backend

This guide will help you get your WhatsApp DApp backend up and running in minutes!

## 📝 Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Ganache running on port 7545
- [ ] Brownie installed (`pip install eth-brownie`)
- [ ] Project dependencies installed

## 🎯 Step-by-Step Setup

### Step 1: Start Ganache

```bash
# Start Ganache CLI
ganache-cli

# OR use Ganache GUI on port 7545
```

**Verify**: You should see accounts with ETH balances displayed.

---

### Step 2: Deploy Contract & Auto-Configure Backend

Run the automated deployment script:

```bash
# From project root directory
brownie run scripts/deploy_for_backend.py --network ganache
```

**What this does**:

- ✅ Deploys the WhatsApp smart contract
- ✅ Automatically updates `CONTRACT_ADDRESS` in backend files
- ✅ Registers 3 test users (Alice, Bob, Charlie)
- ✅ Saves deployment info to `deployment_info.json`
- ✅ Displays test account private keys for API testing

**Example Output**:

```
✅ Contract deployed successfully!
📍 Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
✅ Updated Registrations.py
✅ Updated chatservices.py
```

---

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

### Step 4: Start the FastAPI Server

```bash
# From the backend directory
python main.py
```

**Expected Output**:

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### Step 5: Test the API

#### Option A: Use Interactive Docs (Recommended)

Open your browser and go to:

```
http://localhost:8000/docs
```

You'll see a beautiful Swagger UI with all available endpoints!

#### Option B: Use cURL

**Health Check**:

```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response**:

```json
{
  "status": "healthy",
  "web3_connected": true,
  "contract_initialized": true,
  "network": "Ganache Local",
  "contract_address": "0x5FbDB..."
}
```

---

## 🧪 Testing with Sample Data

After running `deploy_for_backend.py`, you'll have 3 test users registered. Use their addresses and private keys for testing.

### Example: Send a Message

```bash
curl -X POST http://localhost:8000/api/v1/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "to_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "content": "Hello from the API!",
    "is_media": false,
    "private_key": "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
  }'
```

### Example: Get Chat Messages

```bash
curl -X POST http://localhost:8000/api/v1/messages/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user1_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "user2_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
  }'
```

---

## 📊 API Endpoints Overview

### User Management

| Method | Endpoint                         | Description            |
| ------ | -------------------------------- | ---------------------- |
| POST   | `/api/v1/users/register`         | Register new user      |
| GET    | `/api/v1/users/{address}`        | Get user details       |
| GET    | `/api/v1/users/{address}/exists` | Check if user exists   |
| PUT    | `/api/v1/users/status`           | Update user status     |
| PUT    | `/api/v1/users/profile-picture`  | Update profile picture |
| POST   | `/api/v1/users/block`            | Block a user           |

### Messaging

| Method | Endpoint                  | Description          |
| ------ | ------------------------- | -------------------- |
| POST   | `/api/v1/messages/send`   | Send a message       |
| POST   | `/api/v1/messages/chat`   | Get chat messages    |
| POST   | `/api/v1/messages/read`   | Mark message as read |
| DELETE | `/api/v1/messages/delete` | Delete a message     |

### Groups

| Method | Endpoint                             | Description        |
| ------ | ------------------------------------ | ------------------ |
| POST   | `/api/v1/groups/create`              | Create a group     |
| GET    | `/api/v1/groups/user/{address}`      | Get user's groups  |
| POST   | `/api/v1/groups/messages/send`       | Send group message |
| GET    | `/api/v1/groups/{group_id}/messages` | Get group messages |
| POST   | `/api/v1/groups/leave`               | Leave a group      |

---

## 🔍 Verification Checklist

After setup, verify everything is working:

- [ ] Ganache is running and accessible
- [ ] Contract is deployed (check deployment_info.json)
- [ ] Backend server is running on port 8000
- [ ] Health check returns "healthy" status
- [ ] Can access Swagger docs at /docs
- [ ] Test users are registered
- [ ] Can send and receive messages

---

## 🐛 Common Issues & Solutions

### Issue: "Contract not initialized"

**Solution**:

```bash
# Re-run deployment script
brownie run scripts/deploy_for_backend.py --network ganache
```

### Issue: "Web3 connection failed"

**Solution**:

1. Check if Ganache is running: `http://127.0.0.1:7545`
2. Restart Ganache
3. Verify port 7545 is not blocked

### Issue: "Module not found" errors

**Solution**:

```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Transaction failed - insufficient funds"

**Solution**:

- Use Ganache accounts (they come pre-funded with 100 ETH)
- Get account private keys from Ganache

### Issue: Port 8000 already in use

**Solution**:

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
uvicorn main:app --port 8001
```

---

## 📁 Project Structure

```
whatsapp/
├── contracts/
│   └── Whatsapp.sol          # Smart contract
├── scripts/
│   ├── deploy.py             # Original deployment script
│   ├── deploy_for_backend.py # Auto-config deployment
│   └── Message.py            # Message utilities
├── backend/
│   ├── main.py              # FastAPI application
│   ├── Registrations.py     # User & messaging endpoints
│   ├── chatservices.py      # Groups & profile endpoints
│   ├── requirements.txt     # Dependencies
│   ├── deployment_info.json # Auto-generated after deployment
│   └── README.md            # Detailed documentation
├── tests/
│   └── demo-tests.py        # Comprehensive tests
└── FUNCTIONS_REFERENCE.md   # Complete API reference
```

---

## 🎓 Next Steps

1. **Test All Endpoints**: Use Swagger UI to test each endpoint
2. **Build Frontend**: Create a React/Vue app to interact with the API
3. **Add Features**: Implement real-time messaging, notifications
4. **Deploy**: Move to testnet (Sepolia, Goerli) then mainnet

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **API Information**: http://localhost:8000/api/v1/info
- **Functions Reference**: `FUNCTIONS_REFERENCE.md`
- **Backend README**: `backend/README.md`

---

## 🎉 You're All Set!

Your WhatsApp DApp backend is now running!

**Test it out**:

1. Visit http://localhost:8000/docs
2. Try the "Register User" endpoint
3. Send some messages
4. Create a group chat

**Happy Building! 🚀**

---

## 💡 Pro Tips

1. **Save Test Accounts**: Keep the private keys from `deploy_for_backend.py` output
2. **Use Postman**: Import the API endpoints for easier testing
3. **Monitor Logs**: Watch the FastAPI console for debugging
4. **Check Ganache**: Monitor transactions in Ganache UI
5. **Read the Docs**: Check `FUNCTIONS_REFERENCE.md` for detailed function info

---

_For issues or questions, check the troubleshooting section or review the test files._

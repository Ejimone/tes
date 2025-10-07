# WhatsApp DApp Backend API

A decentralized WhatsApp clone built on Ethereum blockchain with FastAPI backend.

## 🚀 Features

- **User Management**: Register users, update profiles, check user status
- **Direct Messaging**: Send, read, and delete messages between users
- **Group Chats**: Create groups, send group messages, manage members
- **Profile Management**: Update status, profile pictures
- **User Privacy**: Block users, archive chats

## 📋 Prerequisites

- Python 3.8+
- Ganache (for local blockchain)
- Brownie (for smart contract deployment)
- Node.js & npm (optional, for frontend)

## 🛠️ Installation

### 1. Install Python Dependencies

```bash
# Navigate to the backend directory
cd backend

# Install required packages
pip install fastapi uvicorn web3 pydantic python-multipart
```

### 2. Deploy Smart Contract

First, deploy your WhatsApp smart contract using Brownie:

```bash
# From the project root directory
brownie run scripts/deploy.py --network ganache
```

After deployment, you'll get a contract address. **Copy this address!**

### 3. Configure Backend

Open both `Registrations.py` and `chatservices.py` and update the `CONTRACT_ADDRESS` variable:

```python
# In Registrations.py and chatservices.py
CONTRACT_ADDRESS = "0xYourContractAddressHere"  # Replace with your deployed contract address
```

### 4. Start Ganache

Make sure Ganache is running on `http://127.0.0.1:7545`

```bash
# If using Ganache CLI
ganache-cli

# Or start Ganache GUI and ensure it's on port 7545
```

## 🏃 Running the API

### Start the Server

```bash
# From the backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Documentation

### Health Check

```bash
GET /api/v1/health
```

Response:

```json
{
  "status": "healthy",
  "web3_connected": true,
  "contract_initialized": true,
  "network": "Ganache Local",
  "contract_address": "0x..."
}
```

### User Registration

```bash
POST /api/v1/users/register
```

Request Body:

```json
{
  "address": "0x1234...",
  "name": "Alice",
  "private_key": "0xYourPrivateKey"
}
```

### Send Message

```bash
POST /api/v1/messages/send
```

Request Body:

```json
{
  "from_address": "0x1234...",
  "to_address": "0x5678...",
  "content": "Hello, World!",
  "is_media": false,
  "private_key": "0xYourPrivateKey"
}
```

### Get Chat Messages

```bash
POST /api/v1/messages/chat
```

Request Body:

```json
{
  "user1_address": "0x1234...",
  "user2_address": "0x5678..."
}
```

### Create Group

```bash
POST /api/v1/groups/create
```

Request Body:

```json
{
  "group_name": "Dev Team",
  "members": ["0x1234...", "0x5678...", "0x9abc..."],
  "description": "Development team chat",
  "admin_address": "0x1234...",
  "admin_private_key": "0xYourPrivateKey"
}
```

## 🔑 Private Keys

**IMPORTANT**: The API requires private keys to sign transactions. In production:

1. **Never expose private keys in requests**
2. Use wallet integration (MetaMask, WalletConnect)
3. Implement proper authentication (JWT, OAuth)
4. Use environment variables for sensitive data

For testing with Ganache, you can get private keys from:

- Ganache GUI: Click the key icon next to each account
- Ganache CLI: Displayed when starting the node

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── Registrations.py     # User & messaging endpoints
├── chatservices.py      # Groups & profile endpoints
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Update Contract Address

After deploying your contract, update these files:

**Registrations.py**:

```python
CONTRACT_ADDRESS = "0xYourContractAddress"
```

**chatservices.py**:

```python
CONTRACT_ADDRESS = "0xYourContractAddress"
```

### Ganache Connection

Default connection: `http://127.0.0.1:7545`

To change, update in both `Registrations.py` and `chatservices.py`:

```python
w3 = Web3(Web3.HTTPProvider("http://your-ganache-url"))
```

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Register a user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x1234...",
    "name": "Alice",
    "private_key": "0xYourPrivateKey"
  }'
```

### Using Interactive Docs

Visit http://localhost:8000/docs to use the built-in Swagger UI for testing.

## 📊 Available Endpoints

### User Management

- `POST /api/v1/users/register` - Register new user
- `GET /api/v1/users/{address}` - Get user details
- `GET /api/v1/users/{address}/exists` - Check if user exists
- `PUT /api/v1/users/status` - Update user status
- `PUT /api/v1/users/profile-picture` - Update profile picture
- `POST /api/v1/users/block` - Block a user

### Messaging

- `POST /api/v1/messages/send` - Send a message
- `POST /api/v1/messages/chat` - Get chat messages
- `POST /api/v1/messages/read` - Mark message as read
- `DELETE /api/v1/messages/delete` - Delete a message

### Groups

- `POST /api/v1/groups/create` - Create a group
- `GET /api/v1/groups/user/{address}` - Get user's groups
- `POST /api/v1/groups/messages/send` - Send group message
- `GET /api/v1/groups/{group_id}/messages` - Get group messages
- `POST /api/v1/groups/leave` - Leave a group

## 🐛 Troubleshooting

### Contract Not Initialized

**Error**: "Contract not initialized"

**Solution**: Make sure you've set `CONTRACT_ADDRESS` in both `Registrations.py` and `chatservices.py`

### Web3 Connection Failed

**Error**: "Web3 connection failed"

**Solution**:

1. Ensure Ganache is running on port 7545
2. Check firewall settings
3. Verify the RPC URL in your configuration

### Transaction Failed

**Error**: "Transaction failed"

**Solution**:

1. Verify the private key is correct
2. Ensure account has enough ETH for gas
3. Check if users are registered before sending messages
4. Verify contract address is correct

### Import Errors

**Error**: "No module named 'fastapi'"

**Solution**: Install dependencies:

```bash
pip install fastapi uvicorn web3 pydantic
```

## 🔐 Security Notes

⚠️ **This is a development setup. For production:**

1. Use HTTPS
2. Implement proper authentication
3. Never store private keys in code or requests
4. Use environment variables for sensitive data
5. Implement rate limiting
6. Add input validation and sanitization
7. Use a proper key management system
8. Update CORS settings to specific origins

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:

- Check the [Swagger docs](http://localhost:8000/docs)
- Review the smart contract functions in `FUNCTIONS_REFERENCE.md`
- Check Brownie test results

## 🎯 Next Steps

1. ✅ Deploy smart contract
2. ✅ Update CONTRACT_ADDRESS
3. ✅ Start FastAPI server
4. ⬜ Build frontend (React, Vue, etc.)
5. ⬜ Integrate Web3 wallet
6. ⬜ Add real-time messaging (WebSockets)
7. ⬜ Deploy to production network

---

**Happy Coding! 🚀**

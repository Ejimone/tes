from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
try:
    from config import BLOCKCHAIN_RPC_URL, CONTRACT_ADDRESS as CONFIG_CONTRACT_ADDRESS
except ImportError:
    # Fallback for local development
    BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:7545")
    CONFIG_CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0xa2691703072E2821b9EE1698F05309289FA226c1")

app = APIRouter()

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load contract ABI from build artifacts
contract_path = os.path.join(os.path.dirname(__file__), 'build', 'contracts', 'Whatsapp.json')
if not os.path.exists(contract_path):
    # Try parent directory for local development
    contract_path = os.path.join(os.path.dirname(__file__), '..', 'build', 'contracts', 'Whatsapp.json')

with open(contract_path, 'r') as f:
    contract_data = json.load(f)
    contract_abi = contract_data['abi']

# Contract address from config
CONTRACT_ADDRESS = CONFIG_CONTRACT_ADDRESS

# Initialize contract instance (will be set when address is provided)
contract = None
if CONTRACT_ADDRESS and CONTRACT_ADDRESS != "":
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


# ==================== Pydantic Models ====================

class UserRegistration(BaseModel):
    address: str
    name: str
    private_key: Optional[str] = None  # For signing transactions

class UserResponse(BaseModel):
    name: str
    status: str
    profile_picture: str
    user_address: str
    status_expiry: int

class MessageModel(BaseModel):
    from_address: str
    to_address: str
    content: str
    is_media: Optional[bool] = False
    private_key: str  # For signing transactions

class DeleteMessageModel(BaseModel):
    user1_address: str
    user2_address: str
    message_index: int
    deleter_private_key: str  # For signing transactions

class ReadMessageModel(BaseModel):
    user1_address: str
    user2_address: str
    message_index: int
    reader_private_key: str  # For signing transactions

class ChatMessagesRequest(BaseModel):
    user1_address: str
    user2_address: str


# ==================== Helper Functions ====================

def calculate_chat_id(user1_address: str, user2_address: str) -> bytes:
    """Calculate chat ID from two user addresses"""
    addr1 = user1_address.lower().replace('0x', '')
    addr2 = user2_address.lower().replace('0x', '')
    packed_data = addr1 + addr2
    return w3.keccak(hexstr=packed_data)

def check_contract_initialized():
    """Check if contract is initialized"""
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Contract not initialized. Please set CONTRACT_ADDRESS in backend/Registrations.py"
        )

def get_account_from_private_key(private_key: str):
    """Get account from private key"""
    try:
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        account = w3.eth.account.from_key(private_key)
        return account
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid private key: {str(e)}"
        )

def send_transaction(function, private_key: str, gas_limit: int = 500000):
    """Send a transaction to the blockchain"""
    account = get_account_from_private_key(private_key)
    
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = function.build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': w3.eth.gas_price,
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt['blockNumber'],
            'gas_used': tx_receipt['gasUsed'],
            'status': 'success' if tx_receipt['status'] == 1 else 'failed'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed: {str(e)}"
        )


# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Check if the API and Web3 connection are working"""
    return {
        "status": "healthy",
        "web3_connected": w3.is_connected(),
        "contract_initialized": contract is not None,
        "network": "Ganache Local",
        "contract_address": CONTRACT_ADDRESS if CONTRACT_ADDRESS else "Not set"
    }


@app.post("/users/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistration):
    """Register a new user on the blockchain"""
    check_contract_initialized()
    
    # Use default account if no private key provided
    if not user_data.private_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Private key is required for signing the transaction"
        )
    
    try:
        # Check if user already exists
        user_exists = contract.functions.checkUserExists(user_data.address).call()
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {user_data.address} is already registered"
            )
        
        # Register user
        function = contract.functions.userRegistration(user_data.address, user_data.name)
        tx_result = send_transaction(function, user_data.private_key)
        
        return {
            "message": "User registered successfully",
            "user_address": user_data.address,
            "name": user_data.name,
            **tx_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.get("/users/{address}", response_model=UserResponse)
async def get_user(address: str):
    """Get user details by address"""
    check_contract_initialized()
    
    try:
        # Check if user exists
        user_exists = contract.functions.checkUserExists(address).call()
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {address} not found"
            )
        
        # Get user details
        user_data = contract.functions.getUser(address).call()
        
        return UserResponse(
            name=user_data[0],
            status=user_data[1],
            profile_picture=user_data[2],
            user_address=user_data[3],
            status_expiry=user_data[4]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )


@app.get("/users/{address}/exists")
async def check_user_exists(address: str):
    """Check if a user exists"""
    check_contract_initialized()
    
    try:
        exists = contract.functions.checkUserExists(address).call()
        return {
            "address": address,
            "exists": exists
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check user existence: {str(e)}"
        )


@app.post("/messages/send", status_code=status.HTTP_201_CREATED)
async def send_message_endpoint(message: MessageModel):
    """Send a message from one user to another"""
    check_contract_initialized()
    
    try:
        # Check if both users exist
        sender_exists = contract.functions.checkUserExists(message.from_address).call()
        receiver_exists = contract.functions.checkUserExists(message.to_address).call()
        
        if not sender_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sender {message.from_address} is not registered"
            )
        
        if not receiver_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Receiver {message.to_address} is not registered"
            )
        
        # Send message
        function = contract.functions.sendMessage(
            message.from_address,
            message.to_address,
            message.content,
            message.is_media
        )
        tx_result = send_transaction(function, message.private_key)
        
        # Calculate chat ID for reference
        chat_id = calculate_chat_id(message.from_address, message.to_address)
        
        return {
            "message": "Message sent successfully",
            "chat_id": chat_id.hex(),
            "from": message.from_address,
            "to": message.to_address,
            "is_media": message.is_media,
            **tx_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@app.post("/messages/chat")
async def get_chat_messages(request: ChatMessagesRequest):
    """Get all messages between two users"""
    check_contract_initialized()
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(request.user1_address, request.user2_address)
        
        # Get messages
        messages = contract.functions.getChatMessages(chat_id).call()
        
        # Format messages
        formatted_messages = []
        for idx, msg in enumerate(messages):
            formatted_messages.append({
                "index": idx,
                "sender": msg[0],
                "content": msg[1],
                "timestamp": msg[2],
                "is_read": msg[3],
                "is_deleted": msg[4],
                "is_media": msg[5]
            })
        
        return {
            "chat_id": chat_id.hex(),
            "user1": request.user1_address,
            "user2": request.user2_address,
            "message_count": len(formatted_messages),
            "messages": formatted_messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat messages: {str(e)}"
        )


@app.post("/messages/read")
async def read_message_endpoint(request: ReadMessageModel):
    """Mark a message as read"""
    check_contract_initialized()
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(request.user1_address, request.user2_address)
        
        # Mark message as read
        function = contract.functions.readMessage(chat_id, request.message_index)
        tx_result = send_transaction(function, request.reader_private_key)
        
        return {
            "message": "Message marked as read",
            "chat_id": chat_id.hex(),
            "message_index": request.message_index,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark message as read: {str(e)}"
        )


@app.delete("/messages/delete")
async def delete_message_endpoint(request: DeleteMessageModel):
    """Delete a message from chat"""
    check_contract_initialized()
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(request.user1_address, request.user2_address)
        
        # Get deleter address from private key
        deleter_account = get_account_from_private_key(request.deleter_private_key)
        
        # Delete message
        function = contract.functions.deleteMessage(
            chat_id,
            request.message_index,
            deleter_account.address
        )
        tx_result = send_transaction(function, request.deleter_private_key)
        
        return {
            "message": "Message deleted successfully",
            "chat_id": chat_id.hex(),
            "message_index": request.message_index,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        ) 
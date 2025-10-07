from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os

app = APIRouter()

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load contract ABI from build artifacts
contract_path = os.path.join(os.path.dirname(__file__), '..', 'build', 'contracts', 'Whatsapp.json')
with open(contract_path, 'r') as f:
    contract_data = json.load(f)
    contract_abi = contract_data['abi']

# Contract address - Should match Registrations.py
CONTRACT_ADDRESS = "0xa2691703072E2821b9EE1698F05309289FA226c1"  # UPDATE THIS AFTER DEPLOYMENT

# Initialize contract instance
contract = None
if CONTRACT_ADDRESS:
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


# ==================== Pydantic Models ====================

class GroupCreate(BaseModel):
    group_name: str
    members: List[str]  # List of member addresses
    description: str
    admin_address: str
    admin_private_key: str  # For signing transaction

class GroupMessage(BaseModel):
    group_id: str  # Hex string of group ID
    sender_address: str
    content: str
    is_media: Optional[bool] = False
    sender_private_key: str

class GroupMemberAction(BaseModel):
    group_id: str
    member_address: str
    private_key: str

class UserStatusUpdate(BaseModel):
    user_address: str
    status: str
    duration_seconds: int
    private_key: str

class ProfilePictureUpdate(BaseModel):
    user_address: str
    profile_picture_url: str
    private_key: str

class BlockUserRequest(BaseModel):
    user_to_block: str
    blocker_private_key: str


# ==================== Helper Functions ====================

def check_contract_initialized():
    """Check if contract is initialized"""
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Contract not initialized. Please set CONTRACT_ADDRESS"
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

def convert_to_bytes32(group_id: str) -> bytes:
    """Convert group_id to bytes32 format"""
    try:
        # If it's already a hex string with 0x prefix
        if group_id.startswith('0x'):
            # Remove 0x and convert to bytes
            group_id_bytes = bytes.fromhex(group_id[2:])
            # Ensure it's 32 bytes
            if len(group_id_bytes) != 32:
                raise ValueError(f"Group ID must be 32 bytes, got {len(group_id_bytes)} bytes")
            return group_id_bytes
        # If it's a hex string without 0x
        elif len(group_id) == 64:  # 32 bytes = 64 hex chars
            return bytes.fromhex(group_id)
        else:
            raise ValueError(
                "Invalid group_id format. Expected 32-byte hex string (with or without 0x prefix). "
                "You must create a group first to get a valid group_id."
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid group_id: {str(e)}"
        )

def send_transaction(function, private_key: str, gas_limit: int = 500000):
    """Send a transaction to the blockchain"""
    account = get_account_from_private_key(private_key)
    
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = function.build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': w3.eth.gas_price,
        })
        
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
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


# ==================== Group API Endpoints ====================

@app.post("/groups/create", status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupCreate):
    """Create a new group"""
    check_contract_initialized()
    
    try:
        # Verify all members exist
        for member in group.members:
            exists = contract.functions.checkUserExists(member).call()
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Member {member} is not registered"
                )
        
        # Create group
        function = contract.functions.createGroup(
            group.group_name,
            group.members,
            group.description,
            group.admin_address
        )
        tx_result = send_transaction(function, group.admin_private_key, gas_limit=1000000)
        
        return {
            "message": "Group created successfully",
            "group_name": group.group_name,
            "admin": group.admin_address,
            "member_count": len(group.members),
            **tx_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create group: {str(e)}"
        )


@app.get("/groups/user/{user_address}")
async def get_user_groups(user_address: str):
    """Get all groups a user belongs to"""
    check_contract_initialized()
    
    try:
        groups = contract.functions.getUserGroups(user_address).call()
        
        formatted_groups = []
        for group in groups:
            formatted_groups.append({
                "group_name": group[0],
                "members": group[1],
                "group_id": group[2].hex(),
                "description": group[3],
                "admin": group[4]
            })
        
        return {
            "user_address": user_address,
            "group_count": len(formatted_groups),
            "groups": formatted_groups
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user groups: {str(e)}"
        )


@app.post("/groups/messages/send", status_code=status.HTTP_201_CREATED)
async def send_group_message(message: GroupMessage):
    """Send a message to a group"""
    check_contract_initialized()
    
    try:
        # Convert group ID to bytes32 format
        group_id_bytes = convert_to_bytes32(message.group_id)
        
        # Send group message
        function = contract.functions.sendGroupMessage(
            group_id_bytes,
            message.sender_address,
            message.content,
            message.is_media
        )
        tx_result = send_transaction(function, message.sender_private_key)
        
        return {
            "message": "Group message sent successfully",
            "group_id": message.group_id,
            "sender": message.sender_address,
            **tx_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send group message: {str(e)}"
        )


@app.get("/groups/{group_id}/messages")
async def get_group_messages(group_id: str):
    """Get all messages in a group"""
    check_contract_initialized()
    
    try:
        # Convert group ID to bytes32 format
        group_id_bytes = convert_to_bytes32(group_id)
        
        # Get messages
        messages = contract.functions.getGroupMessages(group_id_bytes).call()
        
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
            "group_id": group_id,
            "message_count": len(formatted_messages),
            "messages": formatted_messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group messages: {str(e)}"
        )


@app.post("/groups/leave")
async def leave_group(action: GroupMemberAction):
    """Leave a group"""
    check_contract_initialized()
    
    try:
        group_id_bytes = convert_to_bytes32(action.group_id)
        
        function = contract.functions.leaveGroup(
            group_id_bytes,
            action.member_address
        )
        tx_result = send_transaction(function, action.private_key)
        
        return {
            "message": "Left group successfully",
            "group_id": action.group_id,
            "member": action.member_address,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave group: {str(e)}"
        )


# ==================== User Profile API Endpoints ====================

@app.put("/users/status")
async def update_user_status(status_update: UserStatusUpdate):
    """Update user status"""
    check_contract_initialized()
    
    try:
        function = contract.functions.userStatus(
            status_update.user_address,
            status_update.status,
            status_update.duration_seconds
        )
        tx_result = send_transaction(function, status_update.private_key)
        
        return {
            "message": "Status updated successfully",
            "user_address": status_update.user_address,
            "status": status_update.status,
            "duration": status_update.duration_seconds,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


@app.put("/users/profile-picture")
async def update_profile_picture(picture_update: ProfilePictureUpdate):
    """Update user profile picture"""
    check_contract_initialized()
    
    try:
        function = contract.functions.updateProfilePicture(
            picture_update.user_address,
            picture_update.profile_picture_url
        )
        tx_result = send_transaction(function, picture_update.private_key)
        
        return {
            "message": "Profile picture updated successfully",
            "user_address": picture_update.user_address,
            "profile_picture": picture_update.profile_picture_url,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile picture: {str(e)}"
        )


@app.post("/users/block")
async def block_user(request: BlockUserRequest):
    """Block a user"""
    check_contract_initialized()
    
    try:
        function = contract.functions.blockUser(request.user_to_block)
        tx_result = send_transaction(function, request.blocker_private_key)
        
        return {
            "message": f"User {request.user_to_block} blocked successfully",
            "blocked_user": request.user_to_block,
            **tx_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to block user: {str(e)}"
        )



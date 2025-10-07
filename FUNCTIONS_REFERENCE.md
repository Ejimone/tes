# WhatsApp DApp Functions Reference

This document provides a comprehensive reference for all corrected functions in the WhatsApp DApp, ready for FastAPI integration.

## Table of Contents

1. [Deploy Functions](#deploy-functions)
2. [Message Functions](#message-functions)
3. [User Management Functions](#user-management-functions)
4. [Group Functions](#group-functions)

---

## Deploy Functions

### `deploy()`

**Purpose**: Deploy the WhatsApp smart contract

**Parameters**: None

**Returns**: Contract instance

**Usage**:

```python
from scripts.deploy import deploy

contract = deploy()
```

---

### `registration(contract, address, name)`

**Purpose**: Register a single user on the contract

**Parameters**:

- `contract`: The deployed contract instance
- `address`: User's wallet address (string)
- `name`: User's display name (string)

**Returns**: Transaction object

**Usage**:

```python
from scripts.deploy import registration

tx = registration(contract, "0x123...", "Alice")
```

---

### `multiple_registrations(contract)`

**Purpose**: Register multiple users automatically (accounts[1] through accounts[9])

**Parameters**:

- `contract`: The deployed contract instance

**Returns**: None

**Usage**:

```python
from scripts.deploy import multiple_registrations

multiple_registrations(contract)
```

---

## User Management Functions

### `check_duplicate(contract, address)`

**Purpose**: Check if a user is already registered

**Parameters**:

- `contract`: The deployed contract instance
- `address`: User's wallet address (string)

**Returns**: Boolean (True if user exists, False otherwise)

**Usage**:

```python
from scripts.deploy import check_duplicate

exists = check_duplicate(contract, "0x123...")
```

---

### `get_user_details(contract, address)`

**Purpose**: Get details for a specific user

**Parameters**:

- `contract`: The deployed contract instance
- `address`: User's wallet address (string)

**Returns**: Tuple of user details (name, status, statusTime, userAddress) or None

**Usage**:

```python
from scripts.deploy import get_user_details

user_details = get_user_details(contract, "0x123...")
if user_details:
    name = user_details[0]
    address = user_details[3]
```

---

### `check_if_user_exists(contract, address)`

**Purpose**: Check if a user exists in the contract

**Parameters**:

- `contract`: The deployed contract instance
- `address`: User's wallet address (string)

**Returns**: Boolean (True if user exists, False otherwise)

**Usage**:

```python
from scripts.deploy import check_if_user_exists

exists = check_if_user_exists(contract, "0x123...")
```

---

### `block_user(contract, blocker_address, user_to_block, blocker_account=None)`

**Purpose**: Block a user

**Parameters**:

- `contract`: The deployed contract instance
- `blocker_address`: Address of the user initiating the block (string)
- `user_to_block`: Address of the user to be blocked (string)
- `blocker_account`: Account object for transaction (optional, defaults to accounts[0])

**Returns**: Transaction object or None

**Usage**:

```python
from scripts.deploy import block_user
from brownie import accounts

tx = block_user(contract, accounts[1], "0x456...", accounts[1])
```

---

### `verify_other_users_unaffected(contract, blocked_address)`

**Purpose**: Verify that blocking a user doesn't affect other users

**Parameters**:

- `contract`: The deployed contract instance
- `blocked_address`: Address of the blocked user (string)

**Returns**: None (prints verification results)

**Usage**:

```python
from scripts.deploy import verify_other_users_unaffected

verify_other_users_unaffected(contract, "0x456...")
```

---

## Message Functions

### `calculate_chat_id(user1_address, user2_address)`

**Purpose**: Calculate the chat ID for two users (helper function)

**Parameters**:

- `user1_address`: First user's address (string or Account object)
- `user2_address`: Second user's address (string or Account object)

**Returns**: bytes32 chat ID

**Usage**:

```python
from scripts.Message import calculate_chat_id

chat_id = calculate_chat_id("0x123...", "0x456...")
```

---

### `send_message(contract, from_address, to_address, message, is_media=False)`

**Purpose**: Send a text message from one user to another

**Parameters**:

- `contract`: The deployed contract instance
- `from_address`: Sender's address (string or Account object)
- `to_address`: Receiver's address (string or Account object)
- `message`: Message content (string)
- `is_media`: Whether this is a media message (boolean, default: False)

**Returns**: Boolean (True if successful, False otherwise)

**Usage**:

```python
from scripts.Message import send_message
from brownie import accounts

success = send_message(contract, accounts[1], accounts[2], "Hello!")
```

---

### `send_media_message(contract, from_address, to_address, media_url, sender_account=None)`

**Purpose**: Send a media message (image, video, etc.)

**Parameters**:

- `contract`: The deployed contract instance
- `from_address`: Sender's address (string or Account object)
- `to_address`: Receiver's address (string or Account object)
- `media_url`: URL or path to the media (string)
- `sender_account`: Account object for transaction (optional, defaults to accounts[0])

**Returns**: Boolean (True if successful, False otherwise)

**Usage**:

```python
from scripts.Message import send_media_message
from brownie import accounts

success = send_media_message(
    contract,
    accounts[1],
    accounts[2],
    "https://example.com/image.png",
    accounts[1]
)
```

---

### `get_chat_messages(contract, user1_address, user2_address)`

**Purpose**: Retrieve all messages between two users

**Parameters**:

- `contract`: The deployed contract instance
- `user1_address`: First user's address (string or Account object)
- `user2_address`: Second user's address (string or Account object)

**Returns**: List of message tuples. Each tuple contains:

- [0] sender (address)
- [1] content (string)
- [2] timestamp (uint)
- [3] is_read (bool)
- [4] is_deleted (bool)
- [5] is_media (bool)

**Usage**:

```python
from scripts.Message import get_chat_messages
from brownie import accounts

messages = get_chat_messages(contract, accounts[1], accounts[2])
for msg in messages:
    print(f"From: {msg[0]}, Message: {msg[1]}, Read: {msg[3]}")
```

---

### `read_message(contract, user1_address, user2_address, message_index, reader_account)`

**Purpose**: Mark a message as read

**Parameters**:

- `contract`: The deployed contract instance
- `user1_address`: First user's address (string or Account object)
- `user2_address`: Second user's address (string or Account object)
- `message_index`: Index of the message to mark as read (int)
- `reader_account`: Account object of the reader for transaction

**Returns**: Boolean (True if successful, False otherwise)

**Usage**:

```python
from scripts.Message import read_message
from brownie import accounts

success = read_message(contract, accounts[1], accounts[2], 0, accounts[2])
```

---

### `delete_message(contract, user1_address, user2_address, message_index, deleter_account)`

**Purpose**: Delete a message from chat history

**Parameters**:

- `contract`: The deployed contract instance
- `user1_address`: First user's address (string or Account object)
- `user2_address`: Second user's address (string or Account object)
- `message_index`: Index of the message to delete (int)
- `deleter_account`: Account object of the deleter for transaction

**Returns**: Boolean (True if successful, False otherwise)

**Usage**:

```python
from scripts.Message import delete_message
from brownie import accounts

success = delete_message(contract, accounts[1], accounts[2], 0, accounts[1])
```

---

## Group Functions

### `create_group(contract, group_name, description, members, admin_address)`

**Purpose**: Create a new group

**Parameters**:

- `contract`: The deployed contract instance
- `group_name`: Name of the group (string)
- `description`: Group description (string)
- `members`: List of member addresses (list of strings)
- `admin_address`: Address of the group admin (string)

**Returns**: Transaction object or None

**Usage**:

```python
from scripts.deploy import create_group
from brownie import accounts

members = [accounts[1].address, accounts[2].address, accounts[3].address]
tx = create_group(
    contract,
    "Dev Team",
    "Development team chat",
    members,
    accounts[1].address
)
```

---

### `delete_group(contract, group_id, admin_address, admin_account=None)`

**Purpose**: Delete a group

**Parameters**:

- `contract`: The deployed contract instance
- `group_id`: ID of the group to delete (bytes32)
- `admin_address`: Address of the group admin (string)
- `admin_account`: Account object for transaction (optional, defaults to accounts[0])

**Returns**: Transaction object or None

**Usage**:

```python
from scripts.deploy import delete_group
from brownie import accounts

tx = delete_group(contract, group_id, accounts[1].address, accounts[1])
```

---

### `delete_group_message(contract, group_id, message_index, deleter_account)`

**Purpose**: Delete a message from a group

**Parameters**:

- `contract`: The deployed contract instance
- `group_id`: ID of the group (bytes32)
- `message_index`: Index of the message to delete (int)
- `deleter_account`: Account object of the deleter for transaction

**Returns**: Boolean (True if successful, False otherwise)

**Usage**:

```python
from scripts.deploy import delete_group_message
from brownie import accounts

success = delete_group_message(contract, group_id, 0, accounts[1])
```

---

## FastAPI Integration Tips

### 1. Account Management

For FastAPI, you'll need to manage accounts differently. Consider:

- Using private keys from environment variables
- Implementing wallet connection (Web3.js/ethers.js on frontend)
- Managing gas fees and transaction signing

### 2. Async Operations

Convert these synchronous functions to async for FastAPI:

```python
from fastapi import FastAPI
from brownie import accounts, network

async def send_message_api(from_addr: str, to_addr: str, message: str):
    # Your async implementation
    pass
```

### 3. Error Handling

Add proper error handling for API responses:

```python
from fastapi import HTTPException

try:
    success = send_message(contract, from_addr, to_addr, msg)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send message")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### 4. Response Models

Create Pydantic models for structured responses:

```python
from pydantic import BaseModel

class Message(BaseModel):
    sender: str
    content: str
    timestamp: int
    is_read: bool
    is_deleted: bool
    is_media: bool
```

---

## Testing

All functions have been tested in `tests/demo-tests.py`. Run tests with:

```bash
brownie test tests/demo-tests.py -v --network ganache
```

**Test Coverage**:

- ✅ Contract deployment
- ✅ User registration (single & multiple)
- ✅ Message sending (text & media)
- ✅ Message reading
- ✅ Message deletion
- ✅ Complete messaging workflow

All 8 tests pass successfully! 🎉

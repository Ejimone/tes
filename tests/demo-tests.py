from brownie import accounts, network, Contract
import pytest
from scripts.deploy import deploy, registration, multiple_registrations
from scripts.Message import send_message, get_chat_messages, read_message, send_media_message, delete_message


@pytest.fixture(scope="function")
def contract():
    """Deploy a fresh contract for each test"""
    return deploy()


@pytest.fixture(scope="function")
def contract_with_users(contract):
    """Deploy contract and register multiple users"""
    multiple_registrations(contract)
    return contract


def test_deployment():
    """Test basic contract deployment"""
    print("\n🧪 Testing contract deployment...")
    contract = deploy()
    assert contract is not None
    assert contract.address is not None
    print("✅ Contract deployment test passed!")


def test_user_registration(contract):
    """Test user registration functionality"""
    print("\n🧪 Testing user registration...")
    
    address = accounts[1].address
    name = "TestUser"
    
    tx = contract.userRegistration(address, name, {'from': accounts[0]})
    assert tx is not None
    
    # Verify registration
    assert contract.checkUserExists(address) == True
    user_details = contract.getUser(address)
    assert user_details[0] == name
    assert user_details[3] == address
    
    print("✅ User registration test passed!")


def test_multiple_registrations(contract):
    """Test multiple user registrations to verify contract functionality"""
    print("\n🧪 Testing multiple user registrations...")
    
    test_users = [
        (accounts[1].address, "Bob"),
        (accounts[2].address, "Charlie"),
        (accounts[3].address, "Diana")
    ]
    
    for address, name in test_users:
        try:
            print(f"\n📝 Registering {name} at {address}...")
            tx = contract.userRegistration(address, name, {'from': accounts[0]})
            print(f"✅ {name} registered! Transaction: {tx.txid}")
            
            # Verify registration
            if contract.checkUserExists(address):
                user_details = contract.getUser(address)
                print(f"   ✓ Verified: {user_details[0]} at {user_details[3]}")
                assert user_details[0] == name
                assert user_details[3] == address
            else:
                print(f"   ❌ Verification failed for {name}")
                assert False, f"User {name} registration failed"
                
        except Exception as e:
            print(f"   ❌ Failed to register {name}: {str(e)}")
            raise
    
    registered_count = len([addr for addr, _ in test_users if contract.checkUserExists(addr)])
    print(f"\n📊 Total registered users: {registered_count}")
    assert registered_count == len(test_users)
    print("✅ Multiple registrations test passed!")


def test_send_message(contract_with_users):
    """Test sending messages between users"""
    print("\n🧪 Testing message sending...")
    
    user1 = accounts[1]
    user2 = accounts[2]
    message = "Hello, this is a test message!"
    
    success = send_message(contract_with_users, user1, user2, message)
    assert success == True
    
    # Verify message was stored
    messages = get_chat_messages(contract_with_users, user1, user2)
    assert len(messages) > 0
    
    print("✅ Message sending test passed!")


def test_send_media_message(contract_with_users):
    """Test sending media messages"""
    print("\n🧪 Testing media message sending...")
    
    user1 = accounts[1]
    user2 = accounts[2]
    media_url = "https://example.com/image.png"
    
    success = send_media_message(contract_with_users, user1, user2, media_url, accounts[0])
    assert success == True
    
    # Verify media message was stored
    messages = get_chat_messages(contract_with_users, user1, user2)
    assert len(messages) > 0
    
    # Check if last message is media
    last_message = messages[-1]
    assert last_message[5] == True  # is_media flag
    
    print("✅ Media message sending test passed!")


def test_read_message(contract_with_users):
    """Test marking messages as read"""
    print("\n🧪 Testing message read functionality...")
    
    user1 = accounts[1]
    user2 = accounts[2]
    
    # Send a message first
    send_message(contract_with_users, user1, user2, "Test message for read")
    
    # Mark message as read
    success = read_message(contract_with_users, user1, user2, 0, user2)
    assert success == True
    
    # Verify message is marked as read
    messages = get_chat_messages(contract_with_users, user1, user2)
    assert messages[0][3] == True  # is_read flag
    
    print("✅ Message read test passed!")


def test_delete_message(contract_with_users):
    """Test deleting messages"""
    print("\n🧪 Testing message deletion...")
    
    user1 = accounts[1]
    user2 = accounts[2]
    
    # Send a message first
    send_message(contract_with_users, user1, user2, "Message to be deleted")
    
    # Delete the message
    success = delete_message(contract_with_users, user1, user2, 0, user1)
    assert success == True
    
    # Verify message is marked as deleted
    messages = get_chat_messages(contract_with_users, user1, user2)
    assert messages[0][4] == True  # is_deleted flag
    
    print("✅ Message deletion test passed!")


def test_messaging_demo(contract_with_users):
    """Demonstrate messaging functionality with registered users"""
    print("\n💬 Testing messaging functionality...")
    
    # Get some registered users - accounts[1] and accounts[2] are registered by multiple_registrations
    user1 = accounts[1]  # User1 - registered in multiple_registrations
    user2 = accounts[2]  # User2 - registered in multiple_registrations
    
    # Send some messages between users
    messages_to_send = [
        (user1, user2, "Hello! This is my first message on WhatsApp DApp! 👋"),
        (user2, user1, "Hi there! Great to see you here! 🎉"),
        (user1, user2, "How do you like this decentralized messaging? 🚀"),
        (user2, user1, "It's amazing! Blockchain messaging is the future! 🌟")
    ]
    
    print(f"\n📤 Sending {len(messages_to_send)} messages...")
    
    for sender, receiver, msg in messages_to_send:
        success = send_message(contract_with_users, sender, receiver, msg)
        if not success:
            print(f"⚠️ Failed to send message from {sender} to {receiver}")
            assert False, "Message sending failed"
    
    # Retrieve and display chat messages
    print(f"\n📥 Retrieving chat history...")
    chat_messages = get_chat_messages(contract_with_users, user1, user2)
    assert len(chat_messages) >= 2  # Should have at least 2 messages in this chat
    
    # Mark some messages as read
    if len(chat_messages) > 0:
        print(f"\n👁️ Marking messages as read...")
        for i in range(min(2, len(chat_messages))):  # Read first 2 messages
            success = read_message(contract_with_users, user1, user2, i, user2)
            assert success == True
        
        # Show updated chat after marking as read
        print(f"\n📋 Updated chat after marking messages as read:")
        updated_messages = get_chat_messages(contract_with_users, user1, user2)
        
        # Verify at least first message is marked as read
        assert updated_messages[0][3] == True  # is_read flag
    
    print("✅ Messaging demo test passed!")


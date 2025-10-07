from brownie import Whatsapp, accounts, network, web3
import sys
import os
import warnings

# Suppress the pkg_resources warning
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

# Add the scripts directory to Python path so we can import from deploy.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import functions from deploy.py
from deploy import deploy, registration, multiple_registrations


def calculate_chat_id(user1_address, user2_address):
    """Calculate chat ID from two user addresses"""
    addr1 = str(user1_address).lower().replace('0x', '') 
    addr2 = str(user2_address).lower().replace('0x', '')
    packed_data = addr1 + addr2
    return web3.keccak(hexstr=packed_data)


def send_message(contract, from_address, to_address, message, is_media=False):
    """Send a message from one user to another"""
    print(f"\n✉️ Sending message from {from_address} to {to_address}...")
    print(f"📝 Message: \"{message}\"")
    
    try:
        # Check if both users are registered
        if not contract.checkUserExists(from_address):
            print(f"❌ Sender {from_address} is not registered!")
            return False
            
        if not contract.checkUserExists(to_address):
            print(f"❌ Receiver {to_address} is not registered!")
            return False
        
        # Send message using correct contract function signature
        tx = contract.sendMessage(from_address, to_address, message, is_media, {'from': accounts[0]})
        print(f"✅ Message sent successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        return False



def delete_message(contract, user1_address, user2_address, message_index, deleter_account):
    """Delete a message from chat history"""
    print(f"\n🗑️ Deleting message {message_index}...")
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(user1_address, user2_address)
        
        # Delete message - pass deleter address as parameter
        deleter_address = str(deleter_account) if hasattr(deleter_account, 'address') else str(deleter_account)
        tx = contract.deleteMessage(chat_id, message_index, deleter_address, {'from': deleter_account})
        print(f"✅ Message deleted successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to delete message: {str(e)}")
        return False


def get_chat_messages(contract, user1_address, user2_address):
    """Get messages between two users"""
    print(f"\n📨 Retrieving messages between {user1_address} and {user2_address}...")
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(user1_address, user2_address)
        
        # Get messages using the contract's getChatMessages function
        messages = contract.getChatMessages(chat_id)
        
        if len(messages) > 0:
            print(f"📬 Found {len(messages)} message(s):")
            for idx, msg in enumerate(messages):
                sender = msg[0]
                content = msg[1]
                timestamp = msg[2]
                is_read = msg[3]
                is_deleted = msg[4]
                is_media = msg[5]
                
                status = ""
                if is_deleted:
                    status += " [DELETED]"
                if is_read:
                    status += " [READ]"
                if is_media:
                    status += " [MEDIA]"
                
                print(f"   📩 Message {idx + 1}: From {sender}")
                print(f"      💬 Content: \"{content}\"{status}")
                print(f"      🕐 Timestamp: {timestamp}")
                print()
        else:
            print("   📭 No messages found in this chat.")
            
        return messages
        
    except Exception as e:
        print(f"❌ Failed to retrieve messages: {str(e)}")
        return []


def read_message(contract, user1_address, user2_address, message_index, reader_account):
    """Mark a message as read"""
    print(f"\n👁️ Marking message {message_index} as read...")
    
    try:
        # Calculate chat ID
        chat_id = calculate_chat_id(user1_address, user2_address)
        
        # Mark message as read
        tx = contract.readMessage(chat_id, message_index, {'from': reader_account})
        print(f"✅ Message marked as read!")
        print(f"📄 Transaction hash: {tx.txid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to mark message as read: {str(e)}")
        return False


def send_media_message(contract, from_address, to_address, media_url, sender_account=None):
    """Send a media message (image, video, etc.)"""
    if sender_account is None:
        sender_account = accounts[0]
    
    print(f"\n🖼️ Sending media message from {from_address} to {to_address}...")
    print(f"📝 Media URL: \"{media_url}\"")
    
    try:
        # Check if both users are registered
        if not contract.checkUserExists(from_address):
            print(f"❌ Sender {from_address} is not registered!")
            return False
            
        if not contract.checkUserExists(to_address):
            print(f"❌ Receiver {to_address} is not registered!")
            return False
        
        # Send media message using correct contract function signature
        tx = contract.sendMessage(from_address, to_address, media_url, True, {'from': sender_account})
        print(f"✅ Media message sent successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send media message: {str(e)}")
        return False


def messaging_demo(contract):
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
        success = send_message(contract, sender, receiver, msg)
        if not success:
            print(f"⚠️ Failed to send message from {sender} to {receiver}")
    
    # Retrieve and display chat messages
    print(f"\n📥 Retrieving chat history...")
    chat_messages = get_chat_messages(contract, user1, user2)
    
    # Mark some messages as read
    if len(chat_messages) > 0:
        print(f"\n👁️ Marking messages as read...")
        for i in range(min(2, len(chat_messages))):  # Read first 2 messages
            read_message(contract, user1, user2, i, user2)
        
        # Show updated chat after marking as read
        print(f"\n📋 Updated chat after marking messages as read:")
        get_chat_messages(contract, user1, user2)


def main():
    print("\n🚀 Starting WhatsApp Messaging System...")
    
    # Deploy the contract
    contract = deploy()
    
    if not contract:
        print("❌ Failed to deploy contract. Exiting...")
        return
    
    # Register multiple users for testing
    print("\n👥 Registering users...")
    multiple_registrations(contract)
    
    # Run messaging demo
    messaging_demo(contract)
    
    print("\n✨ Messaging demo completed successfully!")


if __name__ == "__main__":
    main()
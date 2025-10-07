from brownie import Whatsapp, accounts, network
from brownie import web3
import pytest

@pytest.fixture
def whatsapp_contract():
    # Deploy the contract before each test
    account = accounts[0]
    contract = Whatsapp.deploy({'from': account})
    return contract

def test_register_user(whatsapp_contract):
    contract = whatsapp_contract
    account = accounts[0]
    user_address = account.address
    name = "Willy"
    
    # Register the user
    tx = contract.userRegistration(user_address, name, {'from': account})
    tx.wait(1)

    # Verify user is registered
    assert contract.checkUserExists(user_address) == True
    
    # Verify user details
    user = contract.getUser(user_address)
    assert user[0] == name  # name is the first field in User struct
    assert user[3] == user_address  # userAddress is the fourth field in User struct


def test_duplicate_registration(whatsapp_contract):
    contract = whatsapp_contract
    account = accounts[0]
    user_address = account.address
    name = "Willy"
    
    # Register the user
    tx = contract.userRegistration(user_address, name, {'from': account})
    tx.wait(1)

    # Attempt to register the same user again and expect a revert
    with pytest.raises(Exception):
        contract.userRegistration(user_address, name, {'from': account})


def test_get_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account = accounts[0]
    user_address = account.address
    
    # Attempt to get a user that does not exist and expect a revert
    with pytest.raises(Exception):
        contract.getUser(user_address)

def test_check_user_exists(whatsapp_contract):
    contract = whatsapp_contract
    account = accounts[0]
    user_address = account.address
    name = "Willy"
    
    # Initially, the user should not exist
    assert contract.checkUserExists(user_address) == False
    
    # Register the user
    tx = contract.userRegistration(user_address, name, {'from': account})
    tx.wait(1)
    
    # Now, the user should exist
    assert contract.checkUserExists(user_address) == True

def test_multiple_user_registrations(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    account4 = accounts[3]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    user4_address = account4.address
    
    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    name4 = "Charlie"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    #register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)
    #register fourth user
    tx4 = contract.userRegistration(user4_address, name4, {'from': account4})
    tx4.wait(1)

    # Verify all users are registered
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user2_address) == True
    assert contract.checkUserExists(user3_address) == True
    assert contract.checkUserExists(user4_address) == True

    # Verify user details for all users
    user1 = contract.getUser(user1_address)
    user2 = contract.getUser(user2_address)
    user3 = contract.getUser(user3_address)
    user4 = contract.getUser(user4_address)

    assert user1[0] == name1  # name is the first field in User struct
    assert user1[3] == user1_address  # userAddress is the fourth field in User struct
    
    assert user2[0] == name2  # name is the first field in User struct
    assert user2[3] == user2_address  # userAddress is the fourth field in User struct

    assert user3[0] == name3  # name is the first field in User struct
    assert user3[3] == user3_address  # userAddress is the fourth field in User struct

    assert user4[0] == name4  # name is the first field in User struct
    assert user4[3] == user4_address  # userAddress is the fourth field in User struct






def test_block_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Verify both users exist before blocking
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user2_address) == True

    # Block user2 (this deletes the user from the contract)
    tx3 = contract.blockUser(user2_address, {'from': account1})
    tx3.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Verify user1 still exists (was not affected)
    assert contract.checkUserExists(user1_address) == True

def test_block_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Attempt to block a user that does not exist and expect a revert
    with pytest.raises(Exception):
        contract.blockUser(user2_address, {'from': account1})


def test_block_user_twice(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block user2 (this deletes the user from the contract)
    tx3 = contract.blockUser(user2_address, {'from': account1})
    tx3.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Attempt to block user2 again and expect a revert
    with pytest.raises(Exception):
        contract.blockUser(user2_address, {'from': account1})


def test_block_user_does_not_affect_others(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    
    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)

    # Verify all users exist before blocking
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user2_address) == True
    assert contract.checkUserExists(user3_address) == True

    # Block user2 (this deletes the user from the contract)
    tx4 = contract.blockUser(user2_address, {'from': account1})
    tx4.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Verify user1 and user3 still exist (were not affected)
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user3_address) == True


def test_block_user_and_reregister(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Verify both users exist before blocking
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user2_address) == True

    # Block user2 (this deletes the user from the contract)
    tx3 = contract.blockUser(user2_address, {'from': account1})
    tx3.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Re-register user2
    new_name2 = "Alice_New"
    tx4 = contract.userRegistration(user2_address, new_name2, {'from': account2})
    tx4.wait(1)

    # Verify user2 is registered again with new details
    assert contract.checkUserExists(user2_address) == True
    user2 = contract.getUser(user2_address)
    assert user2[0] == new_name2  # name is the first field in User struct
    assert user2[3] == user2_address  # userAddress is the fourth field in User struct

    # Verify user1 still exists and is unaffected
    assert contract.checkUserExists(user1_address) == True


def test_block_user_edge_case(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Verify user exists before blocking
    assert contract.checkUserExists(user1_address) == True

    # Block user1 (this deletes the user from the contract)
    tx2 = contract.blockUser(user1_address, {'from': account1})
    tx2.wait(1)

    # Verify user1 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user1_address) == False

    # Attempt to get user1 and expect a revert
    with pytest.raises(Exception):
        contract.getUser(user1_address)

    # Attempt to block user1 again and expect a revert
    with pytest.raises(Exception):
        contract.blockUser(user1_address, {'from': account1})


def test_register_after_blocking(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    user1_address = account1.address
    name1 = "Willy"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Block user1 (this deletes the user from the contract)
    tx2 = contract.blockUser(user1_address, {'from': account1})
    tx2.wait(1)
    # Verify user1 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user1_address) == False
    # Re-register user1
    new_name1 = "Willy_New"
    tx3 = contract.userRegistration(user1_address, new_name1, {'from': account1})
    tx3.wait(1)
    # Verify user1 is registered again with new details
    assert contract.checkUserExists(user1_address) == True
    user1 = contract.getUser(user1_address)
    assert user1[0] == new_name1  # name is the first field in User struct
    assert user1[3] == user1_address  # userAddress is the fourth field in User struct
    # Verify user1 details are updated correctly
    assert user1[0] == new_name1  # name is the first field in User struct
    assert user1[3] == user1_address  # userAddress is the fourth field in User struct
    # Attempt to register user1 again with the same address and expect a revert
    with pytest.raises(Exception):
        contract.userRegistration(user1_address, new_name1, {'from': account1})




def test_send_message(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send a message from user1 to user2
    message_content = "Hello, Alice!"
    is_media = False
    tx3 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx3.wait(1)
    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct





def test_send_message_to_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Attempt to send a message to a user that does not exist and expect a revert
    message_content = "Hello, Alice!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})


def test_send_message_from_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name2 = "Alice"
    
    # Register second user
    tx1 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx1.wait(1)
    
    # Attempt to send a message from a user that does not exist and expect a revert
    message_content = "Hello, Alice!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})   



def test_send_message_edge_case(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send a message from user1 to user2 with empty content
    message_content = ""
    is_media = False
    tx3 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx3.wait(1)

    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct (should be empty)
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct


def test_send_media_message(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send a media message from user1 to user2
    message_content = "Image_URL_or_Data"
    is_media = True
    tx3 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx3.wait(1)
    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the media message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct (should be True)



def test_send_multiple_messages(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send multiple messages from user1 to user2
    messages_to_send = [
        ("Hello, Alice!", False),
        ("How are you?", False),
        ("Check out this image!", True),
        ("Image_URL_or_Data", True),
        ("Goodbye!", False)
    ]
    
    for content, is_media in messages_to_send:
        tx = contract.sendMessage(user1_address, user2_address, content, is_media, {'from': account1})
        tx.wait(1)

    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify all messages were sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == len(messages_to_send)
    
    for i, (content, is_media) in enumerate(messages_to_send):
        assert messages[i][0] == user1_address  # sender is the first field in Message struct
        assert messages[i][1] == content  # content is the second field in Message struct
        assert messages[i][4] == False  # isDeleted is the fifth field in Message struct
        assert messages[i][5] == is_media  # isMedia is the sixth field in Message struct


def test_send_message_after_blocking(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block user2 (this deletes the user from the contract)
    tx3 = contract.blockUser(user2_address, {'from': account1})
    tx3.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Attempt to send a message to the blocked (deleted) user and expect a revert
    message_content = "Hello, Alice!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})

def test_send_message_after_reregistering(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block user2 (this deletes the user from the contract)
    tx3 = contract.blockUser(user2_address, {'from': account1})
    tx3.wait(1)

    # Verify user2 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user2_address) == False

    # Re-register user2
    new_name2 = "Alice_New"
    tx4 = contract.userRegistration(user2_address, new_name2, {'from': account2})
    tx4.wait(1)

    # Verify user2 is registered again with new details
    assert contract.checkUserExists(user2_address) == True
    user2 = contract.getUser(user2_address)
    assert user2[0] == new_name2  # name is the first field in User struct
    assert user2[3] == user2_address  # userAddress is the fourth field in User struct

    # Now send a message from user1 to the re-registered user2
    message_content = "Hello again, Alice!"
    is_media = False
    tx5 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx5.wait(1)


    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct (should be False) 




def test_send_message_to_self(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address

    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Send a message from user1 to themselves
    message_content = "Hello, me!"
    is_media = False
    tx2 = contract.sendMessage(user1_address, user1_address, message_content, is_media, {'from': account1})
    tx2.wait(1)

    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user1_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct (should be False)



def test_send_message_after_blocking_sender(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block user1 (this deletes the user from the contract)
    tx3 = contract.blockUser(user1_address, {'from': account2})
    tx3.wait(1)

    # Verify user1 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user1_address) == False

    # Attempt to send a message from the blocked (deleted) user and expect a revert
    message_content = "Hello, Alice!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})


def test_send_message_after_both_users_blocked(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block user1 (this deletes the user from the contract)
    tx3 = contract.blockUser(user1_address, {'from': account2})
    tx3.wait(1)

    # Block user2 (this deletes the user from the contract)
    tx4 = contract.blockUser(user2_address, {'from': account1})
    tx4.wait(1)

    # Verify both users no longer exist (have been "blocked"/deleted)
    assert contract.checkUserExists(user1_address) == False
    assert contract.checkUserExists(user2_address) == False

    # Attempt to send a message from the blocked (deleted) user1 to blocked (deleted) user2 and expect a revert
    message_content = "Hello, Alice!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})

def test_send_message_after_blocking_and_reregistering_both(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]

    user1_address = account1.address
    user2_address = account2.address

    name1 = "Willy"
    name2 = "Alice"

    # Register first
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)

    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Block both users
    tx3 = contract.blockUser(user1_address, {'from': account2})
    tx3.wait(1)
    tx4 = contract.blockUser(user2_address, {'from': account1})
    tx4.wait(1)

    # Re-register both users
    new_name1 = "Willy_New"
    new_name2 = "Alice_New"
    tx5 = contract.userRegistration(user1_address, new_name1, {'from': account1})
    tx5.wait(1)
    tx6 = contract.userRegistration(user2_address, new_name2, {'from': account2})
    tx6.wait(1)

    # Verify both users exist after re-registration
    assert contract.checkUserExists(user1_address) == True
    assert contract.checkUserExists(user2_address) == True

    # Send a message from re-registered user1 to re-registered user2 (should succeed)
    message_content = "Hello again, Alice!"
    is_media = False
    tx7 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx7.wait(1)

    # Calculate the chat ID and verify the message was sent correctly
    from brownie import web3
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender
    assert messages[0][1] == message_content  # content




def test_read_message(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send a message from user1 to user2
    message_content = "Hello, Alice!"
    is_media = False
    tx3 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx3.wait(1)
    
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Verify the message was sent correctly
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == 1
    assert messages[0][0] == user1_address  # sender is the first field in Message struct
    assert messages[0][1] == message_content  # content is the second field in Message struct
    assert messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert messages[0][5] == is_media  # isMedia is the sixth field in Message struct (should be False) 

    # Mark the message as read by user2
    tx4 = contract.readMessage(chat_id, 0, {'from': account2})  # Assuming message index is 0
    tx4.wait(1)

    # Verify the message is marked as read
    messages_after_read = contract.getChatMessages(chat_id)
    assert messages_after_read[0][3] == True  # isRead is the fourth field in Message struct




def test_create_group(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    
    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)

    # Create a group with user1 as admin and user2, user3 as members
    group_name = "Friends"
    members = [user1_address, user2_address, user3_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address
    
    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx4.wait(1)

    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1  # user1 should be in 1 group
    
    group = user1_groups[0]
    assert group[0] == group_name  # groupName is the first field in Group struct
    assert group[4] == admin  # admin is the fifth field in Group struct
    assert len(group[1]) == 3  # members is the second field in Group struct (should have 3 members)
    assert user1_address in group[1]  # Check if user1 is in members
    assert user2_address in group[1]  # Check if user2 is in members
    assert user3_address in group[1]  # Check if user3 is in members




def test_create_group_with_nonexistent_member(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Attempt to create a group with user3 (non-existent) as a member and expect a revert
    group_name = "Friends"
    members = [user1_address, user2_address, user3_address]  # user3 is not registered
    group_description = "A group for friends"
    admin = user1_address
    
    with pytest.raises(Exception):
        contract.createGroup(group_name, members, group_description, admin, {'from': account1})

def test_create_group_with_non_admin_creator(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    
    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)

    # Create a group with user2 as the creator but user1 as admin (should succeed)
    group_name = "Friends"
    members = [user1_address, user2_address, user3_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address  # admin is user1, but creator will be user2
    
    # This should succeed since the contract allows anyone to create a group and designate an admin
    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account2})
    tx4.wait(1)

    # Verify the group was created correctly with user1 as admin
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) >= 1  # user1 should be in at least 1 group
    
    # Find the group we just created
    group_found = False
    for group in user1_groups:
        if group[0] == group_name:  # groupName matches
            assert group[4] == admin  # admin is user1 (fifth field)
            assert len(group[1]) == 3  # members count (second field)
            group_found = True
            break
    
    assert group_found, "Group not found in user1's groups"




def test_create_group_with_empty_member_list(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)

    # Attempt to create a group with an empty member list and expect a revert
    group_name = "LonelyGroup"
    members = []  # Empty member list
    group_description = "A group with no members"
    admin = user1_address
    
    with pytest.raises(Exception):
        contract.createGroup(group_name, members, group_description, admin, {'from': account1})


    
def test_change_group_admin(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]

    user1_address = account1.address
    user2_address = account2.address

    name1 = "Willy"
    name2 = "Alice"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Create a group with user1 as admin and user2 as member
    group_name = "Friends"
    members = [user1_address, user2_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address

    tx3 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx3.wait(1)
    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1  # user1 should be in 1 group

    group = user1_groups[0]
    assert group[0] == group_name  # groupName is the first field in Group struct
    assert group[4] == admin  # admin is the fifth field in Group struct
    assert len(group[1]) == 2  # members is the second field in Group struct (should have 2 members)
    assert user1_address in group[1]  # Check if user1 is in members
    assert user2_address in group[1]  # Check if user2 is in members
    
    # Get the group ID from the created group
    group_id = group[2]  # groupId is the third field in Group struct
    
    # Change group admin from user1 to user2
    tx4 = contract.changeGroupAdmin(group_id, user2_address, user1_address, {'from': account1})
    tx4.wait(1)
    
    # Verify the admin was changed by checking user1's groups (admin should be updated)
    user1_groups_after = contract.getUserGroups(user1_address)
    assert len(user1_groups_after) == 1  # user1 should still be in 1 group 
    group_after_admin_change = user1_groups_after[0]
    assert group_after_admin_change[0] == group_name  # groupName is the first field in Group struct
    assert group_after_admin_change[4] == user2_address  # admin should now be user2
    assert len(group_after_admin_change[1]) == 2  # members should still be 2
    assert user1_address in group_after_admin_change[1]  # Check if user1 is still in members
    assert user2_address in group_after_admin_change[1]  # Check if user2 is still in members  
    # Verify user1's view of the group also reflects the new admin
    user1_groups_after_admin_change = contract.getUserGroups(user1_address)
    assert len(user1_groups_after_admin_change) == 1  # user1 should still be in 1 group
    group_user1_view = user1_groups_after_admin_change[0]
    assert group_user1_view[0] == group_name  # groupName is the first field in Group struct
    assert group_user1_view[4] == user2_address  # admin should now be user2
    assert len(group_user1_view[1]) == 2  # members should still be 2
    assert user1_address in group_user1_view[1]  # Check if user1 is still in members
    assert user2_address in group_user1_view[1]  # Check if user2 is still in members


def test_change_group_admin_to_non_member(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]

    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address

    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)
    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)

    # Create a group with user1 as admin and user2 as member
    group_name = "Friends"
    members = [user1_address, user2_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address

    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx4.wait(1)
    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1  # user1 should be in 1 group

    group = user1_groups[0]
    assert group[0] == group_name  # groupName is the first field in Group struct
    assert group[4] == admin  # admin is the fifth field in Group struct
    assert len(group[1]) == 2  # members is the second field in Group struct (should have 2 members)
    assert user1_address in group[1]  # Check if user1 is in members
    assert user2_address in group[1]  # Check if user2 is in members
    
    # Get the group ID from the created group
    group_id = group[2]  # groupId is the third field in Group struct
    
    # Change group admin from user1 to user3 (non-member) - contract allows this
    tx5 = contract.changeGroupAdmin(group_id, user3_address, user1_address, {'from': account1})
    tx5.wait(1)

    # Verify the admin was changed to user3 (even though user3 is not a group member)
    # Note: This demonstrates that the contract allows non-members to become admins
    user1_groups_after = contract.getUserGroups(user1_address)
    assert len(user1_groups_after) == 1  # user1 should still be in 1 group 
    group_after_admin_change = user1_groups_after[0]
    assert group_after_admin_change[0] == group_name  # groupName is the first field in Group struct
    assert group_after_admin_change[4] == user3_address  # admin should now be user3



def test_change_group_admin_by_non_admin(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]

    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address

    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Register second user 
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)
    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)
    # Create a group with user1 as admin and user2 as member
    group_name = "Friends"
    members = [user1_address, user2_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address

    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx4.wait(1)
    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1  # user1 should be in 1 group
    group = user1_groups[0]
    assert group[0] == group_name  # groupName is the first field in Group
    assert group[4] == admin  # admin is the fifth field in Group struct
    assert len(group[1]) == 2  # members is the second field in Group
    assert user1_address in group[1]  # Check if user1 is in members
    assert user2_address in group[1]  # Check if user2 is in members
    # Get the group ID from the created group
    group_id = group[2]  # groupId is the third field in Group struct
    # Attempt to change group admin from user1 to user2 by user2 (non-admin) and expect a revert
    with pytest.raises(Exception):
        contract.changeGroupAdmin(group_id, user2_address, user2_address, {'from': account2})

def test_send_group_message(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]
    
    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address

    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)
    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)

    # Create a group with user1 as admin and user2, user3 as members
    group_name = "Friends"
    members = [user1_address, user2_address, user3_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address

    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx4.wait(1)
    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1  # user1 should be in 1 group

    group = user1_groups[0]
    assert group[0] == group_name  # groupName is the first field in Group struct
    assert group[4] == admin  # admin is the fifth field in Group struct
    assert len(group[1]) == 3  # members is the second field in Group struct (should have 3 members)
    assert user1_address in group[1]  # Check if user1 is in members
    assert user2_address in group[1]  # Check if user2 is in members
    assert user3_address in group[1]  # Check if user3 is in members

    # Get the group ID from the created group
    group_id = group[2]  # groupId is the third field in Group struct

    # Send a message to the group from user1
    message_content = "Hello, everyone!"
    is_media = False
    tx5 = contract.sendGroupMessage(group_id, user1_address, message_content, is_media, {'from': account1})
    tx5.wait(1)

    # Verify the message was sent correctly to the group
    group_messages = contract.getGroupMessages(group_id)
    assert len(group_messages) == 1
    assert group_messages[0][0] == user1_address  # sender is the first field in Message struct
    assert group_messages[0][1] == message_content  # content is the second field in Message struct
    assert group_messages[0][4] == False  # isDeleted is the fifth field in Message struct
    assert group_messages[0][5] == is_media  # isMedia is the sixth field in Message struct (should be False)

def test_send_group_message_by_non_member(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    account3 = accounts[2]

    user1_address = account1.address
    user2_address = account2.address
    user3_address = account3.address
    name1 = "Willy"
    name2 = "Alice"
    name3 = "Bob"
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)
    # Register third user
    tx3 = contract.userRegistration(user3_address, name3, {'from': account3})
    tx3.wait(1)
    # Create a group with user1 as admin and user2 as member
    group_name = "Friends"
    members = [user1_address, user2_address]  # Include admin in members list
    group_description = "A group for friends"
    admin = user1_address
    tx4 = contract.createGroup(group_name, members, group_description, admin, {'from': account1})
    tx4.wait(1)
    # Verify the group was created by checking user1's groups
    user1_groups = contract.getUserGroups(user1_address)
    assert len(user1_groups) == 1
    group = user1_groups[0]
    assert group[0] == group_name
    assert group[4] == admin
    assert len(group[1]) == 2  # members is the second field in Group
    assert user1_address in group[1]
    assert user2_address in group[1]
    # Get the group ID from the created group
    group_id = group[2]  # groupId is the third field in Group struct
    # Attempt to send a message to the group from user3 (non-member) and expect a revert
    message_content = "Hello, everyone!"
    is_media = False
    with pytest.raises(Exception):
        contract.sendGroupMessage(group_id, user3_address, message_content, is_media, {'from': account3})




def test_send_multiple_messages(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)
    # Send multiple messages from user1 to user2
    messages_to_send = [
        ("Hello, Alice!", False),
        ("Check out this photo!", True),
        ("How are you?", False)
    ]
    for content, is_media in messages_to_send:
        tx = contract.sendMessage(user1_address, user2_address, content, is_media, {'from': account1})
        tx.wait(1)
        # Verify the messages were sent correctly
    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)
    messages = contract.getChatMessages(chat_id)
    assert len(messages) == len(messages_to_send)
    for i, message in enumerate(messages):
        assert message[0] == user1_address  # sender is the first field in Message struct
        assert message[1] == messages_to_send[i][0]  # content is the second field in Message struct
        assert message[4] == False  # isDeleted is the fifth field in Message struct
        assert message[5] == messages_to_send[i][1]  # isMedia is the sixth field in Message struct (should match sent value)





def test_user_status(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)

    # Set user status
    status_message = "Feeling happy!"
    time_days = 1  # Status expires in 1 day
    tx2 = contract.userStatus(user1_address, status_message, time_days, {'from': account1})
    tx2.wait(1)

    # Verify the status was set correctly
    user_details = contract.getUser(user1_address)
    assert user_details[1] == status_message  # status is the second field in User struct

def test_user_status_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address

    # Attempt to set status for a non-existent user and expect a revert
    status_message = "Feeling happy!"
    time_days = 1
    with pytest.raises(Exception):
        contract.userStatus(user1_address, status_message, time_days, {'from': account1})

    # Attempt to get status for a non-existent user and expect a revert
    with pytest.raises(Exception):
        contract.getUser(user1_address)


def test_user_status_after_blocking(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]
    
    user1_address = account1.address
    user2_address = account2.address
    
    name1 = "Willy"
    name2 = "Alice"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)
    
    # Register second user
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Set user1's status
    status_message = "Feeling happy!"
    time_days = 1  # Status expires in 1 day
    tx3 = contract.userStatus(user1_address, status_message, time_days, {'from': account1})
    tx3.wait(1)

    # Verify the status was set correctly
    user_details = contract.getUser(user1_address)
    assert user_details[1] == status_message  # status is the second field in User struct

    # Block user1 (this deletes the user from the contract)
    tx4 = contract.blockUser(user1_address, {'from': account2})
    tx4.wait(1)

    # Verify user1 no longer exists (has been "blocked"/deleted)
    assert contract.checkUserExists(user1_address) == False

    # Attempt to get status for the blocked (deleted) user and expect a revert
    with pytest.raises(Exception):
        contract.getUser(user1_address)




def test_update_profile_picture(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address
    
    name1 = "Willy"
    
    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)

    # Update profile picture
    new_profile_picture = "http://example.com/profile.jpg"
    tx2 = contract.updateProfilePicture(user1_address, new_profile_picture, {'from': account1})
    tx2.wait(1)

    # Verify the profile picture was updated correctly
    user_details = contract.getUser(user1_address)
    assert user_details[2] == new_profile_picture  # profilePicture is the third field in User struct


def test_update_profile_picture_nonexistent_user(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    
    user1_address = account1.address

    # Attempt to update profile picture for a non-existent user and expect a revert
    new_profile_picture = "http://example.com/profile.jpg"
    with pytest.raises(Exception):
        contract.updateProfilePicture(user1_address, new_profile_picture, {'from': account1})

    # Attempt to get details for a non-existent user and expect a revert
    with pytest.raises(Exception):
        contract.getUserDetails(user1_address)

    

def test_archive_chat(whatsapp_contract):
    contract = whatsapp_contract
    account1 = accounts[0]
    account2 = accounts[1]

    user1_address = account1.address
    user2_address = account2.address

    name1 = "Willy"
    name2 = "Alice"

    # Register first user
    tx1 = contract.userRegistration(user1_address, name1, {'from': account1})
    tx1.wait(1)

    # Register second
    tx2 = contract.userRegistration(user2_address, name2, {'from': account2})
    tx2.wait(1)

    # Send a message from user1 to user2
    message_content = "Hello, Alice!"
    is_media = False
    tx3 = contract.sendMessage(user1_address, user2_address, message_content, is_media, {'from': account1})
    tx3.wait(1)

    # Create the packed encoding like abi.encodePacked in Solidity
    # Remove '0x' prefix and concatenate the hex strings, then hash
    packed_data = user1_address.lower().replace('0x', '') + user2_address.lower().replace('0x', '')
    chat_id = web3.keccak(hexstr=packed_data)

    # Archive the chat (correct parameter order: chatId, userAddress, isArchived)
    tx4 = contract.archiveChat(chat_id, user1_address, True, {'from': account1})
    tx4.wait(1)
    
    # Note: The contract doesn't provide a getter for archived chats,
    # but we can verify the transaction succeeded by checking no revert occurred
    
    # Unarchive the chat
    tx5 = contract.archiveChat(chat_id, user1_address, False, {'from': account1})
    tx5.wait(1)
    
    # Again, verify the transaction succeeded by checking no revert occurred



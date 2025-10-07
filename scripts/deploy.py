from brownie import Whatsapp, accounts, network
import warnings

# Suppress the pkg_resources warning
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

def deploy():
    print("Starting deployment...")
    print(f"Using network: {network.show_active()}")
    
    account = accounts[0]
    print(f"Deploying from account: {account}")
    print(f"Account balance: {account.balance() / 1e18} ETH")
    
    print("Deploying Whatsapp contract...")
    contract = Whatsapp.deploy({'from': account})
    
    print(f"✅ Contract deployed successfully!")
    print(f"📍 Contract address: {contract.address}")
    print(f"⛽ Gas used: {contract.tx.gas_used:,}")
    print(f"📄 Transaction hash: {contract.tx.txid}")
    
    # Basic contract verification
    print("\n🔍 Verifying contract deployment...")
    print(f"Contract exists: {contract.address is not None}")
    
    return contract



def registration(contract, address, name):
    # Get account dynamically - supports multiple methods
    if network.show_active() in ['development', 'ganache']:
        # Use first account for local development automatically
        account = accounts[0]
        print(f"\n📝 Using account 0 for registration: {account.address}")
    elif len(accounts) > 1:
        # If multiple accounts loaded, let user choose
        print("\nAvailable accounts:")
        for i, acc in enumerate(accounts):
            print(f"{i}: {acc.address}")
        account_index = int(input("Enter account index to use: "))
        account = accounts[account_index]
    else:
        # For live networks, load from private key or keystore
        print("\nAccount options:")
        print("1. Load from private key")
        print("2. Load from keystore file")
        choice = input("Choose option (1 or 2): ")
        
        if choice == "1":
            private_key = input("Enter private key: ")
            account = accounts.add(private_key)
        else:
            keystore_path = input("Enter keystore file path: ")
            password = input("Enter password: ")
            account = accounts.load(keystore_path, password=password)
    
    print(f"Using account: {account.address}")
    print(f"Account balance: {account.balance() / 1e18} ETH")
    print("\nRegistering user on the contract...")

    # Use correct function name from contract
    tx = contract.userRegistration(address, name, {'from': account})
    print(f"✅ User registered successfully!")
    print(f"📄 Transaction hash: {tx.txid}")
    
    # Verify registration
    print("\n🔍 Verifying user registration...")
    user_exists = contract.checkUserExists(address)
    print(f"User exists in contract: {user_exists}")
    
    if user_exists:
        user_details = contract.getUser(address)
        print(f"👤 Registered name: {user_details[0]}")
        print(f"📧 User address: {user_details[3]}")

    return tx



def multiple_registrations(contract):
    print("\n📝 Multiple registrations")
    users = [accounts[i].address for i in range(1, len(accounts))]

    for i, user in enumerate(users):
        name = f"User{i+1}"
        print(f"\n📝 Registering {name} at {user}...")
        try:
            tx = contract.userRegistration(user, name, {'from': accounts[0]})
            print(f"✅ {name} registered! Transaction: {tx.txid}")
            
            # Verify registration
            if contract.checkUserExists(user):
                user_details = contract.getUser(user)
                print(f"   ✓ Verified: {user_details[0]} at {user_details[3]}")
            else:
                print(f"   ❌ Verification failed for {name}")
                
        except Exception as e:
            print(f"   ❌ Failed to register {name}: {str(e)}")



def check_duplicate(contract, address):
    print("\n🔍 Checking for duplicate registration...")
    user_exists = contract.checkUserExists(address)
    if user_exists:
        user_details = contract.getUser(address)
        print(f"👤 User already registered: {user_details[0]} at {user_details[3]}")
    else:
        print("👤 No existing registration found.")
    return user_exists



def get_user_details(contract, address):
    if contract.checkUserExists(address):
        user_details = contract.getUser(address)
        print(f"👤 User details: Name: {user_details[0]}, Address: {user_details[3]}")
        return user_details
    else:
        print("👤 No user found with that address.")
        return None

def get_a_user_details(contract):
    """Get details for a specific user by entering their address"""
    user_address = input("Enter user address to lookup: ")
    
    print(f"\n🔍 Looking up user: {user_address}")
    try:
        if contract.checkUserExists(user_address):
            user_details = contract.getUser(user_address)
            print(f"✅ User found!")
            print(f"👤 Name: {user_details[0]}")
            print(f"📧 Address: {user_details[3]}")
            return user_details
        else:
            print("❌ No user found with that address.")
            return None
    except Exception as e:
        print(f"❌ Error retrieving user details: {str(e)}")
        return None


def check_if_user_exists(contract, address):
    """Check if a user exists in the contract"""
    print(f"\n🔍 Checking if user {address} exists...")
    user_exists = contract.checkUserExists(address)
    if user_exists:
        print(f"✅ User exists: {address}")
    else:
        print(f"❌ User does not exist: {address}")
    return user_exists


def block_user(contract, blocker_address, user_to_block, blocker_account=None):
    """Block a user"""
    if blocker_account is None:
        blocker_account = accounts[0]
    
    print(f"\n🔒 {blocker_address} blocking user {user_to_block}...")
    try:
        tx = contract.blockUser(user_to_block, {'from': blocker_account})
        print(f"✅ You blocked {user_to_block} successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return tx
    except Exception as e:
        print(f"❌ Failed to block user: {str(e)}")
        return None



def verify_other_users_unaffected(contract, blocked_address):
    """Verify that blocking a user doesn't affect other users"""
    print("\n🔍 Verifying other users are unaffected...")
    users = [accounts[i].address for i in range(1, len(accounts))]
    
    for user in users:
        if user != blocked_address:
            if contract.checkUserExists(user):
                user_details = contract.getUser(user)
                print(f"   ✓ {user_details[0]} at {user_details[3]} is unaffected.")
            else:
                print(f"   ❌ {user} not found, something went wrong!")



def create_group(contract, group_name, description,  members, admin_address):
    print(f"\n👥 Creating group '{group_name}' with admin {admin_address}...")
    try:
        tx = contract.createGroup(group_name, description, members, admin_address, {'from': accounts[0]})
        print(f"✅ Group created successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return tx
    except Exception as e:
        print(f"❌ Failed to create group: {str(e)}")
        return None




def delete_group(contract, group_id, admin_address, admin_account=None):
    """Delete a group"""
    if admin_account is None:
        admin_account = accounts[0]
    
    print(f"\n🗑️ Deleting group ID {group_id} by admin {admin_address}...")
    try:
        tx = contract.deleteGroup(group_id, admin_address, {'from': admin_account})
        print(f"✅ Group deleted successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return tx
    except Exception as e:
        print(f"❌ Failed to delete group: {str(e)}")
        return None


def group_details(contract, group_id):
    """Get details of a group"""
    print(f"\n🔍 Retrieving details for group ID {group_id}...")
    try:
        group_info = contract.getGroup(group_id)
        if group_info[0] != "":
            print(f"✅ Group found!")
            print(f"👥 Name: {group_info[0]}")
            print(f"📝 Description: {group_info[1]}")
            print(f"👤 Admin: {group_info[3]}")
            print(f"👥 Members: {group_info[4]}")
            return group_info
        else:
            print("❌ No group found with that ID.")
            return None
    except Exception as e:
        print(f"❌ Error retrieving group details: {str(e)}")
        return None



def delete_group_message(contract, group_id, message_index, deleter_account):
    """Delete a message from a group"""
    print(f"\n🗑️ Deleting group message {message_index} from group {group_id}...")
    try:
        # Pass deleter address as parameter
        deleter_address = str(deleter_account) if hasattr(deleter_account, 'address') else str(deleter_account)
        tx = contract.deleteGroupMessage(group_id, message_index, deleter_address, {'from': deleter_account})
        print(f"✅ Group message deleted successfully!")
        print(f"📄 Transaction hash: {tx.txid}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete group message: {str(e)}")
        return False




def main():
    address = accounts[0].address  # Get the address, not the account object
    name = input("Enter user name: ")
    
    try:
        # Deploy the contract
        contract = deploy()
        print("\n🎉 Deployment completed successfully!")
        
        # Register the user on the deployed contract
        registration(contract, address, name)
        
        # # Test multiple registrations if we have enough accounts
        # if len(accounts) >= 4 and network.show_active() in ['development', 'ganache']:
        #     test_multiple_registrations(contract)
        
        print("\n🎊 All operations completed successfully!")


        print("multiple registrations")
        multiple_registrations(contract)
        print("check duplicate")
        check_duplicate(contract, address)

        print("get all  user details")
        get_user_details(contract, address)

        get_a_user_details(contract)
        check_if_user_exists(contract, address)



        return contract
        
    except Exception as e:
        print(f"❌ Operation failed: {str(e)}")
        raise
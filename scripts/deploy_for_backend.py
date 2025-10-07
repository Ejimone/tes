"""
Deployment Helper Script
Deploy contract and automatically update backend configuration
"""
from brownie import Whatsapp, accounts, network
import json
import os
import re

def deploy_and_configure():
    """Deploy contract and update backend configuration"""
    print("=" * 60)
    print("WhatsApp DApp - Deployment & Configuration Script")
    print("=" * 60)
    
    # Deploy contract
    print("\n📦 Deploying WhatsApp contract...")
    print(f"🌐 Network: {network.show_active()}")
    
    account = accounts[0]
    print(f"👤 Deployer: {account.address}")
    print(f"💰 Balance: {account.balance() / 1e18} ETH")
    
    contract = Whatsapp.deploy({'from': account})
    
    print(f"\n✅ Contract deployed successfully!")
    print(f"📍 Contract Address: {contract.address}")
    print(f"⛽ Gas Used: {contract.tx.gas_used:,}")
    print(f"📄 Transaction Hash: {contract.tx.txid}")
    
    # Update backend configuration
    print("\n🔧 Updating backend configuration...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    files_to_update = ['Registrations.py', 'chatservices.py']
    
    for filename in files_to_update:
        filepath = os.path.join(backend_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Update CONTRACT_ADDRESS
            pattern = r'CONTRACT_ADDRESS = "[^"]*"'
            replacement = f'CONTRACT_ADDRESS = "{contract.address}"'
            updated_content = re.sub(pattern, replacement, content)
            
            with open(filepath, 'w') as f:
                f.write(updated_content)
            
            print(f"   ✅ Updated {filename}")
        else:
            print(f"   ⚠️  {filename} not found")
    
    # Save deployment info
    deployment_info = {
        'contract_address': contract.address,
        'deployer': account.address,
        'network': network.show_active(),
        'transaction_hash': contract.tx.txid,
        'gas_used': contract.tx.gas_used,
        'block_number': contract.tx.block_number
    }
    
    deployment_file = os.path.join(backend_dir, 'deployment_info.json')
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n💾 Deployment info saved to: deployment_info.json")
    
    # Register some test users
    print("\n👥 Registering test users...")
    test_users = [
        (accounts[1].address, "Alice"),
        (accounts[2].address, "Bob"),
        (accounts[3].address, "Charlie")
    ]
    
    for address, name in test_users:
        try:
            tx = contract.userRegistration(address, name, {'from': accounts[0]})
            print(f"   ✅ Registered {name} at {address[:10]}...")
        except Exception as e:
            print(f"   ⚠️  Failed to register {name}: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 Deployment Complete!")
    print("=" * 60)
    print(f"\n📋 Quick Start Guide:")
    print(f"1. Contract Address: {contract.address}")
    print(f"2. Backend files updated automatically")
    print(f"3. Start the backend:")
    print(f"   cd backend")
    print(f"   python main.py")
    print(f"4. API will be available at: http://localhost:8000")
    print(f"5. Interactive docs: http://localhost:8000/docs")
    
    print(f"\n🔑 Test Accounts (for API testing):")
    print(f"   Note: Get private keys from Ganache UI or CLI output")
    for i in range(1, 4):
        acc = accounts[i]
        print(f"   Account {i}: {acc.address}")
    
    print(f"\n💡 Tip: If using Ganache CLI, check the terminal output for private keys")
    print(f"💡 Tip: If using Ganache GUI, click on the key icon next to each account")
    
    print("=" * 60)
    
    return contract

def main():
    """Main function"""
    try:
        contract = deploy_and_configure()
        return contract
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

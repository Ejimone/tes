"""
Deploy WhatsApp contract to Sepolia testnet and update backend
"""
from brownie import Whatsapp, accounts, network, config
import json
import os
import re

def deploy_to_sepolia():
    """Deploy contract to Sepolia and update backend"""
    print("=" * 60)
    print("WhatsApp DApp - Sepolia Deployment")
    print("=" * 60)
    
    # Check network
    if network.show_active() != "sepolia":
        print("❌ Please switch to sepolia network")
        print("Run: brownie run scripts/deploy_sepolia.py --network sepolia")
        return
    
    # Get account from private key
    account = accounts.add(config["wallets"]["from_key"])
    print(f"🌐 Network: {network.show_active()}")
    print(f"👤 Deployer: {account.address}")
    print(f"💰 Balance: {account.balance() / 1e18:.4f} ETH")
    
    if account.balance() == 0:
        print("❌ No ETH balance! Get Sepolia ETH from:")
        print("   🚰 https://sepoliafaucet.com/")
        print("   🚰 https://sepolia-faucet.pk910.de/")
        return
    
    # Deploy contract
    print(f"\n📦 Deploying WhatsApp contract...")
    contract = Whatsapp.deploy({'from': account})
    
    print(f"\n✅ Contract deployed successfully!")
    print(f"📍 Contract Address: {contract.address}")
    print(f"⛽ Gas Used: {contract.tx.gas_used:,}")
    print(f"📄 Transaction Hash: {contract.tx.txid}")
    print(f"🔗 Etherscan: https://sepolia.etherscan.io/tx/{contract.tx.txid}")
    
    # Update backend configuration
    print(f"\n🔧 Updating Google Cloud backend...")
    
    update_cmd = f"""gcloud run services update whatsapp-dapp-backend \\
  --update-env-vars CONTRACT_ADDRESS={contract.address} \\
  --region us-central1"""
    
    print(f"Running: {update_cmd}")
    os.system(update_cmd)
    
    # Save deployment info
    deployment_info = {
        'contract_address': contract.address,
        'deployer': account.address,
        'network': network.show_active(),
        'transaction_hash': contract.tx.txid,
        'gas_used': contract.tx.gas_used,
        'block_number': contract.tx.block_number,
        'etherscan_url': f"https://sepolia.etherscan.io/address/{contract.address}"
    }
    
    deployment_file = 'sepolia_deployment.json'
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n💾 Deployment info saved to: {deployment_file}")
    
    # Register test users if you have ETH
    if account.balance() > 0.01e18:  # If more than 0.01 ETH
        print(f"\n👥 Registering test user...")
        try:
            tx = contract.userRegistration(account.address, "TestUser", {'from': account})
            print(f"   ✅ Registered TestUser at {account.address}")
        except Exception as e:
            print(f"   ⚠️  Failed to register test user: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Sepolia Deployment Complete!")
    print("=" * 60)
    print(f"\n📋 Summary:")
    print(f"   Contract Address: {contract.address}")
    print(f"   Network: Sepolia Testnet")
    print(f"   Backend URL: https://whatsapp-dapp-backend-580832663068.us-central1.run.app")
    print(f"   Etherscan: https://sepolia.etherscan.io/address/{contract.address}")
    print(f"\n🧪 Test your API:")
    print(f"   curl https://whatsapp-dapp-backend-580832663068.us-central1.run.app/api/v1/health")
    print("\n✨ Your backend is now connected to Sepolia testnet!")
    
    return contract

def main():
    """Main function"""
    try:
        contract = deploy_to_sepolia()
        return contract
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure you have Sepolia ETH in your wallet")
        print(f"   2. Check your .env file has the correct PRIVATE_KEY")
        print(f"   3. Verify your Infura endpoint is working")
        raise

if __name__ == "__main__":
    main()
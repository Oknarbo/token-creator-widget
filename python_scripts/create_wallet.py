# create_wallet.py
import sys
import json
import argparse
from solders.keypair import Keypair
from solana.rpc.api import Client
import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description='Kreiraj novi Solana novčanik')
    parser.add_argument('--network', type=str, default='devnet', help='Solana mreža (mainnet-beta, testnet, devnet)')
    return parser.parse_args()

def create_wallet(network):
    try:
        # Kreiraj novi wallet
        wallet = Keypair()
        
        # Spremi private key
        private_key = bytes(wallet.secret()).hex()
        
        # Spremi public key
        public_key = wallet.pubkey()
        
        # Generiraj timestamp za jedinstveno ime datoteke
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wallet_info_{timestamp}.txt"
        
        # Spremi u datoteku s timestamp-om
        with open(filename, "w") as f:
            f.write(f"Private Key: {private_key}\n")
            f.write(f"Public Key: {public_key}\n")
            f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Spremi u glavnu datoteku za widget
        with open("wallet_info.txt", "w") as f:
            f.write(f"Private Key: {private_key}\n")
            f.write(f"Public Key: {public_key}\n")
            f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Odaberi RPC endpoint na temelju mreže
        if network == 'mainnet-beta':
            rpc_url = "https://api.mainnet-beta.solana.com"
        elif network == 'testnet':
            rpc_url = "https://api.testnet.solana.com"
        else:  # devnet
            rpc_url = "https://api.devnet.solana.com"
        
        # Poveži se s mrežom
        client = Client(rpc_url)
        
        # Provjeri stanje
        balance = client.get_balance(public_key)
        balance_value = balance.value / 1000000000  # Pretvori lamporte u SOL
        
        return {
            "success": True,
            "publicKey": str(public_key),
            "privateKey": private_key,
            "network": network,
            "balance": balance_value,
            "filename": filename,
            "message": f"Wallet kreiran i spremljen u {filename}!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "network": network
        }

def main():
    args = parse_arguments()
    
    # Kreiraj novčanik
    result = create_wallet(args.network)
    
    # Ispiši samo JSON rezultat
    print(json.dumps(result))

if __name__ == "__main__":
    main()




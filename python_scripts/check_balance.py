# check_balance.py
import sys
import json
import argparse
from solana.rpc.api import Client

def parse_arguments():
    parser = argparse.ArgumentParser(description='Provjeri stanje Solana novčanika')
    parser.add_argument('--publicKey', type=str, required=True, help='Javni ključ novčanika')
    parser.add_argument('--network', type=str, default='devnet', help='Solana mreža (mainnet-beta, testnet, devnet)')
    return parser.parse_args()

def check_balance(public_key, network):
    try:
        # Konvertuj public_key string u Pubkey objekt
        from solders.pubkey import Pubkey
        pubkey_obj = Pubkey.from_string(public_key)

        # Odaberi RPC endpoint na temelju mreže
        if network == 'mainnet-beta':
            rpc_url = "https://api.mainnet-beta.solana.com"
        elif network == 'testnet':
            rpc_url = "https://api.testnet.solana.com"
        else:  # devnet
            rpc_url = "https://api.devnet.solana.com"

        # Poveži se s mrežom
        client = Client(rpc_url)

        # Dohvati stanje koristeći Pubkey objekt
        balance = client.get_balance(pubkey_obj)
        balance_value = balance.value / 1000000000  # Pretvori lamporte u SOL
        
        return {
            "success": True,
            "publicKey": public_key,
            "network": network,
            "balance": balance_value
        }
    except Exception as e:
        return {
            "success": False,
            "publicKey": public_key,
            "network": network,
            "error": str(e)
        }

def main():
    args = parse_arguments()
    
    # Provjeri stanje novčanika
    result = check_balance(args.publicKey, args.network)
    
    # Ispiši samo JSON rezultat
    print(json.dumps(result))

if __name__ == "__main__":
    main()

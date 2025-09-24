# load_wallet.py
import sys
import os
import json
import argparse
from solders.keypair import Keypair
from solana.rpc.api import Client
import base58
import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description='Učitaj Solana novčanik iz datoteke')
    parser.add_argument('--filePath', type=str, default='wallet_info.txt', help='Putanja do datoteke s informacijama o novčaniku')
    parser.add_argument('--network', type=str, default='devnet', help='Solana mreža (mainnet-beta, testnet, devnet)')
    return parser.parse_args()

def load_wallet_from_file(file_path):
    try:
        # Provjeri postoji li datoteka
        if not os.path.exists(file_path):
            print(json.dumps({
                "error": f"Datoteka {file_path} ne postoji"
            }))
            return None
        
        # Učitaj sadržaj datoteke
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Pronađi privatni ključ
        private_key_line = [line for line in content.split('\n') if line.startswith('Private Key:')]
        if not private_key_line:
            print(json.dumps({
                "error": "Privatni ključ nije pronađen u datoteci"
            }))
            return None
        
        private_key_hex = private_key_line[0].split('Private Key: ')[1].strip()
        
        # Pretvori hex u bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # Kreiraj Keypair iz privatnog ključa
        keypair = Keypair.from_bytes(private_key_bytes)
        
        return keypair
    
    except Exception as e:
        print(json.dumps({
            "error": f"Greška pri učitavanju novčanika: {str(e)}"
        }))
        return None

def main():
    args = parse_arguments()
    
    # Učitaj novčanik iz datoteke
    wallet = load_wallet_from_file(args.filePath)
    if not wallet:
        sys.exit(1)
    
    # Dohvati javni ključ
    public_key = wallet.pubkey()
    
    # Odaberi RPC endpoint na temelju mreže
    if args.network == 'mainnet-beta':
        rpc_url = "https://api.mainnet-beta.solana.com"
    elif args.network == 'testnet':
        rpc_url = "https://api.testnet.solana.com"
    else:  # devnet
        rpc_url = "https://api.devnet.solana.com"
    
    # Poveži se s mrežom
    client = Client(rpc_url)
    
    try:
        # Dohvati stanje
        balance = client.get_balance(public_key)
        balance_value = balance.value / 1000000000  # Pretvori lamporte u SOL
        
        # Ispiši informacije
        print(f"Public Key: {public_key}")
        print(f"Network: {args.network}")
        print(f"Balance: {balance_value} SOL")
        
        # Ispiši JSON za JavaScript integraciju
        print(json.dumps({
            "publicKey": str(public_key),
            "network": args.network,
            "balance": balance_value
        }))
        
    except Exception as e:
        print(f"Greška pri dohvaćanju stanja: {str(e)}")
        print(json.dumps({
            "publicKey": str(public_key),
            "network": args.network,
            "error": str(e)
        }))

if __name__ == "__main__":
    main()

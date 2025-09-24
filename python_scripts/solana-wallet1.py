# wallet.py
from solders.keypair import Keypair
from solana.rpc.api import Client
import datetime

# Kreiraj novi wallet
wallet = Keypair()

# Spremi private key (SAKRIVAJTE OVO!)
private_key = bytes(wallet.secret()).hex()
print(f"Private Key: {private_key}")

# Spremi public key (adresu)
public_key = wallet.pubkey()
print(f"Public Key: {public_key}")

# Generiraj timestamp za jedinstveno ime datoteke
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"wallet_info_{timestamp}.txt"

# Spremi u datoteku s timestamp-om
with open(filename, "w") as f:
    f.write(f"Private Key: {private_key}\n")
    f.write(f"Public Key: {public_key}\n")
    f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"Wallet kreiran i spremljen u {filename}!")

# Također spremi u glavnu datoteku za widget
with open("wallet_info.txt", "w") as f:
    f.write(f"Private Key: {private_key}\n")
    f.write(f"Public Key: {public_key}\n")
    f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("Wallet također spremljen u wallet_info.txt za widget!")

# Povežite se s Solana mrežom
client = Client("https://api.mainnet-beta.solana.com")

# Provjerite stanje
balance = client.get_balance(public_key)
balance_value = balance.value
print(f"Stanje: {balance_value / 1000000000} SOL")
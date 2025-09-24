# transfer_tokens.py
import sys
import json
import argparse
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
import struct

def parse_arguments():
    parser = argparse.ArgumentParser(description='Transfer tokens na Solana blockchainu')
    parser.add_argument('--privateKey', type=str, required=True, help='Privatni ključ novčanika (pošiljalac)')
    parser.add_argument('--mintAddress', type=str, required=True, help='Adresa token mint-a')
    parser.add_argument('--recipient', type=str, required=True, help='Adresa primatelja')
    parser.add_argument('--amount', type=int, required=True, help='Količina tokena za transfer')
    parser.add_argument('--network', type=str, default='devnet', help='Solana mreža (mainnet-beta, testnet, devnet)')
    return parser.parse_args()

def get_rpc_url(network):
    """Dohvati RPC URL na temelju mreže"""
    if network == 'mainnet-beta':
        return "https://api.mainnet-beta.solana.com"
    elif network == 'testnet':
        return "https://api.testnet.solana.com"
    else:  # devnet
        return "https://api.devnet.solana.com"

async def transfer_tokens(private_key, mint_address, recipient_address, amount, network):
    try:
        # Validacija privatnog ključa
        try:
            # Pokušaj prvo kao hex
            if private_key.startswith('0x'):
                private_key = private_key[2:]
                private_key_bytes = bytes.fromhex(private_key)
            elif len(private_key) == 128 and all(c in '0123456789abcdefABCDEF' for c in private_key):
                private_key_bytes = bytes.fromhex(private_key)
            elif len(private_key) == 64 and all(c in '0123456789abcdefABCDEF' for c in private_key):
                private_key_bytes = bytes.fromhex(private_key)
            else:
                # Pokušaj kao base58
                import base58
                private_key_bytes = base58.b58decode(private_key)

            # Kreiraj keypair
            keypair = Keypair.from_seed(private_key_bytes[:32])
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid private key: {str(e)}"
            }

        # Poveži se s RPC-om
        rpc_url = get_rpc_url(network)
        client = AsyncClient(rpc_url)

        if not await client.is_connected():
            return {
                "success": False,
                "error": "Failed to connect to RPC"
            }

        # Validacija adresa
        try:
            mint_pubkey = Pubkey.from_string(mint_address)
            recipient_pubkey = Pubkey.from_string(recipient_address)
        except Exception as e:
            error_msg = str(e)
            if "Invalid Base58 string" in error_msg:
                return {
                    "success": False,
                    "error": f"Invalid address format. Expected valid Solana address."
                }
            else:
                return {
                    "success": False,
                    "error": f"Address validation error: {error_msg}"
                }

        # Provjeri stanje novčanika
        balance = await client.get_balance(keypair.pubkey())
        balance_sol = balance.value / 1_000_000_000

        if balance_sol < 0.01:
            return {
                "success": False,
                "error": f"Insufficient balance: {balance_sol} SOL. Need at least 0.01 SOL"
            }

        # Program IDs
        TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

        # Kreiraj Associated Token Account adrese
        from hashlib import sha256

        # Sender's ATA
        sender_seed = b"\xff" + keypair.pubkey().to_bytes() + TOKEN_PROGRAM_ID.to_bytes() + mint_pubkey.to_bytes()
        sender_hash = sha256(sender_seed).digest()
        sender_ata = Pubkey.from_bytes(sender_hash[:32])

        # Recipient's ATA
        recipient_seed = b"\xff" + recipient_pubkey.to_bytes() + TOKEN_PROGRAM_ID.to_bytes() + mint_pubkey.to_bytes()
        recipient_hash = sha256(recipient_seed).digest()
        recipient_ata = Pubkey.from_bytes(recipient_hash[:32])

        instructions = []

        # Provjeri da li recipient ATA postoji, ako ne kreiraj ga
        recipient_account_info = await client.get_account_info(recipient_ata)
        if recipient_account_info.value is None:
            # Kreiraj recipient ATA
            ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
            create_ata_instruction = Instruction(
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),  # payer
                    AccountMeta(pubkey=recipient_ata, is_signer=False, is_writable=True),  # ata
                    AccountMeta(pubkey=recipient_pubkey, is_signer=False, is_writable=False),  # owner
                    AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),  # mint
                    AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # system
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),  # token
                ],
                data=bytes([])
            )
            instructions.append(create_ata_instruction)

        # Transfer instruction
        transfer_instruction = Instruction(
            program_id=TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=sender_ata, is_signer=False, is_writable=True),  # source
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),  # mint
                AccountMeta(pubkey=recipient_ata, is_signer=False, is_writable=True),  # destination
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),  # authority
            ],
            data=bytes([3]) + struct.pack("<Q", amount)  # Transfer instruction
        )

        instructions.append(transfer_instruction)

        # Pošalji transakciju
        blockhash_resp = await client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash

        message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )

        tx = VersionedTransaction(message, [keypair])
        txid = await client.send_transaction(tx)

        await client.close()

        return {
            "success": True,
            "senderAccount": str(sender_ata),
            "recipientAccount": str(recipient_ata),
            "amount": amount,
            "recipient": recipient_address,
            "mintAddress": mint_address,
            "transactionId": str(txid.value),
            "message": f"Successfully transferred {amount} tokens to {recipient_address}!"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    args = parse_arguments()

    import asyncio
    result = asyncio.run(transfer_tokens(
        args.privateKey,
        args.mintAddress,
        args.recipient,
        args.amount,
        args.network
    ))

    print(json.dumps(result))

if __name__ == "__main__":
    main()











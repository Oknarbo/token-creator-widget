# mint_tokens.py
import sys
import json
import argparse
import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta

def parse_arguments():
    parser = argparse.ArgumentParser(description='Mint tokens na Solana blockchainu')
    parser.add_argument('--privateKey', type=str, required=True, help='Privatni ključ novčanika (mint authority)')
    parser.add_argument('--mintAddress', type=str, required=True, help='Adresa token mint-a')
    parser.add_argument('--amount', type=int, required=True, help='Količina tokena za mintanje')
    parser.add_argument('--destination', type=str, required=True, help='Destinacijska adresa (gdje poslati tokene)')
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

async def mint_tokens(private_key, mint_address, amount, destination_address, network):
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
            destination_pubkey = Pubkey.from_string(destination_address)
        except Exception as e:
            error_msg = str(e)
            if "Invalid Base58 string" in error_msg:
                if mint_address.startswith('Sim'):
                    return {
                        "success": False,
                        "error": "Cannot mint tokens on simulated token. Create a real token first."
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Invalid mint address format. Expected valid Solana address, got: {mint_address[:20]}..."
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
        ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

        # Kreiraj Associated Token Account address
        from hashlib import sha256

        # Associated Token Account formula: sha256(PDA_marker + owner + token_program + mint)
        seed = b"\xff" + destination_pubkey.to_bytes() + TOKEN_PROGRAM_ID.to_bytes() + mint_pubkey.to_bytes()
        hash_result = sha256(seed).digest()
        associated_token_account = Pubkey.from_bytes(hash_result[:32])

        # Provjeri da li ATA već postoji
        account_info = await client.get_account_info(associated_token_account)

        instructions = []

        if account_info.value is None:
            # Kreiraj ATA instrukciju
            create_ata_instruction = Instruction(
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                accounts=[
                    AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),  # payer
                    AccountMeta(pubkey=associated_token_account, is_signer=False, is_writable=True),  # ata
                    AccountMeta(pubkey=destination_pubkey, is_signer=False, is_writable=False),  # owner
                    AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),  # mint
                    AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # system
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),  # token
                ],
                data=bytes([])
            )
            instructions.append(create_ata_instruction)

        # Mint tokens instrukcija
        mint_instruction = Instruction(
            program_id=TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=True),  # mint
                AccountMeta(pubkey=associated_token_account, is_signer=False, is_writable=True),  # destination
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),  # authority
            ],
            data=bytes([7]) + struct.pack("<Q", amount)  # MintTo instruction
        )

        instructions.append(mint_instruction)

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
            "tokenAccount": str(associated_token_account),
            "amount": amount,
            "destination": destination_address,
            "mintAddress": mint_address,
            "transactionId": str(txid.value),
            "message": f"Successfully minted {amount} tokens to {destination_address}!"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    args = parse_arguments()

    import asyncio
    result = asyncio.run(mint_tokens(
        args.privateKey,
        args.mintAddress,
        args.amount,
        args.destination,
        args.network
    ))

    print(json.dumps(result))

if __name__ == "__main__":
    main()

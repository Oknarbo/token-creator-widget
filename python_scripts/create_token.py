# create_token.py
import sys
import json
import argparse
import asyncio
import os
import struct
import base58
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.system_program import create_account, CreateAccountParams, CreateAccountWithSeedParams, create_account_with_seed
from solders.token_program import mint_to, MintToParams, get_associated_token_address, create_associated_token_account, CreateAssociatedTokenAccountParams

def parse_arguments():
    parser = argparse.ArgumentParser(description='Create SPL token on Solana blockchain')
    parser.add_argument('--privateKey', type=str, required=True, help='Wallet private key')
    parser.add_argument('--network', type=str, default='devnet', help='Solana network (mainnet-beta, testnet, devnet)')
    parser.add_argument('--tokenName', type=str, required=True, help='Token name')
    parser.add_argument('--tokenSymbol', type=str, required=True, help='Token symbol')
    parser.add_argument('--totalSupply', type=int, required=True, help='Total token supply')
    parser.add_argument('--decimals', type=int, default=9, help='Number of decimals (default: 9)')
    return parser.parse_args()

def get_rpc_url(network):
    """Get RPC URL based on network"""
    if network == 'mainnet-beta':
        return "https://api.mainnet-beta.solana.com"
    elif network == 'testnet':
        return "https://api.testnet.solana.com"
    else:  # devnet
        return "https://api.devnet.solana.com"

async def create_token(private_key, network, token_name, token_symbol, total_supply, decimals):
    try:
        # Private key validation - supports both hex and base58 format
        try:
            # Try first as hex (if starts with 0x or is just hex)
            if private_key.startswith('0x'):
                private_key_clean = private_key[2:]  # Remove 0x prefix
                private_key_bytes = bytes.fromhex(private_key_clean)
            elif len(private_key) == 128 and all(c in '0123456789abcdefABCDEF' for c in private_key):
                # Hex format without 0x prefix (128 characters for 64 bytes)
                private_key_bytes = bytes.fromhex(private_key)
            elif len(private_key) == 64 and all(c in '0123456789abcdefABCDEF' for c in private_key):
                # 32 byte hex (64 characters)
                private_key_bytes = bytes.fromhex(private_key)
            else:
                # Try as base58
                private_key_bytes = base58.b58decode(private_key)

            # Create keypair from first 32 bytes
            keypair = Keypair.from_seed(private_key_bytes[:32])
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid private key: {str(e)}"
            }

        # Connect to RPC
        rpc_url = get_rpc_url(network)
        client = AsyncClient(rpc_url)

        if not await client.is_connected():
            return {
                "success": False,
                "error": "Failed to connect to RPC"
            }

        # Check wallet balance
        balance = await client.get_balance(keypair.pubkey())
        balance_sol = balance.value / 1_000_000_000

        if balance_sol < 0.01:  # Minimum amount for transactions
            return {
                "success": False,
                "error": f"Insufficient balance: {balance_sol} SOL. Need at least 0.01 SOL"
            }

        # SPL Token Program ID
        TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
        RENT_SYSVAR = Pubkey.from_string("11111111111111111111111111111111")

        # Generate new keypair for token mint
        mint_keypair = Keypair()
        mint_pubkey = mint_keypair.pubkey()

        # Calculate required lamports for mint account
        lamports = await client.get_minimum_balance_for_rent_exemption(82)  # Mint account size

        # Create account instruction for mint
        create_account_instruction = create_account(
            CreateAccountParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=mint_pubkey,
                lamports=lamports.value,
                space=82,  # Mint account size
                owner=TOKEN_PROGRAM_ID
            )
        )

        # Send create account transaction
        blockhash_resp = await client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash

        create_message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[create_account_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )

        create_tx = VersionedTransaction(create_message, [keypair, mint_keypair])
        create_txid = await client.send_transaction(create_tx, opts=TxOpts(skip_preflight=True))

        # Wait for transaction confirmation
        await asyncio.sleep(2)

        # Initialize mint instruction
        initialize_mint_data = (
            struct.pack("<B", 0) +  # InitializeMint discriminator
            struct.pack("<B", decimals) +  # Decimals
            bytes(keypair.pubkey()) +  # Mint authority
            bytes([0]) * 32  # Freeze authority (None)
        )

        initialize_mint_instruction = Instruction(
            program_id=TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=True),
                AccountMeta(pubkey=RENT_SYSVAR, is_signer=False, is_writable=False),
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
            ],
            data=initialize_mint_data
        )

        # Send initialize mint transaction
        blockhash_resp = await client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash

        init_message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[initialize_mint_instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )

        init_tx = VersionedTransaction(init_message, [keypair])
        init_txid = await client.send_transaction(init_tx, opts=TxOpts(skip_preflight=True))

        # Save token information
        token_info = {
            "name": token_name,
            "symbol": token_symbol,
            "mintAddress": str(mint_pubkey),
            "totalSupply": total_supply,
            "decimals": decimals,
            "network": network,
            "createTxId": str(create_txid.value),
            "initTxId": str(init_txid.value)
        }

        # Save to file
        timestamp = asyncio.get_event_loop().time()
        filename = f"token_{token_symbol}_{int(timestamp)}.json"
        with open(filename, "w") as f:
            json.dump(token_info, f, indent=2)

        await client.close()

        return {
            "success": True,
            "token": token_info,
            "filename": filename,
            "message": f"Token {token_name} ({token_symbol}) created successfully!"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    args = parse_arguments()

    # Run async function
    result = asyncio.run(create_token(
        args.privateKey,
        args.network,
        args.tokenName,
        args.tokenSymbol,
        args.totalSupply,
        args.decimals
    ))

    # Ispiši samo JSON rezultat
    print(json.dumps(result))

if __name__ == "__main__":
    main()

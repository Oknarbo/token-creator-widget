# 🚀 Token Creator Widget - Solana Token Creation Suite

A comprehensive web-based tool for creating, managing, and deploying Solana tokens with real blockchain integration, backup systems, and multi-network support.

## ✨ Features

### 🔗 **Real Blockchain Integration**
- **Solana SDK** - Full blockchain interaction
- **Real token creation** - On-chain token deployment
- **Multi-network support** - Devnet, Testnet, Mainnet
- **Wallet management** - Create, load, and manage wallets
- **Balance checking** - Real-time balance monitoring

### 💾 **Advanced Backup System**
- **Automatic backup** - Every 30 seconds
- **File storage** - `data/` folder with JSON files
- **localStorage fallback** - Backup redundancy
- **Export/Import** - Manual backup management
- **Transaction history** - Complete audit trail

### 🛠️ **Token Management**
- **Create SPL tokens** - Full token creation with metadata
- **Mint tokens** - Add supply to existing tokens
- **Transfer tokens** - Send tokens to other addresses
- **Burn tokens** - Remove tokens from circulation
- **Token metadata** - Name, symbol, supply, decimals

### 🌐 **Multi-Network Support**
- **Devnet** - For testing (free SOL from faucet)
- **Testnet** - For testing (free SOL from faucet)
- **Mainnet** - For real transactions (requires SOL)

## 🚀 Installation

### 1. **Clone/Download**
```bash
git clone <repository-url>
cd token-creator-widget
```

### 2. **Install Node.js Dependencies**
```bash
npm install
```

### 3. **Install Python Dependencies**
```bash
pip install -r python_scripts/requirements.txt
```

### 4. **Start the Server**
```bash
npm start
```

### 5. **Open in Browser**
```
http://localhost:3000
```

## 🔧 Configuration

### **Network Selection**
- **Devnet** - For testing (free SOL)
- **Testnet** - For testing (free SOL)
- **Mainnet** - For real transactions (requires SOL)

### **Wallet Management**
- **Create new wallet** - Generate secure keypairs
- **Load existing wallet** - Import from file
- **Balance checking** - Real-time SOL balance
- **Private key security** - Never stored on server

## 💰 Usage

### **Creating Wallets**
1. Click "🔑 Create New Wallet"
2. Wallet is generated with secure keypair
3. Private key is displayed (SAVE SECURELY!)
4. Wallet is automatically backed up

### **Creating Tokens**
1. Fill in token details (name, symbol, supply, decimals)
2. Select network (Devnet for testing)
3. Click "Create Token"
4. Token is deployed on blockchain
5. Transaction details are saved

### **Token Operations**
1. **Mint tokens** - Add supply to existing tokens
2. **Transfer tokens** - Send to other addresses
3. **Burn tokens** - Remove from circulation
4. **Check balances** - Monitor token holdings

## 🔒 Security Features

### **Private Key Management**
- **Secure generation** - Web Crypto API
- **Local storage** - Never sent to server
- **Backup protection** - Encrypted storage
- **Access control** - Wallet selection required

### **Transaction Safety**
- **Network validation** - Prevents wrong network usage
- **Balance checking** - Insufficient funds validation
- **Transaction confirmation** - User confirmation required
- **Error handling** - Comprehensive error management

## 📁 File Structure

```
token-creator-widget/
├── index.html              # Main interface
├── styles.css              # Styling
├── script.js               # Frontend logic
├── server.js               # Express server
├── package.json            # Node.js dependencies
├── python_scripts/         # Python blockchain scripts
│   ├── create_wallet.py    # Wallet creation
│   ├── load_wallet.py      # Wallet loading
│   ├── check_balance.py    # Balance checking
│   ├── create_token.py     # Token creation
│   ├── mint_tokens.py      # Token minting
│   ├── transfer_tokens.py  # Token transfers
│   ├── burn_tokens.py      # Token burning
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Python scripts documentation
├── data/                   # Backup storage
│   ├── wallets.json        # Wallet data
│   ├── tokens.json         # Token data
│   ├── config.json         # Configuration
│   └── backup_*.json       # Automatic backups
└── README.md               # This file
```

## 🌐 Network Endpoints

### **Devnet**
- **RPC**: `https://api.devnet.solana.com`
- **Use**: Testing, development
- **SOL**: Free from faucet

### **Testnet**
- **RPC**: `https://api.testnet.solana.com`
- **Use**: Testing, development
- **SOL**: Free from faucet

### **Mainnet**
- **RPC**: `https://api.mainnet-beta.solana.com`
- **Use**: Real transactions
- **SOL**: Purchase required

## 🚨 Important Notes

### **Before Mainnet Use**
1. **Test thoroughly** on devnet/testnet
2. **Verify wallet balances** before transactions
3. **Check network settings** for your token
4. **Monitor transaction fees** and network conditions
5. **Keep private keys secure** - never share!

### **Security Best Practices**
- **Start small** - test with minimal amounts
- **Use devnet first** - always test before mainnet
- **Backup regularly** - export wallet data
- **Monitor transactions** - check transaction status
- **Keep keys secure** - never share private keys

## 🆘 Troubleshooting

### **Common Issues**

#### **"Failed to connect to network"**
- Check internet connection
- Verify RPC endpoint
- Try different network

#### **"Insufficient balance"**
- Add SOL to wallet
- Check network (devnet vs mainnet)
- Verify wallet selection

#### **"Transaction failed"**
- Check network congestion
- Verify token parameters
- Check SOL balance for fees
- Try again with higher fees

#### **"Backup failed"**
- Check disk space
- Verify folder permissions
- Restart application
- Check console for errors

### **Getting Help**
1. **Check console** for error messages
2. **Verify configuration** settings
3. **Test on devnet** first
4. **Check backup status** in UI
5. **Review transaction logs**

## 🔄 Updates

### **Keeping Updated**
- **Regular backups** - Export data frequently
- **Version tracking** - Check package.json
- **Dependency updates** - Run `npm update`
- **Security patches** - Monitor for updates

## 📞 Support

### **Documentation**
- **This README** - Comprehensive guide
- **Python scripts README** - Script documentation
- **Console logs** - Real-time information
- **UI help text** - Inline guidance

### **Best Practices**
1. **Always test** on devnet first
2. **Keep backups** of all data
3. **Monitor transactions** carefully
4. **Use secure networks** only
5. **Regular maintenance** of dependencies

## 🎯 **Ready to Launch!**

Your Token Creator Widget is now equipped with **real blockchain integration** and **advanced backup systems**!

**🚀 Start with devnet testing, then move to mainnet when ready!**

**💾 Your data is automatically backed up every 30 seconds!**

**⚡ Token creation works on real blockchain networks!**

**🔒 All transactions are secure and protected!**

---

*Built with ❤️ for the Solana ecosystem*
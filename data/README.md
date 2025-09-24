# Data Folder - Backup System

## 📁 Folder Structure

This folder contains all backup data for the Sol Sniper Bot:

### 🔄 Backup Files
- `backup_[timestamp].json` - Timestamped backup files (keeps last 10)
- `latest_backup.json` - Most recent backup
- `wallets.json` - All wallet data
- `tokens.json` - All created tokens
- `config.json` - Application configuration

### 💾 What Gets Backed Up

1. **Wallets**
   - Public keys
   - Private keys (encrypted)
   - Balance information
   - Network settings

2. **Tokens**
   - Token names and symbols
   - Token addresses
   - Metadata (description, image, website, etc.)
   - Creation timestamps
   - DEX information

3. **Configuration**
   - Helius API keys
   - Network settings (devnet/testnet/mainnet)
   - DEX preferences
   - Backup settings

## 🚀 How It Works

### Automatic Backup
- **Every 30 seconds** - Automatic backup to files
- **On page unload** - Backup before closing
- **After token creation** - Immediate backup
- **After wallet creation** - Immediate backup

### Manual Backup
- **Manual Backup button** - Force backup now
- **Export Backup** - Download backup file
- **Import Backup** - Restore from backup file

## 🔒 Security

- All data is stored locally in this folder
- Private keys are stored securely
- Backup files are automatically cleaned up (keeps last 10)
- Data is also backed up to localStorage as fallback

## 📋 Usage

### Copying to Another Computer
1. Copy the entire `sol-sniper-bot` folder
2. Run `npm install` to install dependencies
3. Start with `npm start`
4. All your data will be automatically restored!

### Manual Backup
1. Use "Export Backup" to download backup file
2. Store backup file safely (USB, cloud, etc.)
3. Use "Import Backup" to restore data

## 🆘 Troubleshooting

### If Backup Fails
- Check console for error messages
- Verify data folder permissions
- Check available disk space
- Restart the application

### If Data Won't Load
- Check if `latest_backup.json` exists
- Verify file permissions
- Check console for error messages
- Try manual import from backup file

## 📊 File Sizes

- **Wallets**: ~1-5 KB per wallet
- **Tokens**: ~2-10 KB per token
- **Config**: ~1-2 KB
- **Total**: Usually under 100 KB for normal usage

## 🔄 Cleanup

- Old backup files are automatically deleted
- Only the last 10 backup files are kept
- Individual data files are always kept
- localStorage backup is kept as fallback



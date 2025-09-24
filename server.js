const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;

// Middleware
console.log('🔧 Setting up middleware...');
app.use(express.json());
app.use(express.static(__dirname));
console.log('✅ Middleware setup complete');

// Enhanced logging function
function log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
    console.log(logMessage);

    // Optional: write to log file
    const fs = require('fs');
    const logFile = path.join(__dirname, 'server.log');
    fs.appendFileSync(logFile, logMessage + '\n');
}

// Error handling middleware
app.use((err, req, res, next) => {
    log(`Unhandled error: ${err.message}`, 'error');
    log(`Stack trace: ${err.stack}`, 'error');

    if (!res.headersSent) {
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
        });
    }
});

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    log('📁 Created data directory', 'info');
}

console.log('🔧 Setting up routes...');

// Backup API endpoints
app.post('/api/backup', (req, res) => {
    try {
        const backupData = req.body;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        // Save main backup
        const backupFile = path.join(dataDir, `backup_${timestamp}.json`);
        fs.writeFileSync(backupFile, JSON.stringify(backupData, null, 2));
        
        // Save latest backup
        const latestBackupFile = path.join(dataDir, 'latest_backup.json');
        fs.writeFileSync(latestBackupFile, JSON.stringify(backupData, null, 2));
        
        // Save individual data files
        if (backupData.wallets && backupData.wallets.length > 0) {
            const walletsFile = path.join(dataDir, 'wallets.json');
            fs.writeFileSync(walletsFile, JSON.stringify(backupData.wallets, null, 2));
        }
        
        if (backupData.tokens && backupData.tokens.length > 0) {
            const tokensFile = path.join(dataDir, 'tokens.json');
            fs.writeFileSync(tokensFile, JSON.stringify(backupData.tokens, null, 2));
        }
        
        if (backupData.config) {
            const configFile = path.join(dataDir, 'config.json');
            fs.writeFileSync(configFile, JSON.stringify(backupData.config, null, 2));
        }
        
        // Clean up old backups (keep last 10)
        cleanupOldBackups();
        
        log('✅ Backup saved successfully', 'success');
        res.json({ success: true, message: 'Backup saved', timestamp });

    } catch (error) {
        log(`❌ Backup error: ${error.message}`, 'error');
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/api/backup', (req, res) => {
    try {
        const latestBackupFile = path.join(dataDir, 'latest_backup.json');
        
        if (fs.existsSync(latestBackupFile)) {
            const backupData = JSON.parse(fs.readFileSync(latestBackupFile, 'utf8'));
            res.json(backupData);
        } else {
            res.status(404).json({ success: false, message: 'No backup found' });
        }
        
    } catch (error) {
        console.error('❌ Load backup error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get backup list
app.get('/api/backups', (req, res) => {
    try {
        const files = fs.readdirSync(dataDir);
        const backups = files
            .filter(file => file.startsWith('backup_') && file.endsWith('.json'))
            .map(file => {
                const filePath = path.join(dataDir, file);
                const stats = fs.statSync(filePath);
                return {
                    filename: file,
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => new Date(b.modified) - new Date(a.modified));
        
        res.json({ success: true, backups });
        
    } catch (error) {
        console.error('❌ Get backups error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Delete specific backup
app.delete('/api/backup/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const filePath = path.join(dataDir, filename);
        
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            console.log(`🗑️ Deleted backup: ${filename}`);
            res.json({ success: true, message: 'Backup deleted' });
        } else {
            res.status(404).json({ success: false, message: 'Backup not found' });
        }
        
    } catch (error) {
        console.error('❌ Delete backup error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get data directory info
app.get('/api/data-info', (req, res) => {
    try {
        const files = fs.readdirSync(dataDir);
        const totalSize = files.reduce((size, file) => {
            const filePath = path.join(dataDir, file);
            const stats = fs.statSync(filePath);
            return size + stats.size;
        }, 0);
        
        res.json({
            success: true,
            dataDir: dataDir,
            fileCount: files.length,
            totalSize: totalSize,
            files: files
        });
        
    } catch (error) {
        console.error('❌ Get data info error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get wallets
app.get('/api/wallets', (req, res) => {
    try {
        const walletsFile = path.join(dataDir, 'wallets.json');
        
        if (fs.existsSync(walletsFile)) {
            const wallets = JSON.parse(fs.readFileSync(walletsFile, 'utf8'));
            res.json({ success: true, wallets });
        } else {
            res.json({ success: true, wallets: [] });
        }
        
    } catch (error) {
        console.error('❌ Get wallets error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get tokens
app.get('/api/tokens', (req, res) => {
    try {
        const tokensFile = path.join(dataDir, 'tokens.json');

        if (fs.existsSync(tokensFile)) {
            const tokens = JSON.parse(fs.readFileSync(tokensFile, 'utf8'));
            res.json({ success: true, tokens });
        } else {
            res.json({ success: true, tokens: [] });
        }

    } catch (error) {
        console.error('❌ Get tokens error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Python script execution endpoints
console.log('🔧 Registering Python API endpoints...');

app.post('/api/python/create-wallet', (req, res) => {
    console.log('📡 Received POST /api/python/create-wallet');
    const { network = 'devnet' } = req.body;

    console.log(`🐍 Executing create_wallet.py with network: ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'create_wallet.py'),
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python create_wallet script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                output: stdout,
                stderr: stderr
            });
        }
    });

    pythonProcess.on('error', (error) => {
        console.error('❌ Failed to start Python process:', error);
        res.status(500).json({
            success: false,
            error: `Failed to execute Python script: ${error.message}`
        });
    });
});

app.post('/api/python/check-balance', (req, res) => {
    const { publicKey, network = 'devnet' } = req.body;

    if (!publicKey) {
        return res.status(400).json({
            success: false,
            error: 'Public key is required'
        });
    }

    console.log(`🐍 Executing check_balance.py for ${publicKey} on ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'check_balance.py'),
        '--publicKey', publicKey,
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python check_balance script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                output: stdout,
                stderr: stderr
            });
        }
    });

    pythonProcess.on('error', (error) => {
        console.error('❌ Failed to start Python process:', error);
        res.status(500).json({
            success: false,
            error: `Failed to execute Python script: ${error.message}`
        });
    });
});

app.post('/api/python/load-wallet', (req, res) => {
    const { filePath = 'wallet_info.txt', network = 'devnet' } = req.body;

    console.log(`🐍 Executing load_wallet.py with file: ${filePath} on ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'load_wallet.py'),
        '--filePath', filePath,
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python load_wallet script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                output: stdout,
                stderr: stderr
            });
        }
    });

    pythonProcess.on('error', (error) => {
        console.error('❌ Failed to start Python process:', error);
        res.status(500).json({
            success: false,
            error: `Failed to execute Python script: ${error.message}`
        });
    });
});

// Create token endpoint
app.post('/api/python/create-token', (req, res) => {
    const {
        privateKey,
        network = 'devnet',
        tokenName,
        tokenSymbol,
        totalSupply,
        decimals = 9
    } = req.body;

    if (!privateKey || !tokenName || !tokenSymbol || !totalSupply) {
        return res.status(400).json({
            success: false,
            error: 'Missing required parameters: privateKey, tokenName, tokenSymbol, totalSupply'
        });
    }

    console.log(`🐍 Executing create_token.py for ${tokenName} (${tokenSymbol})`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'create_token.py'),
        '--privateKey', privateKey,
        '--network', network,
        '--tokenName', tokenName,
        '--tokenSymbol', tokenSymbol,
        '--totalSupply', totalSupply.toString(),
        '--decimals', decimals.toString()
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python create_token script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                output: stdout,
                stderr: stderr
            });
        }
    });

    pythonProcess.on('error', (error) => {
        console.error('❌ Failed to start Python process:', error);
        res.status(500).json({
            success: false,
            error: `Failed to execute Python script: ${error.message}`
        });
    });
});

// Get server logs
app.get('/api/logs', (req, res) => {
    try {
        const logFile = path.join(__dirname, 'server.log');
        const lines = req.query.lines ? parseInt(req.query.lines) : 100; // Default last 100 lines

        if (fs.existsSync(logFile)) {
            const logContent = fs.readFileSync(logFile, 'utf8');
            const logLines = logContent.split('\n').filter(line => line.trim());

            // Return last N lines
            const recentLines = logLines.slice(-lines);

            res.json({
                success: true,
                logs: recentLines,
                totalLines: logLines.length,
                returnedLines: recentLines.length
            });
        } else {
            res.json({
                success: true,
                logs: [],
                message: 'No log file found'
            });
        }

    } catch (error) {
        log(`❌ Error reading logs: ${error.message}`, 'error');
        res.status(500).json({ success: false, error: error.message });
    }
});

// Clear server logs
app.delete('/api/logs', (req, res) => {
    try {
        const logFile = path.join(__dirname, 'server.log');

        if (fs.existsSync(logFile)) {
            fs.unlinkSync(logFile);
            log('🗑️ Server logs cleared', 'info');
            res.json({ success: true, message: 'Logs cleared' });
        } else {
            res.json({ success: true, message: 'No log file to clear' });
        }

    } catch (error) {
        log(`❌ Error clearing logs: ${error.message}`, 'error');
        res.status(500).json({ success: false, error: error.message });
    }
});

// Mint tokens endpoint
app.post('/api/python/mint-tokens', (req, res) => {
    const {
        privateKey,
        mintAddress,
        amount,
        destination,
        network = 'devnet'
    } = req.body;

    if (!privateKey || !mintAddress || !amount || !destination) {
        return res.status(400).json({
            success: false,
            error: 'Missing required parameters: privateKey, mintAddress, amount, destination'
        });
    }

    console.log(`🐍 Minting ${amount} tokens to ${destination} on ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'mint_tokens.py'),
        '--privateKey', privateKey,
        '--mintAddress', mintAddress,
        '--amount', amount.toString(),
        '--destination', destination,
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python mint_tokens script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error.message);
            console.error('❌ Raw stdout:', stdout);
            console.error('❌ Raw stderr:', stderr);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                details: error.message
            });
        }
    });
});

// Transfer tokens endpoint
app.post('/api/python/transfer-tokens', (req, res) => {
    const {
        privateKey,
        mintAddress,
        recipient,
        amount,
        network = 'devnet'
    } = req.body;

    if (!privateKey || !mintAddress || !recipient || !amount) {
        return res.status(400).json({
            success: false,
            error: 'Missing required parameters: privateKey, mintAddress, recipient, amount'
        });
    }

    console.log(`🐍 Transferring ${amount} tokens to ${recipient} on ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'transfer_tokens.py'),
        '--privateKey', privateKey,
        '--mintAddress', mintAddress,
        '--recipient', recipient,
        '--amount', amount.toString(),
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python transfer_tokens script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error.message);
            console.error('❌ Raw stdout:', stdout);
            console.error('❌ Raw stderr:', stderr);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                details: error.message
            });
        }
    });
});

// Burn tokens endpoint
app.post('/api/python/burn-tokens', (req, res) => {
    const {
        privateKey,
        mintAddress,
        amount,
        network = 'devnet'
    } = req.body;

    if (!privateKey || !mintAddress || !amount) {
        return res.status(400).json({
            success: false,
            error: 'Missing required parameters: privateKey, mintAddress, amount'
        });
    }

    console.log(`🐍 Burning ${amount} tokens on ${network}`);

    const pythonProcess = spawn('python', [
        path.join(__dirname, 'python_scripts', 'burn_tokens.py'),
        '--privateKey', privateKey,
        '--mintAddress', mintAddress,
        '--amount', amount.toString(),
        '--network', network
    ], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
        try {
            if (code === 0) {
                console.log('📄 Raw stdout:', stdout);
                const result = JSON.parse(stdout);
                console.log('✅ Python burn_tokens script executed successfully');
                res.json(result);
            } else {
                console.error('❌ Python script error:', stderr);
                res.status(500).json({
                    success: false,
                    error: stderr || 'Python script execution failed'
                });
            }
        } catch (error) {
            console.error('❌ JSON parse error:', error.message);
            console.error('❌ Raw stdout:', stdout);
            console.error('❌ Raw stderr:', stderr);
            res.status(500).json({
                success: false,
                error: 'Failed to parse Python script output',
                details: error.message
            });
        }
    });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: require('./package.json').version
    });
});

console.log('✅ All routes registered successfully');

// Clean up old backups (keep last 10)
function cleanupOldBackups() {
    try {
        const files = fs.readdirSync(dataDir);
        const backupFiles = files
            .filter(file => file.startsWith('backup_') && file.endsWith('.json'))
            .map(file => {
                const filePath = path.join(dataDir, file);
                const stats = fs.statSync(filePath);
                return { filename: file, modified: stats.mtime };
            })
            .sort((a, b) => new Date(b.modified) - new Date(a.modified));
        
        // Keep only last 10 backups
        if (backupFiles.length > 10) {
            const filesToDelete = backupFiles.slice(10);
            filesToDelete.forEach(file => {
                const filePath = path.join(dataDir, file.filename);
                fs.unlinkSync(filePath);
                console.log(`🗑️ Cleaned up old backup: ${file.filename}`);
            });
        }
        
    } catch (error) {
        console.error('❌ Cleanup error:', error);
    }
}

// Error handling middleware (must be last)
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    if (!res.headersSent) {
        res.status(500).json({
            success: false,
            error: 'Internal server error',
            message: err.message
        });
    }
});

// 404 handler
app.use((req, res) => {
    console.log(`404 - Route not found: ${req.method} ${req.url}`);
    res.status(404).json({
        success: false,
        error: 'Route not found',
        path: req.url,
        method: req.method
    });
});

// Start server
try {
    const server = app.listen(PORT, () => {
        console.log(`🚀 Server running on http://localhost:${PORT}`);
        console.log(`📁 Data directory: ${dataDir}`);
        console.log(`💾 Backup system ready`);
        console.log(`🔗 Available routes:`);
        console.log(`   POST /api/python/create-wallet`);
        console.log(`   POST /api/python/check-balance`);
        console.log(`   POST /api/python/load-wallet`);
        console.log(`   POST /api/python/create-token`);
        console.log(`   POST /api/python/mint-tokens`);
        console.log(`   POST /api/python/transfer-tokens`);
        console.log(`   POST /api/python/burn-tokens`);
        console.log(`   GET /api/health`);
        console.log(`   GET /api/logs`);
    });

    server.on('error', (error) => {
        console.error('❌ Server error:', error);
    });
} catch (error) {
    console.error('❌ Failed to start server:', error);
}

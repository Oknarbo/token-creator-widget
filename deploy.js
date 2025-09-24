#!/usr/bin/env node

/**
 * Launch Your SOL - Deployment Script
 * Automatski deployment na Vercel
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 LAUNCH YOUR SOL - DEPLOYMENT SCRIPT');
console.log('=====================================\n');

// Provjeri da li je Vercel CLI instaliran
try {
  execSync('vercel --version', { stdio: 'pipe' });
  console.log('✅ Vercel CLI je instaliran');
} catch (error) {
  console.log('❌ Vercel CLI nije instaliran');
  console.log('📦 Instaliraj sa: npm i -g vercel\n');
  process.exit(1);
}

// Provjeri da li je korisnik prijavljen
try {
  execSync('vercel whoami', { stdio: 'pipe' });
  console.log('✅ Prijavljen u Vercel');
} catch (error) {
  console.log('❌ Nisi prijavljen u Vercel');
  console.log('🔐 Prijavi se sa: vercel login\n');
  process.exit(1);
}

// Provjeri da li postoji .env fajl
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
  console.log('⚠️  Nema .env fajla - kreiram template...');

  const envTemplate = `# Environment Variables
NODE_ENV=production
PORT=3000

# RPC Endpoints (opciono - koristi default)
# DEVNET_RPC=https://api.devnet.solana.com
# MAINNET_RPC=https://api.mainnet-beta.solana.com

# Database (ako koristite)
# DATABASE_URL=postgresql://...

# Analytics (opciono)
# ANALYTICS_ID=your_analytics_id
`;

  fs.writeFileSync(envPath, envTemplate);
  console.log('✅ Kreiran .env template');
}

// Git status
try {
  console.log('\n📋 Git status:');
  const gitStatus = execSync('git status --porcelain', { encoding: 'utf8' });
  if (gitStatus.trim()) {
    console.log('📝 Nepreuzete promjene:');
    console.log(gitStatus);
  } else {
    console.log('✅ Svi fajlovi su preuzeti');
  }
} catch (error) {
  console.log('❌ Git repository nije inicijaliziran');
  console.log('🔧 Inicijaliziraj sa: git init');
}

// Deploy na Vercel
console.log('\n🚀 Započinjem deployment na Vercel...');

try {
  // Dodaj sve fajlove
  execSync('git add .', { stdio: 'inherit' });

  // Commit
  try {
    execSync('git commit -m "Deploy to Vercel"', { stdio: 'inherit' });
  } catch (error) {
    console.log('⚠️  Nema novih promjena za commit');
  }

  // Vercel deploy
  console.log('\n📦 Deploying to Vercel...');
  execSync('vercel --prod', { stdio: 'inherit' });

  console.log('\n🎉 DEPLOYMENT USPJEŠAN!');
  console.log('============================');
  console.log('🌐 Tvoja aplikacija je sada dostupna!');
  console.log('📱 Dijeli link sa prijateljima!');
  console.log('📊 Provjeri analytics u Vercel dashboard-u');

} catch (error) {
  console.log('\n❌ DEPLOYMENT FAILED');
  console.log('==================');
  console.log('Greška:', error.message);
  console.log('\n🔧 Provjeri:');
  console.log('- Da li je Vercel CLI ažuriran');
  console.log('- Da li su svi dependencies instalirani');
  console.log('- Da li je .env fajl ispravno konfiguriran');
}

// Pokreni lokalno za testiranje
console.log('\n🧪 Za lokalno testiranje:');
console.log('npm start');
console.log('http://localhost:3000');

console.log('\n📚 Korisne komande:');
console.log('vercel logs     # Vidi logove');
console.log('vercel domains  # Upravljaj domenama');
console.log('vercel env      # Environment variables');

console.log('\n🎯 SLJEDEĆI KORACI:');
console.log('1. 🌐 Kupi domenu (Namecheap, GoDaddy)');
console.log('2. 🔗 Poveži domenu sa Vercel-om');
console.log('3. 📢 Objavi na Twitter/X, Discord');
console.log('4. 📊 Dodaj Google Analytics');
console.log('5. 💰 Postavi monetizaciju');

console.log('\n🚀 SRETNO S LAUNCH-YOUR-SOL.COM! 🔥');











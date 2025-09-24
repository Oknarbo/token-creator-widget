# 🐍 Python Scripts for Token Creator Widget

## 📋 **Dostupne skripte:**

### **1. create_wallet.py**
Kreira novi Solana novčanik i sprema ga u datoteku.

```bash
python create_wallet.py --network devnet
```

**Parametri:**
- `--network`: Solana mreža (devnet, testnet, mainnet-beta)

**Rezultat:**
- Kreira `wallet_info.txt` s privatnim i javnim ključem
- Kreira `wallet_info_TIMESTAMP.txt` s timestamp-om
- Vraća JSON s informacijama o novčaniku

### **2. load_wallet.py**
Učitava postojeći novčanik iz datoteke.

```bash
python load_wallet.py --filePath wallet_info.txt --network devnet
```

**Parametri:**
- `--filePath`: Putanja do datoteke s novčanikom
- `--network`: Solana mreža (devnet, testnet, mainnet-beta)

**Rezultat:**
- Učitava privatni ključ iz datoteke
- Generira javni ključ
- Dohvaća trenutno stanje s mreže

### **3. check_balance.py**
Provjerava stanje postojećeg novčanika.

```bash
python check_balance.py --publicKey YOUR_PUBLIC_KEY --network devnet
```

**Parametri:**
- `--publicKey`: Javni ključ novčanika
- `--network`: Solana mreža (devnet, testnet, mainnet-beta)

**Rezultat:**
- Dohvaća trenutno stanje s mreže
- Vraća JSON s informacijama o stanju

## 🚀 **Instalacija:**

### **1. Instalirajte Python pakete:**
```bash
pip install -r requirements.txt
```

### **2. Provjerite instalaciju:**
```bash
python --version
pip list | grep solana
```

## 🔧 **Korištenje u widgetu:**

1. **Kreirajte novčanik:**
   - Kliknite "🔑 Kreiraj novi novčanik" u widgetu
   - Widget će automatski pozvati `create_wallet.py`

2. **Učitajte postojeći novčanik:**
   - Kliknite "📂 Učitaj postojeći" u widgetu
   - Widget će automatski pozvati `load_wallet.py`

3. **Provjerite stanje:**
   - Kliknite "🔄 Osvježi balans" u widgetu
   - Widget će automatski pozvati `check_balance.py`

## 📁 **Struktura datoteka:**

```
python_scripts/
├── __init__.py              # Python paket inicijalizacija
├── create_wallet.py         # Kreiranje novog novčanika
├── load_wallet.py           # Učitavanje postojećeg novčanika
├── check_balance.py         # Provjera stanja
├── requirements.txt         # Potrebni Python paketi
└── README.md               # Ova datoteka
```

## ⚠️ **Važne napomene:**

- **Privatni ključevi su osjetljivi** - nikada ih ne dijelite
- **Testirajte na devnet** prije korištenja mainnet-a
- **Backup wallet_info.txt** datoteke
- **Provjerite mrežu** prije izvršavanja skripti

## 🆘 **Rješavanje problema:**

### **Greška: "ModuleNotFoundError: No module named 'solana'"**
```bash
pip install solana solders base58
```

### **Greška: "Permission denied"**
```bash
# Windows: Pokrenite kao administrator
# Linux/Mac: dodajte sudo
sudo python create_wallet.py
```

### **Greška: "Network connection failed"**
- Provjerite internet vezu
- Provjerite jesu li RPC endpoint-i dostupni
- Pokušajte s drugom mrežom (devnet umjesto mainnet)

---

**🎉 Uživajte u Python integraciji s Token Creator Widgetom!**




# Soliq.uz QR Fayl Bot

Telegram bot orqali fayllarni yuklash, QR kod yaratish va PDF/Word konvertatsiya qilish xizmati.

## Xususiyatlar

- 📤 Fayllarni yuklash va doimiy havola olish
- 🔲 QR kod yaratish va skanerlash
- 📄 PDF ↔ Word konvertatsiya
- 📋 Word faylga QR kod qo'shish
- 📄 PDF faylga QR kod qo'shish
- 👑 Admin paneli
- 🔒 Foydalanuvchi ruxsati boshqaruvi

## O'rnatish

### 1. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Environment o'zgaruvchilarini o'rnatish

Windows PowerShell da:
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_bot_token_here"
$env:ADMIN_TELEGRAM_ID = "your_admin_id_here"
```

Yoki .env fayl yarating:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_ID=your_admin_id_here
```

### 3. Telegram Bot Token olish

1. @BotFather ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username ni kiriting
4. Token ni oling

### 4. Admin ID olish

1. @userinfobot ga o'ting
2. Sizning ID ni oling

## Ishga tushirish

### Lokal ishga tushirish

#### 1. File server ni ishga tushirish
```bash
python file_server.py
```

#### 2. Bot ni ishga tushirish
```bash
python bot.py
```

### Railway da ishga tushirish

#### 1. Railway ga deploy qilish
1. Railway.app ga o'ting
2. "New Project" ni bosing
3. GitHub repository ni ulang
4. Environment variables ni o'rnating:
   - `TELEGRAM_BOT_TOKEN` - Bot token
   - `ADMIN_TELEGRAM_ID` - Admin ID
5. Deploy qiling

#### 2. Environment variables
Railway da quyidagi o'zgaruvchilarni o'rnating:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_TELEGRAM_ID=your_admin_id_here
```

#### 3. Avtomatik ishga tushish
Railway da `start.py` fayl avtomatik ishga tushadi va ikkala xizmatni (file server + bot) bir vaqtda ishlatadi.

## Foydalanish

1. Botga `/start` buyrug'ini yuboring
2. Admin sizga ruxsat bersin
3. Quyidagi xizmatlardan foydalaning:
   - 📤 Fayl yuborish
   - 🔄 PDF ↔ Word
   - 📋 Word faylga QR qo'shish
   - 📄 PDF faylga QR qo'shish

## Admin buyruqlari

- `/admin` - Admin panelini ochish
- `/start` - Botni ishga tushirish

## Texnik ma'lumotlar

- Python 3.11+
- Flask (file server)
- python-telegram-bot
- SQLite (ma'lumotlar bazasi)
- PyMuPDF (PDF ishlov berish)
- python-docx (Word ishlov berish)
- qrcode (QR kod yaratish)

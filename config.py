import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))

# Railway Configuration
RAILWAY_URL = os.getenv('RAILWAY_PUBLIC_DOMAIN')
REPLIT_URL = os.getenv('REPLIT_DEV_DOMAIN')

# File Server Configuration
PORT = int(os.getenv('PORT', '5000'))
HOST = os.getenv('HOST', '0.0.0.0')

# Railway specific port
if RAILWAY_URL:
    PORT = int(os.getenv('PORT', '5000'))

# Database Configuration
DB_FILE = os.getenv('DB_FILE', 'bot_database.db')

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '20971520'))  # 20MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
QR_FOLDER = os.getenv('QR_FOLDER', 'qr_codes')

# Allowed File Extensions
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 
    'pdf,docx,doc,xlsx,xls,jpg,jpeg,png,gif,bmp,zip,rar,7z,txt,pptx,ppt'
).split(','))

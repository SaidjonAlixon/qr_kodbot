#!/usr/bin/env python3
"""
Railway uchun start fayl - file server va bot ni bir vaqtda ishga tushiradi
"""
import os
import sys
import threading
import time
import subprocess
from config import RAILWAY_URL, PORT

def start_file_server():
    """File server ni ishga tushirish"""
    print("File server ishga tushmoqda...")
    try:
        import file_server
        file_server.app.run(host='0.0.0.0', port=PORT, debug=False)
    except Exception as e:
        print(f"File server xatoligi: {e}")

def start_bot():
    """Bot ni ishga tushirish"""
    print("Bot ishga tushmoqda...")
    try:
        print("Bot ni alohida process da ishga tushiramiz...")
        subprocess.Popen([sys.executable, 'bot.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        print("Bot process ishga tushdi!")
    except Exception as e:
        print(f"Bot xatoligi: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Asosiy funksiya"""
    print("Railway da ishga tushmoqda...")
    
    # Token tekshirish
    from config import TELEGRAM_BOT_TOKEN
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("XATOLIK: TELEGRAM_BOT_TOKEN o'rnatilmagan!")
        print("Railway da Environment Variables da TELEGRAM_BOT_TOKEN ni o'rnating.")
        print("Faqat file server ishlaydi...")
        
        # Faqat file server ni ishga tushirish
        start_file_server()
        return
    
    # File server ni alohida thread da ishga tushirish
    file_server_thread = threading.Thread(target=start_file_server, daemon=True)
    file_server_thread.start()
    
    # Kichik kutish
    time.sleep(2)
    
    # Bot ni ishga tushirish
    start_bot()

if __name__ == '__main__':
    main()

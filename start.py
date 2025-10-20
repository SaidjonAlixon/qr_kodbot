#!/usr/bin/env python3
"""
Railway uchun start fayl - file server va bot ni bir vaqtda ishga tushiradi
"""
import os
import sys
import threading
import time
from config import RAILWAY_URL, PORT, TELEGRAM_BOT_TOKEN

def start_file_server():
    """File server ni ishga tushirish"""
    print("File server ishga tushmoqda...")
    try:
        import file_server
        file_server.app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        print(f"File server xatoligi: {e}")

def start_bot():
    """Bot ni ishga tushirish"""
    print("Bot ishga tushmoqda...")
    try:
        print("Bot modulini import qilmoqda...")
        import bot
        print("Bot moduli import qilindi, main() ni chaqirmoqda...")
        bot.main()
    except Exception as e:
        print(f"Bot xatoligi: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Asosiy funksiya"""
    print("Railway da ishga tushmoqda...")
    print(f"TELEGRAM_BOT_TOKEN mavjud: {bool(TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE')}")
    
    # Token tekshirish
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("XATOLIK: TELEGRAM_BOT_TOKEN o'rnatilmagan!")
        print("Railway da Environment Variables da TELEGRAM_BOT_TOKEN ni o'rnating.")
        print("Faqat file server ishlaydi...")
        
        # Faqat file server ni ishga tushirish
        start_file_server()
        return
    
    print("Token mavjud, ikkala xizmatni ishga tushiramiz...")
    
    # File server ni alohida thread da ishga tushirish
    file_server_thread = threading.Thread(target=start_file_server, daemon=True)
    file_server_thread.start()
    
    # Kichik kutish
    time.sleep(3)
    
    # Bot ni ishga tushirish
    start_bot()

if __name__ == '__main__':
    main()

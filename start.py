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
        import bot
        bot.main()
    except Exception as e:
        print(f"Bot xatoligi: {e}")

def main():
    """Asosiy funksiya"""
    print("Railway da ishga tushmoqda...")
    
    # File server ni alohida thread da ishga tushirish
    file_server_thread = threading.Thread(target=start_file_server, daemon=True)
    file_server_thread.start()
    
    # Kichik kutish
    time.sleep(2)
    
    # Bot ni ishga tushirish
    start_bot()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Railway test fayl - environment o'zgaruvchilarini tekshirish
"""
import os

print("=== RAILWAY TEST ===")
print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN', 'NOT SET')}")
print(f"ADMIN_TELEGRAM_ID: {os.getenv('ADMIN_TELEGRAM_ID', 'NOT SET')}")
print(f"RAILWAY_PUBLIC_DOMAIN: {os.getenv('RAILWAY_PUBLIC_DOMAIN', 'NOT SET')}")
print("===================")

# Config import qilish
try:
    from config import TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID, RAILWAY_URL
    print(f"Config TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10] if TELEGRAM_BOT_TOKEN else 'None'}...")
    print(f"Config ADMIN_TELEGRAM_ID: {ADMIN_TELEGRAM_ID}")
    print(f"Config RAILWAY_URL: {RAILWAY_URL}")
except Exception as e:
    print(f"Config import xatoligi: {e}")

print("Test tugadi!")
print("10 soniya kutamiz...")
import time
time.sleep(10)
print("Test to'liq tugadi!")
print("Endi bot.py ni ishga tushiramiz...")

# Bot ni ishga tushirish
try:
    import subprocess
    import sys
    print("Bot ni alohida process da ishga tushiramiz...")
    subprocess.Popen([sys.executable, 'bot.py'])
    print("Bot process ishga tushdi!")
except Exception as e:
    print(f"Bot ishga tushirishda xatolik: {e}")

print("Barcha jarayonlar tugadi!")

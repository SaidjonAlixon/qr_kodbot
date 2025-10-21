#!/usr/bin/env python3
"""
URL test fayl
"""
import os

print("=== URL TEST ===")
print(f"RAILWAY_PUBLIC_DOMAIN: {os.getenv('RAILWAY_PUBLIC_DOMAIN')}")
print(f"RAILWAY_URL: {os.getenv('RAILWAY_URL')}")
print(f"PORT: {os.getenv('PORT')}")

# Config import qilish
try:
    from config import RAILWAY_URL, REPLIT_URL
    print(f"Config RAILWAY_URL: {RAILWAY_URL}")
    print(f"Config REPLIT_URL: {REPLIT_URL}")
except Exception as e:
    print(f"Config import xatoligi: {e}")

# get_base_url funksiyasini test qilish
try:
    from bot import get_base_url
    url = get_base_url()
    print(f"get_base_url() natijasi: {url}")
except Exception as e:
    print(f"get_base_url() xatoligi: {e}")

print("=== URL TEST TUGADI ===")

#!/usr/bin/env python
"""
Django server va Telegram botni birdaniga ishga tushirish
"""
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

# Django yo'lini qo'shish
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

def run_django_server():
    """Django serverni ishga tushirish"""
    try:
        print("🚀 Django server ishga tushmoqda...")
        execute_from_command_line(['manage.py', 'runserver', '--noreload'])
    except KeyboardInterrupt:
        print("🛑 Django server to'xtatildi")
    except Exception as e:
        print(f"❌ Django server xatosi: {e}")

def run_telegram_bot():
    """Telegram botni ishga tushirish"""
    try:
        time.sleep(3)  # Django serverning ishga tushishini kutish
        print("🤖 Telegram bot ishga tushmoqda...")
        execute_from_command_line(['manage.py', 'runbot'])
    except KeyboardInterrupt:
        print("🛑 Telegram bot to'xtatildi")
    except Exception as e:
        print(f"❌ Telegram bot xatosi: {e}")

def main():
    """Asosiy funksiya"""
    print("🚀 Django loyihasi va Telegram bot ishga tushmoqda...")
    print("🔗 Admin panel: http://127.0.0.1:8000/admin")
    print("⏹️  To'xtatish uchun Ctrl+C bosing")
    print("-" * 50)
    
    try:
        # Django serverni alohida threadda ishga tushirish
        django_thread = threading.Thread(target=run_django_server, daemon=True)
        django_thread.start()
        
        # Telegram botni asosiy threadda ishga tushirish
        run_telegram_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Barcha xizmatlar to'xtatildi")
    except Exception as e:
        print(f"❌ Umumiy xato: {e}")

if __name__ == "__main__":
    main()

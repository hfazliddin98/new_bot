#!/usr/bin/env python
"""
PythonAnywhere uchun bot ishga tushirish skripti
Bu skriptni PythonAnywhere'da Tasks yoki Always-On Tasks orqali ishga tushiring

Ishlatish:
1. Django management command orqali:
   python manage.py start_telegram_bot

2. To'g'ridan-to'g'ri shu skript orqali:
   python start_bot.py
"""

import os
import sys
import django
from pathlib import Path

# Django loyihasining ildiz papkasini qo'shish
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Django sozlamalarini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')

# Django'ni sozlash
django.setup()

def main():
    """Bot ishga tushirish"""
    try:
        print("🚀 Bot ishga tushirish skripti boshlandi...")
        
        # Django management command orqali ishga tushirish (tavsiya etiladi)
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'start_telegram_bot'])
        
    except KeyboardInterrupt:
        print("\n🛑 Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Bot ishga tushishda xatolik: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
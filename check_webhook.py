#!/usr/bin/env python
"""
Telegram bot webhook holatini tekshirish
"""
import os
import sys
import django
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from django.conf import settings
import telebot

def check_webhook():
    """Webhook holatini tekshirish"""
    print("=" * 60)
    print("🔍 TELEGRAM BOT WEBHOOK TEKSHIRUVI")
    print("=" * 60)
    
    try:
        # Bot token
        token = settings.TELEGRAM_BOT_TOKEN
        print(f"\n✅ Bot token: {token[:10]}...{token[-5:]}")
        
        # Bot instance
        bot = telebot.TeleBot(token)
        bot_info = bot.get_me()
        print(f"✅ Bot username: @{bot_info.username}")
        print(f"✅ Bot ID: {bot_info.id}")
        print(f"✅ Bot name: {bot_info.first_name}")
        
        # Webhook info
        print("\n" + "=" * 60)
        print("📊 WEBHOOK HOLATI:")
        print("=" * 60)
        
        webhook_info = bot.get_webhook_info()
        
        if webhook_info.url:
            print(f"✅ Webhook URL: {webhook_info.url}")
        else:
            print("⚠️  Webhook o'rnatilmagan!")
            print(f"   Expected URL: {settings.TELEGRAM_WEBHOOK_URL}")
        
        print(f"📨 Pending updates: {webhook_info.pending_update_count}")
        print(f"🔢 Max connections: {webhook_info.max_connections or 40}")
        
        if webhook_info.last_error_message:
            print(f"\n❌ OXIRGI XATO:")
            print(f"   {webhook_info.last_error_message}")
            if webhook_info.last_error_date:
                from datetime import datetime
                error_date = datetime.fromtimestamp(webhook_info.last_error_date)
                print(f"   Vaqt: {error_date.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("\n✅ Xatolar yo'q")
        
        # Webhook URL tekshiruvi
        print("\n" + "=" * 60)
        print("🌐 URL TEKSHIRUVI:")
        print("=" * 60)
        
        expected_url = settings.TELEGRAM_WEBHOOK_URL
        actual_url = webhook_info.url
        
        if actual_url == expected_url:
            print(f"✅ Webhook URL to'g'ri")
        else:
            print(f"⚠️  Webhook URL mos emas!")
            print(f"   Kutilgan: {expected_url}")
            print(f"   Hozirgi:  {actual_url}")
            print(f"\n💡 Webhook qayta o'rnatish:")
            print(f"   python manage.py start_webhook")
        
        # Tavsiyalar
        print("\n" + "=" * 60)
        print("💡 TAVSIYALAR:")
        print("=" * 60)
        
        if not webhook_info.url:
            print("1. Webhook o'rnatish:")
            print("   python manage.py start_webhook")
            print("\n2. Web server restart qiling (PythonAnywhere)")
        elif webhook_info.last_error_message:
            print("1. Error log'ni tekshiring")
            print("2. Django server restart qiling")
            print("3. Webhook qayta o'rnating:")
            print("   python manage.py start_webhook")
        elif webhook_info.pending_update_count > 0:
            print(f"1. {webhook_info.pending_update_count} ta xabar kutilmoqda")
            print("2. Bot'ga xabar yuboring - handler'lar ishga tushadi")
        else:
            print("✅ Hammasi yaxshi! Bot tayyor.")
            print("📱 Telegram'da bot'ga xabar yuboring va tekshiring.")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ XATOLIK: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_webhook()

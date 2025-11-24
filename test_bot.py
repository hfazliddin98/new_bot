#!/usr/bin/env python
"""
Telegram bot test (mahalliy polling rejimi)
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

from bot.telegram_bot import get_bot, setup_handlers

def test_bot():
    """Bot test qilish - polling rejimi"""
    print("=" * 60)
    print("🧪 TELEGRAM BOT TEST (Polling rejimi)")
    print("=" * 60)
    
    try:
        # Bot instance
        bot = get_bot()
        if not bot:
            print("❌ Bot yaratilmadi!")
            return
        
        print(f"✅ Bot tayyor: @{bot.get_me().username}\n")
        
        # Handler'larni o'rnatish
        print("🔧 Handler'lar o'rnatilmoqda...")
        result = setup_handlers()
        
        if result:
            print("✅ Handler'lar tayyor\n")
        else:
            print("❌ Handler'lar o'rnatilmadi\n")
            return
        
        # Polling boshlanishi
        print("=" * 60)
        print("🚀 BOT ISHGA TUSHDI (Polling)")
        print("=" * 60)
        print("📱 Telegram'da bot'ga xabar yuboring:")
        print("   - /start - Botni boshlash")
        print("   - 🍕 Menyu - Mahsulotlar ko'rish")
        print("   - 🛒 Savat - Savatni ko'rish")
        print("\n⏹️  To'xtatish uchun: Ctrl+C")
        print("=" * 60 + "\n")
        
        # Polling
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ XATOLIK: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_bot()

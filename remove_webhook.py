#!/usr/bin/env python
"""Webhook o'chirish"""
import telebot

TOKEN = '7908094134:AAHhj28h-QmV8hqEqOZAUnU9ebXBEwwKuA0'

print("🔄 Webhook o'chirilmoqda...")
bot = telebot.TeleBot(TOKEN)

result = bot.remove_webhook()

if result:
    print("✅ Webhook muvaffaqiyatli o'chirildi!")
    
    # Holat tekshirish
    info = bot.get_webhook_info()
    print(f"\n📊 Webhook holati:")
    print(f"  URL: {info.url or '(yo''q)'}")
    print(f"  Pending updates: {info.pending_update_count}")
    
    if not info.url:
        print("\n✅ Endi polling ishlatishingiz mumkin!")
        print("   python manage.py runserver")
else:
    print("❌ Webhook o'chirilmadi")

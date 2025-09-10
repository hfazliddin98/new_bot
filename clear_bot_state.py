#!/usr/bin/env python
"""
Bot webhook va pending updatelarni tozalash
"""
import requests
import time

BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def clear_bot_state():
    """Bot holatini tozalash"""
    try:
        print("🧹 Bot holatini tozalamoqda...")
        
        # 1. Webhook'ni o'chirish
        print("📡 Webhook'ni o'chirish...")
        response = requests.get(f"{BASE_URL}/deleteWebhook", timeout=30)
        if response.status_code == 200:
            print("✅ Webhook o'chirildi")
        else:
            print(f"⚠️ Webhook o'chirishda muammo: {response.text}")
        
        time.sleep(2)
        
        # 2. Pending updatelarni tozalash
        print("🔄 Pending updatelarni tozalash...")
        for i in range(3):
            response = requests.get(f"{BASE_URL}/getUpdates?offset=-1&timeout=1", timeout=30)
            if response.status_code == 200:
                print(f"✅ Update {i+1}/3 tozalandi")
            time.sleep(1)
        
        # 3. Bot ma'lumotlarini tekshirish
        print("🤖 Bot ma'lumotlarini tekshirish...")
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                print(f"✅ Bot aktiv: @{bot_info['result']['username']}")
            else:
                print("❌ Bot ma'lumotlarini olishda xatolik")
        else:
            print(f"❌ Bot API'ga ulanishda xatolik: {response.status_code}")
        
        print("🎉 Bot holati tozalandi!")
        return True
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

if __name__ == "__main__":
    clear_bot_state()

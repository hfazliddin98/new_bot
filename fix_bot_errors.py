#!/usr/bin/env python
"""
Bot xatoliklarini hal qilish va webhook tozalash
"""
import requests
import time

BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def clear_bot_issues():
    """Bot bilan bog'liq muammolarni hal qilish"""
    try:
        print("🧹 Bot xatoliklarini hal qilish...")
        
        # 1. Webhook o'chirish
        print("1️⃣ Webhook o'chirilmoqda...")
        webhook_response = requests.get(f"{BASE_URL}/deleteWebhook")
        print(f"   Webhook: {webhook_response.json()}")
        
        # 2. Pending updatelarni olish va tozalash
        print("2️⃣ Pending updatelar tozalanmoqda...")
        
        # Oldingi updatelarni olish
        updates_response = requests.get(f"{BASE_URL}/getUpdates?timeout=1&limit=100")
        if updates_response.status_code == 200:
            updates_data = updates_response.json()
            if updates_data.get('result'):
                last_update_id = max([update['update_id'] for update in updates_data['result']])
                
                # Barcha oldingi updatelarni confirm qilish
                confirm_response = requests.get(f"{BASE_URL}/getUpdates?offset={last_update_id + 1}&timeout=1")
                print(f"   Updates confirmed: {len(updates_data['result'])} ta")
            else:
                print("   Pending update topilmadi")
        
        # 3. Bot holatini tekshirish
        print("3️⃣ Bot holati tekshirilmoqda...")
        me_response = requests.get(f"{BASE_URL}/getMe")
        if me_response.status_code == 200:
            bot_info = me_response.json()
            if bot_info.get('ok'):
                print(f"   ✅ Bot active: @{bot_info['result']['username']}")
            else:
                print("   ❌ Bot inactive")
        
        # 4. Webhook holatini tekshirish 
        print("4️⃣ Webhook holati tekshirilmoqda...")
        webhook_info_response = requests.get(f"{BASE_URL}/getWebhookInfo")
        if webhook_info_response.status_code == 200:
            webhook_info = webhook_info_response.json()
            if webhook_info.get('result', {}).get('url'):
                print(f"   ⚠️ Webhook hali mavjud: {webhook_info['result']['url']}")
            else:
                print("   ✅ Webhook o'chirilgan")
        
        print("\n🎯 Bot tozalandi! Endi yangi bot ishga tushirishingiz mumkin.")
        return True
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return False

if __name__ == "__main__":
    clear_bot_issues()

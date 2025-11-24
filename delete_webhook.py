import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("🔧 Telegram Bot webhook'ini o'chirish...")
print(f"Token: {TOKEN[:20]}...")

try:
    # Webhook'ni o'chirish
    url = f'https://api.telegram.org/bot{TOKEN}/deleteWebhook'
    response = requests.get(url, timeout=10)
    result = response.json()
    
    print("\n✅ Natija:")
    print(f"  OK: {result.get('ok')}")
    print(f"  Description: {result.get('description', 'N/A')}")
    
    if result.get('ok'):
        print("\n✅ Webhook muvaffaqiyatli o'chirildi!")
        print("🚀 Endi botni ishga tushirishingiz mumkin.")
    else:
        print("\n❌ Xatolik yuz berdi!")
        
except Exception as e:
    print(f"\n❌ Xatolik: {e}")

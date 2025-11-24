# Telegram Bot Hosting Setup (PythonAnywhere)

## 1. Django proyektni yuklash

```bash
cd ~
git clone https://github.com/yourusername/new_bot.git
cd new_bot
```

## 2. Virtual environment yaratish

```bash
mkvirtualenv --python=/usr/bin/python3.10 myenv
workon myenv
pip install -r requirements.txt
```

## 3. Environment variables o'rnatish

`.env` fayl yaratish:
```bash
nano .env
```

Quyidagilarni yozing:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
TELEGRAM_BOT_TOKEN=7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q
TELEGRAM_WEBHOOK_URL=https://dastavka.pythonanywhere.com/bot/webhook/
```

## 4. Django sozlamalari

Database yaratish:
```bash
python manage.py migrate
python manage.py createsuperuser
```

Static fayllarni yig'ish:
```bash
python manage.py collectstatic --noinput
```

## 5. WSGI sozlamalari

PythonAnywhere Web tab'da:
- Source code: `/home/yourusername/new_bot`
- Working directory: `/home/yourusername/new_bot`
- Virtualenv: `/home/yourusername/.virtualenvs/myenv`

WSGI configuration file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

```python
import os
import sys

path = '/home/yourusername/new_bot'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'asosiy.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 6. Telegram Bot Webhook o'rnatish

### A. URLs tekshirish

`bot/urls.py` faylida webhook route borligini tekshiring:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    # ...
]
```

### B. Management command orqali webhook o'rnatish

PythonAnywhere Bash console'da:

```bash
cd ~/new_bot
workon myenv
python manage.py start_webhook
```

Yoki URL bilan:
```bash
python manage.py start_webhook --url https://dastavka.pythonanywhere.com/bot/webhook/
```

### C. Webhook holatini tekshirish

Python console'da:
```python
import telebot
bot = telebot.TeleBot('7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q')
info = bot.get_webhook_info()
print(f"URL: {info.url}")
print(f"Pending: {info.pending_update_count}")
print(f"Error: {info.last_error_message}")
```

## 7. Test qilish

1. Web app'ni restart qiling (PythonAnywhere Web tab)
2. Telegram bot'ga xabar yuboring
3. Logs tekshiring: `/var/log/yourusername.pythonanywhere.com.error.log`

## 8. Muammolarni hal qilish

### Bot javob bermasa:

**1. Webhook URL to'g'riligini tekshiring:**
```python
import requests
url = "https://api.telegram.org/bot7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q/getWebhookInfo"
response = requests.get(url)
print(response.json())
```

**2. Django webhook URL ochiq ekanligini tekshiring:**
```bash
curl https://dastavka.pythonanywhere.com/bot/webhook/
# "Method not allowed" qaytishi kerak (GET bo'lgani uchun)
```

**3. Eski webhook'ni o'chirish:**
```python
import telebot
bot = telebot.TeleBot('7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q')
bot.remove_webhook()
# 2-3 soniya kutish
bot.set_webhook('https://dastavka.pythonanywhere.com/bot/webhook/')
```

**4. Error log'ni ko'rish:**
```bash
tail -f /var/log/yourusername.pythonanywhere.com.error.log
```

### 409 Conflict Error:

Bu xato ikkita bot instance bir vaqtda ishlaganida chiqadi:
- Polling rejimidagi bot'ni to'xtating
- Webhook o'rnating
- Web app'ni restart qiling

```bash
# Bot process'larni topish va o'chirish
ps aux | grep python | grep bot
kill <process_id>
```

## 9. Xabar yuborish (Django'dan)

Courier yetkazib berganida xabar yuborish (tayyor):

```python
from bot.telegram_bot import get_bot
from bot.models import TelegramUser

# Order yetkazilganda
telegram_user = TelegramUser.objects.filter(
    phone_number=order.phone_number
).first()

if telegram_user and telegram_user.user_id:
    bot = get_bot()
    message = f"✅ Buyurtma #{order.id} yetkazildi!"
    bot.send_message(telegram_user.user_id, message)
```

## 10. Scheduled Tasks (agar kerak bo'lsa)

PythonAnywhere'da har kuni 00:00 da biror task ishlatish:

Tasks tab'da:
```bash
cd ~/new_bot && source ~/.virtualenvs/myenv/bin/activate && python manage.py your_command
```

---

## Tezkor Test

Hammasi to'g'ri ishlayotganini tekshirish:

```bash
# 1. Database
python manage.py showmigrations

# 2. Static files
ls -la /home/yourusername/new_bot/staticfiles/

# 3. Webhook
python manage.py start_webhook

# 4. Test xabar
# Telegram bot'ga "/start" yuboring
```

## Muhim eslatma

⚠️ **Polling va Webhook bir vaqtda ishlamaydi!**
- Local development: `python bot/telegram_bot.py` (polling)
- Hosting (PythonAnywhere): Webhook (yuqoridagi qo'llanma)

Polling'dan webhook'ga o'tish:
1. Bot process'ni to'xtating (polling)
2. `python manage.py start_webhook` ishga tushiring
3. Web app'ni restart qiling

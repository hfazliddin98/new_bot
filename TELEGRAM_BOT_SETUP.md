# Telegram Bot - Hostingda Ishga Tushirish

## 🚀 Tezkor Boshlash (PythonAnywhere)

### 1️⃣ Proyektni yuklash va sozlash

```bash
cd ~
git clone <your-repo-url> new_bot
cd new_bot
mkvirtualenv --python=/usr/bin/python3.10 botenv
pip install -r requirements.txt
```

### 2️⃣ .env fayl yaratish

```bash
nano .env
```

```env
SECRET_KEY=your-long-random-secret-key
DEBUG=False
TELEGRAM_BOT_TOKEN=7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q
TELEGRAM_WEBHOOK_URL=https://dastavka.pythonanywhere.com/bot/webhook/
```

### 3️⃣ Database va static

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py create_test_data  # Test data (ixtiyoriy)
```

### 4️⃣ Web App sozlamalari

PythonAnywhere > Web > Add new web app:

- **Source code:** `/home/yourusername/new_bot`
- **Working directory:** `/home/yourusername/new_bot`  
- **Virtualenv:** `/home/yourusername/.virtualenvs/botenv`

**WSGI file** (`/var/www/username_pythonanywhere_com_wsgi.py`):

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

**Reload** tugmasini bosing.

### 5️⃣ Webhook o'rnatish

```bash
cd ~/new_bot
workon botenv
python manage.py start_webhook
```

✅ Ko'rinishi:
```
🔄 Eski webhook o'chirilmoqda...
🔧 Webhook o'rnatilmoqda: https://dastavka.pythonanywhere.com/bot/webhook/
✅ Webhook muvaffaqiyatli o'rnatildi
📊 Webhook holati:
  - URL: https://dastavka.pythonanywhere.com/bot/webhook/
  - Pending updates: 0
```

### 6️⃣ Test

Telegram'da botga `/start` yuboring. Javob kelishi kerak!

---

## 🔧 Muammolarni Hal Qilish

### ❌ Bot javob bermayapti

**1. Webhook holatini tekshirish:**

```bash
cd ~/new_bot
workon botenv
python
```

```python
import telebot
bot = telebot.TeleBot('7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q')
info = bot.get_webhook_info()
print(f"Webhook URL: {info.url}")
print(f"Pending updates: {info.pending_update_count}")
print(f"Last error: {info.last_error_message}")
print(f"Last error date: {info.last_error_date}")
```

**2. URL ochiqligini tekshirish:**

```bash
curl -X POST https://dastavka.pythonanywhere.com/bot/webhook/
# "OK" yoki "Error" qaytishi kerak
```

**3. Loglarni ko'rish:**

```bash
tail -50 /var/log/yourusername.pythonanywhere.com.error.log
```

**4. Webhook qayta o'rnatish:**

```bash
python manage.py start_webhook --url https://dastavka.pythonanywhere.com/bot/webhook/
```

### ❌ 409 Conflict (Ikkita bot ishlayapti)

Bu xato polling rejimidagi bot hali ishlaganida chiqadi.

**Yechim:**

```bash
# Bot processlarni topish
ps aux | grep python | grep bot

# Process'ni to'xtatish
kill <process_id>

# Webhook'ni tozalash va qayta o'rnatish
python -c "import telebot; bot=telebot.TeleBot('7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q'); bot.remove_webhook()"

# 3 soniya kutish
sleep 3

# Qayta o'rnatish
python manage.py start_webhook
```

### ❌ Xabarlar kelmayapti

**Handler'lar tekshiruvi:**

`bot/views.py` da `telegram_webhook` funksiyasida `setup_handlers()` chaqirilganini tekshiring:

```python
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        # ...
        if not hasattr(telegram_webhook, 'handlers_set'):
            setup_handlers()  # ✅ Bu qator bo'lishi kerak
            telegram_webhook.handlers_set = True
        # ...
```

**Web app restart:**

PythonAnywhere > Web > **Reload** tugmasini bosing.

---

## 📋 URLs.py tekshiruvi

`bot/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'bot'

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('stats/', views.bot_stats, name='bot_stats'),
]
```

`asosiy/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/', include('bot.urls')),  # ✅ Bu qator bo'lishi kerak
    # ...
]
```

---

## 📊 Telegram xabar yuborish (Courier)

`courier/views.py` da order yetkazilganda avtomatik xabar yuboriladi:

```python
from bot.telegram_bot import get_bot
from bot.models import TelegramUser

# Order yetkazilganda
telegram_user = TelegramUser.objects.filter(
    phone_number=delivery.order.phone_number
).first()

if telegram_user and telegram_user.user_id:
    bot = get_bot()
    message = f"✅ Buyurtma #{delivery.order.id} yetkazildi!"
    bot.send_message(telegram_user.user_id, message)
```

Bu kod tayyor - faqat webhook ishlashi kerak!

---

## ⚙️ Settings.py tekshiruvi

```python
# asosiy/settings.py

DOMEN = 'dastavka.pythonanywhere.com'
ALLOWED_HOSTS = [DOMEN, 'localhost', '127.0.0.1', '.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = [f'https://{DOMEN}']

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7305057883:AAG...')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', f'https://{DOMEN}/bot/webhook/')
```

---

## 🎯 Xulosa

**Local development:**
```bash
python bot/telegram_bot.py  # Polling rejimi
```

**Hosting (PythonAnywhere):**
```bash
python manage.py start_webhook  # Webhook rejimi
```

⚠️ **Muhim:** Polling va Webhook bir vaqtda ishlamaydi! Hostingda faqat webhook ishlatiladi.

---

## ✅ Tekshirish bo'yicha Checklist

- [ ] `.env` fayl yaratilgan va to'ldirilgan
- [ ] `python manage.py migrate` ishlatilgan
- [ ] Web app sozlamalari to'g'ri (WSGI, virtualenv, paths)
- [ ] `python manage.py start_webhook` muvaffaqiyatli ishladi
- [ ] Web app reload qilindi
- [ ] Telegram bot'ga `/start` yuborildi va javob keldi
- [ ] Error log'da xatolik yo'q
- [ ] Webhook info'da `last_error_message` bo'sh

Barcha checklist ✅ bo'lsa - bot tayyor! 🎉

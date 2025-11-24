# Telegram Bot - Avtomatik Polling

## 🚀 Tezkor Boshlash

### 1. O'rnatish

```bash
pip install -r requirements.txt
```

### 2. Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_test_data  # Test data (ixtiyoriy)
```

### 3. Django serverni ishga tushirish

```bash
python manage.py runserver
```

**Bot avtomatik ishga tushadi!** ✅

```
🚀 Django server ishga tushdi (runserver)
✅ Telegram bot thread yaratildi va ishga tushdi!
📱 Bot @qdutaomttj_bot ga xabar yuborishingiz mumkin
🤖 Telegram bot polling rejimida ishga tushirilmoqda...
✅ Bot tayyor: @qdutaomttj_bot
🔧 Handler'lar o'rnatilmoqda...
✅ Barcha handler'lar muvaffaqiyatli o'rnatildi
🚀 Bot polling rejimida ishga tushmoqda...
```

### 4. Test

Telegram'da bot'ga xabar yuboring:
- `/start` - Botni boshlash
- `🍕 Menyu` - Mahsulotlarni ko'rish
- `🛒 Savat` - Savatni ko'rish
- `📋 Buyurtmalarim` - Buyurtmalar tarixi

---

## 📁 Proyekt Strukturasi

```
new_bot/
├── asosiy/          # Django settings
├── bot/             # Telegram bot app
│   ├── telegram_bot.py     # Bot handlers (polling)
│   ├── models.py           # TelegramUser, Order, Product
│   └── apps.py             # Avtomatik bot ishga tushirish
├── users/           # Custom User model
├── kitchen/         # Oshxona paneli
├── courier/         # Kuryer paneli
└── manage.py
```

---

## 🔧 Qanday Ishlaydi?

### Avtomatik Ishga Tushish

Django server ishga tushganda `bot/apps.py` avtomatik bot'ni ishga tushiradi:

```python
# bot/apps.py
class BotConfig(AppConfig):
    def ready(self):
        # Django server ishga tushganda
        self.start_telegram_bot()  # Bot avtomatik ishga tushadi
```

Bot alohida thread'da ishlaydi - Django server va bot bir vaqtda ishlaydi.

### Polling Rejimi

Bot Telegram'dan xabarlarni doimiy so'raydi (polling):

```
Bot → Telegram API (getUpdates) → Yangi xabarlar
    ↓
Handler'lar xabarni process qiladi
    ↓
Bot javob yuboradi
```

**Afzalliklari:**
- Oddiy sozlash
- Localhost'da ishlaydi
- Webhook kerak emas
- HTTPS talab qilinmaydi

---

## 🌐 Hostingda Ishlatish

### PythonAnywhere

```bash
# 1. Proyektni yuklash
cd ~
git clone <repo-url> new_bot
cd new_bot

# 2. Virtual environment
mkvirtualenv --python=/usr/bin/python3.10 botenv
pip install -r requirements.txt

# 3. Database
python manage.py migrate

# 4. WSGI sozlash
# Web tab > WSGI configuration file
```

WSGI file:
```python
import os
import sys

path = '/home/username/new_bot'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'asosiy.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Web app restart qiling** - bot avtomatik ishga tushadi!

### Heroku

`Procfile`:
```
web: gunicorn asosiy.wsgi:application
```

Deploy:
```bash
git push heroku main
```

Bot avtomatik ishga tushadi!

### VPS (Ubuntu/DigitalOcean)

Supervisor bilan:

```ini
[program:django]
command=/path/to/venv/bin/gunicorn asosiy.wsgi:application
directory=/path/to/new_bot
autostart=true
autorestart=true
```

Nginx + Gunicorn:
```bash
gunicorn asosiy.wsgi:application --bind 0.0.0.0:8000 --daemon
```

Bot avtomatik ishga tushadi!

---

## 🐛 Muammolarni Hal Qilish

### ❌ Bot ishlamayapti

**1. Console'ni tekshiring:**

Bot ishga tushganda quyidagi xabarlar ko'rinishi kerak:
```
🚀 Django server ishga tushdi
✅ Telegram bot thread yaratildi
🤖 Bot polling rejimida ishga tushmoqda...
```

**2. Bot token to'g'riligini tekshiring:**

```python
# Django shell
python manage.py shell
from django.conf import settings
print(settings.TELEGRAM_BOT_TOKEN)
```

**3. Thread ishlayotganini tekshirish:**

```python
from bot.apps import BotConfig
if BotConfig.bot_thread:
    print(f"Thread alive: {BotConfig.bot_thread.is_alive()}")
```

### ❌ 409 Conflict Error

Webhook hali faol. O'chirish:

```bash
python remove_webhook.py
```

Yoki:
```python
import telebot
bot = telebot.TeleBot('YOUR_TOKEN')
bot.remove_webhook()
```

### ❌ Bot to'xtadi

Django serverni qayta ishga tushiring:
```bash
# Ctrl+C yoki Ctrl+Break
python manage.py runserver
```

---

## 📊 Admin Panel

Django admin: `http://127.0.0.1:8000/admin/`

**Admin paneli:**
- `/admin-panel/` - Bosh sahifa
- `/kitchen/` - Oshxona paneli
- `/courier/` - Kuryer paneli

**User roles:**
- `admin` - Barcha panellar
- `kitchen` - Oshxona paneli
- `courier` - Kuryer paneli

---

## 📝 Environment Variables

`.env` fayl yarating:

```env
SECRET_KEY=your-secret-key
DEBUG=True
TELEGRAM_BOT_TOKEN=7908094134:AAHhj28h-QmV8hqEqOZAUnU9ebXBEwwKuA0
```

**Hostingda:**
```env
DEBUG=False
SECRET_KEY=production-secret-key
```

---

## 🎯 Xulosa

✅ **Oddiy:** Django server bilan birga avtomatik ishga tushadi  
✅ **Tez:** Webhook sozlash kerak emas  
✅ **Universal:** Localhost va hosting'da ishlaydi  
✅ **Ishonchli:** Thread crash bo'lsa Django qayta yuklaydi  

**Faqat Django serverni ishga tushiring - bot avtomatik ishlaydi!** 🚀

# Telegram Bot - Avtomatik Polling

## 🚀 Bot avtomatik ishlaydi!

Django server ishga tushganda Telegram bot **avtomatik** polling rejimida ishlaydi.

## Ishlatish

### Mahalliy (Development)

```bash
# Django server ishga tushiring
python manage.py runserver

# Bot avtomatik ishga tushadi! ✅
```

Console chiqishi:
```
🚀 Django server ishga tushdi (runserver)
🤖 Bot instance yaratilmoqda...
✅ Bot tayyor: @qdutaomttj_bot
🔧 Handler'lar o'rnatilmoqda...
✅ Barcha handler'lar muvaffaqiyatli o'rnatildi
✅ Telegram bot thread yaratildi va ishga tushdi!
📱 Bot @qdutaomttj_bot ga xabar yuborishingiz mumkin
🚀 Bot polling rejimida ishga tushmoqda...
```

### Hostingda (PythonAnywhere, Heroku, VPS)

**Variant 1: Webhook (tavsiya etiladi)**

`.env` faylda:
```env
TELEGRAM_USE_POLLING=false
```

Web server ishga tushganda:
```
🌐 Bot webhook rejimida (polling o'chiq)
💡 Webhook o'rnatish: python manage.py start_webhook
```

Webhook o'rnatish:
```bash
python manage.py start_webhook
```

**Variant 2: Avtomatik Polling (oddiy, lekin webhook yaxshiroq)**

`.env` faylda:
```env
TELEGRAM_USE_POLLING=true
```

Web server restart qilganda bot avtomatik ishga tushadi:
```
🚀 Django server ishga tushdi (production)
✅ Telegram bot thread yaratildi va ishga tushdi!
```

## Environment Variables

### TELEGRAM_USE_POLLING

Bot rejimini boshqaradi:

| Qiymat | Rejim | Qachon ishlatiladi |
|--------|-------|-------------------|
| `true` | Polling | Mahalliy development, ba'zi hostinglar |
| `false` | Webhook | Production, PythonAnywhere, Heroku |

**Default:** `true`

### Qaysi rejimni tanlash?

| Hosting | Tavsiya | Sabab |
|---------|---------|-------|
| Localhost | Polling ✅ | Webhook localhost bilan ishlamaydi |
| PythonAnywhere | Webhook ✅ | Polling cheklangan, webhook tez |
| Heroku | Webhook ✅ | Dyno uxlashi, webhook yaxshi |
| VPS/DigitalOcean | Polling ✅ | To'liq nazorat, polling oson |
| Vercel/Netlify | Webhook ✅ | Serverless, faqat webhook |

## Qanday ishlaydi?

### Polling rejimi

```python
# bot/apps.py
class BotConfig(AppConfig):
    def ready(self):
        # Django server ishga tushganda
        if use_polling:
            self.start_telegram_bot()  # Bot avtomatik ishga tushadi
```

```
Django Server → AppConfig.ready() → start_telegram_bot()
                                   → Thread yaratiladi
                                   → bot.infinity_polling()
```

### Webhook rejimi

```
Telegram → Webhook URL → Django view → Handler
```

## Test qilish

### 1. Polling test

```bash
# .env
TELEGRAM_USE_POLLING=true

# Server ishga tushirish
python manage.py runserver

# Telegram'da bot'ga xabar yuboring
# /start, 🍕 Menyu, 🛒 Savat
```

### 2. Webhook test

```bash
# .env
TELEGRAM_USE_POLLING=false

# Server ishga tushirish
python manage.py runserver

# Webhook o'rnatish
python manage.py start_webhook --url http://localhost:8000/bot/webhook/

# Agar ngrok ishlatilsa:
ngrok http 8000
python manage.py start_webhook --url https://abc123.ngrok.io/bot/webhook/
```

## Muammolarni hal qilish

### ❌ Bot ishga tushmadi

**1. Log tekshiring:**

Console'da quyidagi xabarlar ko'rinishi kerak:
```
🚀 Django server ishga tushdi
✅ Telegram bot thread yaratildi
```

Agar ko'rinmasa:
- `.env` faylda `TELEGRAM_USE_POLLING=true` borligini tekshiring
- `TELEGRAM_BOT_TOKEN` to'g'riligini tekshiring

**2. Thread ishlayotganini tekshirish:**

```python
# Django shell
python manage.py shell

from bot.apps import BotConfig
if BotConfig.bot_thread:
    print(f"Thread alive: {BotConfig.bot_thread.is_alive()}")
else:
    print("Thread yaratilmagan")
```

**3. Manual ishga tushirish:**

Agar avtomatik ishlamasa:
```bash
python bot/telegram_bot.py
```

### ❌ 409 Conflict

Bir vaqtda ikkita bot instance ishlamoqda.

```bash
# Barcha bot processlarni to'xtatish
# Windows
tasklist | findstr python
taskkill /PID <PID> /F

# Linux/Mac
ps aux | grep python | grep bot
kill <PID>

# Webhook tozalash
python -c "import telebot; bot=telebot.TeleBot('YOUR_TOKEN'); bot.remove_webhook()"

# Django server qayta ishga tushiring
```

### ❌ Bot thread to'xtadi

Agar thread crash bo'lsa, Django serverni qayta ishga tushiring:

```bash
# Ctrl+C
# python manage.py runserver
```

### ℹ️ Bot allaqachon ishlab turibdi

Bu xabar ko'rinsa - yaxshi! Bot allaqachon ishlamoqda, qayta ishga tushirilmaydi.

## Production bo'yicha tavsiyalar

### PythonAnywhere

Webhook'ni ishlatish tavsiya etiladi:

```env
TELEGRAM_USE_POLLING=false
```

```bash
python manage.py start_webhook
```

Lekin polling ham ishlaydi:

```env
TELEGRAM_USE_POLLING=true
```

Web app restart qilganda bot avtomatik ishga tushadi.

### Heroku

Webhook majburiy (dyno uxlashi):

```env
TELEGRAM_USE_POLLING=false
```

Procfile:
```
web: gunicorn asosiy.wsgi
```

Release command:
```bash
python manage.py start_webhook
```

### VPS/DigitalOcean

Polling yoki webhook - ikkalasi ham ishlaydi.

**Supervisor bilan (tavsiya etiladi):**

```ini
[program:django]
command=/path/to/venv/bin/gunicorn asosiy.wsgi:application
directory=/path/to/new_bot
environment=TELEGRAM_USE_POLLING="true"

[program:telegram-bot]
command=/path/to/venv/bin/python bot/telegram_bot.py
directory=/path/to/new_bot
```

Yoki faqat Django server bilan:
```env
TELEGRAM_USE_POLLING=true
```

## Xulosa

✅ **Mahalliy development:** Polling avtomatik (`TELEGRAM_USE_POLLING=true`)  
✅ **Hosting:** Webhook tavsiya etiladi (`TELEGRAM_USE_POLLING=false`)  
✅ **VPS:** Polling ham yaxshi ishlaydi  
✅ **Avtomatik:** Django server bilan birga ishga tushadi  

Webhook ishlamasa, `.env` da `TELEGRAM_USE_POLLING=true` qiling va Django serverni qayta ishga tushiring. Bot avtomatik ishlaydi! 🎉

# PythonAnywhere'da Bot Ishga Tushirish

## 1. Fayllarni Yuklash
- Barcha loyiha fayllarini PythonAnywhere'ga yuklang
- Git orqali: `git clone https://github.com/hfazliddin98/new_bot.git`

## 2. Virtual Environment Yaratish
```bash
cd new_bot
python3.10 -m venv venv
source venv/bin/activate
```

## 3. Paketlarni O'rnatish
```bash
pip install -r requirements.txt
```

## 4. Environment Variables Sozlash
```bash
cp .env.example .env
# .env faylini tahrirlang va o'z qiymatlaringizni kiriting
```

## 5. Database Migratsiya
```bash
python manage.py migrate
python manage.py createsuperuser
```

## 6. Static Fayllar
```bash
python manage.py collectstatic
```

## 7. Web App Sozlash
- PythonAnywhere Dashboard'da Web app yarating
- WSGI file: `/home/yourusername/new_bot/asosiy/wsgi.py`
- Static files: `/static/` -> `/home/yourusername/new_bot/static/`

## 8. Bot Ishga Tushirish

### Variant 1: Django Management Command (Tavsiya etiladi)
```bash
cd /home/yourusername/new_bot
source venv/bin/activate
python manage.py start_telegram_bot
```

### Variant 2: Always-On Tasks (Haqiqiy account)
- Always-On Tasks bo'limida yangi task yarating
- Command: `/home/yourusername/new_bot/venv/bin/python /home/yourusername/new_bot/manage.py start_telegram_bot`

### Variant 3: Tasks (Bepul account)
- Tasks bo'limida yangi task yarating
- Command: `/home/yourusername/new_bot/venv/bin/python /home/yourusername/new_bot/start_bot.py`
- Har 1 soatda takrorlanishini sozlang

### Variant 4: Console orqali test qilish
```bash
python manage.py start_telegram_bot
```

## 9. Logs Tekshirish
```bash
# Django logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Bot logs (agar kerak bo'lsa)
tail -f /home/yourusername/new_bot/bot.log
```

## Muhim Eslatmalar
1. Environment variables'larni to'g'ri sozlang
2. Bot tokenini xavfsiz saqlang
3. DEBUG=False production uchun
4. ALLOWED_HOSTS'ga domain qo'shing
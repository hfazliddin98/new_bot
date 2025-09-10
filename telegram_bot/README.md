# 🤖 Telegram Bot Files

Bu papka loyihadagi Telegram bot bilan bog'liq barcha fayllarni o'z ichiga oladi.

## 📂 Fayllar:

### 1. `main_bot.py`
- Asosiy telegram bot fayli
- Bot classlarini va asosiy funksiyalarni o'z ichiga oladi
- Django models bilan integratsiya

### 2. `handlers.py`
- Bot message handlerlarini o'z ichiga oladi
- Foydalanuvchi xabarlarini qayta ishlash
- Callback query handlarlari

### 3. `django_bot.py`
- Django management command sifatida bot
- `python manage.py runbot` buyrug'i uchun
- To'liq registratsiya tizimi bilan

## 🚀 Botni ishga tushirish:

### Django orqali (tavsiya etiladi):
```bash
python manage.py runbot
```

### To'g'ridan-to'g'ri (development):
```bash
python telegram_bot/main_bot.py
```

## 🔑 Environment o'zgaruvchilari:

`.env` faylida quyidagi o'zgaruvchilarni belgilang:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
SECRET_KEY=your_django_secret_key
```

## 📱 Bot funksiyalari:

1. **Registratsiya tizimi**
   - To'liq ism, yosh, telefon
   - Yotoqxona va xona ma'lumotlari
   - Avtomatik validatsiya

2. **Menyu tizimi**
   - Kategoriyalar bo'yicha mahsulotlar
   - Savatcha boshqaruvi
   - Buyurtma berish

3. **Profil boshqaruvi**
   - Foydalanuvchi ma'lumotlarini ko'rish
   - Ma'lumotlarni yangilash

4. **Yetkazib berish**
   - Ish soatlari nazorati
   - Zona bo'yicha yetkazib berish
   - Real-time status tracking

## 🔧 Konfiguratsiya:

Bot tokeni va boshqa sozlamalar `asosiy/settings.py` da:
```python
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
```

## 📊 Admin Panel:

Django admin panel orqali bot ma'lumotlarini boshqarishingiz mumkin:
- http://127.0.0.1:8000/admin/
- Foydalanuvchilar
- Buyurtmalar
- Mahsulotlar
- Yetkazib berish zonalari

## 🐛 Debug:

Bot loglarini `bot.log` faylida ko'rishingiz mumkin.

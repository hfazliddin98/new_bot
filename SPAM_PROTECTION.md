# 🛡️ Telegram Bot Spam Himoyasi

## Muammo
Telegram botga spam xabarlar (masalan, "Hot_Girl", "Direct Link", "MEGA" kabi noxush kanallar) kelmoqda.

## Yechim

### 1. **Shaxsiy Chat Himoyasi**
Bot faqat shaxsiy (private) chatda ishlaydi:
- Guruh/kanallarda ishlamaydi
- Bot guruhga qo'shilsa, avtomatik chiqib ketadi

### 2. **Spam Filtr**
Quyidagi spam pattern'larni aniqlaydi:
- Spam kalit so'zlar: `mega`, `direct link`, `stream`, `porn`, va boshqalar
- Ko'p emoji (10+ ta)
- Ko'p linklar (t.me/, http://, https://)
- Juda uzun xabarlar (1000+ belgi)

### 3. **Avtomatik Bloklash**
Spam xabar yuborganlar avtomatik bloklanadi.

## Ishlatish

### Spam foydalanuvchilarni topish
```bash
python manage.py manage_spam --find-spam
```

### Foydalanuvchini bloklash
```bash
python manage.py manage_spam --block <user_id>
```

### Foydalanuvchini blokdan chiqarish
```bash
python manage.py manage_spam --unblock <user_id>
```

### Bloklangan foydalanuvchilar ro'yxati
```bash
python manage.py manage_spam --list-blocked
```

## Himoya Mexanizmlari

### 1. Chat Type Check
```python
if message.chat.type != 'private':
    return  # Guruh/kanallarda ishlamaydi
```

### 2. Spam Detection
```python
from telegram_bot.spam_protection import validate_message

is_valid, error_msg = validate_message(message)
if not is_valid:
    return  # Spam xabar rad etiladi
```

### 3. Auto-leave Groups
```python
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_chat_members(message):
    bot.leave_chat(message.chat.id)
```

## Loglar

Spam faoliyati logga yoziladi:
```
⚠️ SPAM BLOKLANDI: user_id=123456, username=@spammer, text=...
```

## Qo'shimcha Himoya

### BotFather orqali
1. `/mybots` - o'z botingizni tanlang
2. `Bot Settings` → `Group Privacy` → `Disable`
3. Bu bot guruhga qo'shilishini butunlay to'xtatadi

### Environment sozlamalari
`.env` faylida:
```env
TELEGRAM_BOT_TOKEN=your_token_here
SPAM_PROTECTION=true
AUTO_BLOCK_SPAM=true
```

## Xavfsizlik Tavsiyalar

1. **Bot tokenini maxfiy saqlang** - hech qachon GitHub'ga commit qilmang
2. **Webhook ishlatilsa** - HTTPS dan foydalaning
3. **User input** - har doim validatsiya qiling
4. **Rate limiting** - ko'p so'rov yuboruvchilarni cheklang
5. **Admin panel** - faqat ishonchli IP'lardan kirish

## Muammo hal bo'lmasa

Agar hali ham spam kelsa:

1. **Database'ni tozalang:**
```bash
python manage.py manage_spam --find-spam
python manage.py manage_spam --block <spam_user_id>
```

2. **Bot tokenini yangilang:**
   - BotFather'da `/revoke` buyrug'ini ishlatish
   - `.env` fayldagi tokenni yangilash

3. **Bot ni qayta ishga tushuring:**
```bash
python telegram_bot/main_bot.py
```

## Kontakt

Qo'shimcha yordam kerak bo'lsa, admin bilan bog'laning.

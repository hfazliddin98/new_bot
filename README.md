# 🚚 Yotoqxonalar uchun Yetkazib berish Xizmati

Qo'qon Davlat Universiteti TTTJSI uchun Telegram bot va Web panel bilan yetkazib berish xizmati.

## 🎯 Loyiha tavsifi

Bu loyiha yotoqxonalar uchun to'liq yetkazib berish tizimi bo'lib, quyidagi komponentlardan iborat:
- 🤖 **Telegram Bot** - Mijozlar uchun buyurtma berish
- 👨‍🍳 **Kitchen Panel** - Oshxona xodimlari uchun boshqaruv paneli  
- 🚛 **Courier Panel** - Kuryer xodimlari uchun panel
- 📊 **Admin Panel** - To'liq tizim boshqaruvi

## 🚀 Tez ishga tushirish

### 1. Repository'ni klonlash
```bash
git clone https://github.com/hfazliddin98/new_bot.git
cd new_bot
```

### 2. Virtual environment yaratish
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# yoki
source .venv/bin/activate  # Linux/Mac
```

### 3. Paketlarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Environment sozlash
`.env` fayl yarating va quyidagilarni kiriting:
```env
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DEBUG=True
```

### 5. Database sozlash
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Test ma'lumotlar yaratish (ixtiyoriy)
```bash
python create_products.py
python create_dormitories.py
python create_staff.py
```

### 7. Loyihani ishga tushirish
```bash
# Django server va Telegram bot bir vaqtda ishga tushadi
python manage.py runserver
```

Bot avtomatik ishga tushadi va http://127.0.0.1:8000/ da ishlaydi.

## 📂 Loyiha strukturasi

```
new_bot/
├── asosiy/                  # Django asosiy sozlamalari
│   ├── settings.py          # Loyiha sozlamalari
│   ├── urls.py              # Asosiy URL routing
│   └── wsgi.py              # WSGI konfiguratsiya
├── bot/                     # Telegram bot app
│   ├── models.py            # TelegramUser, Product, Order, Cart
│   ├── views.py             # Bot API views
│   ├── admin.py             # Django admin
│   ├── management/
│   │   └── commands/
│   │       └── manage_spam.py  # Spam boshqaruv
│   └── migrations/
├── kitchen/                 # Oshxona app
│   ├── models.py            # KitchenStaff, OrderProgress
│   ├── views.py             # Kitchen dashboard
│   └── urls.py
├── courier/                 # Kuryer app
│   ├── models.py            # CourierStaff, Delivery
│   ├── views.py             # Courier dashboard
│   └── urls.py
├── users/                   # Custom User model
│   ├── models.py            # User (role-based)
│   ├── views.py             # Admin panel views
│   ├── forms.py             # Staff forms
│   ├── decorators.py        # @admin_required, @kitchen_required
│   └── middleware.py        # Role-based access
├── telegram_bot/            # Bot fayllar
│   ├── main_bot.py          # Asosiy bot mantiq
│   ├── spam_protection.py   # Spam himoyasi
│   ├── handlers.py          # Xabar handlerlari
│   └── django_bot.py        # Management command
├── templates/               # HTML shablonlar
│   ├── admin_panel/
│   ├── kitchen/
│   ├── courier/
│   └── base.html
├── static/                  # CSS, JS, rasm
├── media/                   # Yuklangan fayllar
├── create_products.py       # Mahsulotlar yaratish
├── create_dormitories.py    # Yotoqxonalar yaratish
├── create_staff.py          # Xodimlar yaratish
├── test_spam_protection.py  # Spam test
├── manage.py                # Django management
├── requirements.txt         # Python paketlar
├── .env.example             # Environment misol
├── README.md                # Ushbu fayl
├── SPAM_PROTECTION.md       # Spam himoyasi qo'llanma
└── SPAM_FIX_SUMMARY.md      # Spam fix xulosa
```

## 🔗 Asosiy URL'lar

- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Kitchen Dashboard**: http://127.0.0.1:8000/kitchen/
- **Courier Dashboard**: http://127.0.0.1:8000/courier/
- **Telegram Bot**: @ttjqdu_bot

## 🤖 Telegram Bot

Bot `telegram_bot/` papkasida joylashgan:
- `main_bot.py` - Asosiy bot fayli (spam himoyasi bilan)
- `spam_protection.py` - Spam filtr tizimi
- `handlers.py` - Message handlerlar
- `django_bot.py` - Django management command

### Bot funksiyalari:
- ✅ Foydalanuvchi registratsiyasi
- 🍽️ Menyu ko'rish va buyurtma berish
- 🛒 Savatcha boshqaruvi
- 📱 Profil boshqaruvi
- ⏰ Ish soatlari nazorati
- 🏠 Yotoqxona tanlov

## 👨‍🍳 Kitchen Panel

Oshxona xodimlari uchun panel (`/kitchen/`):
- 📊 Real-time dashboard
- 🆕 Yangi buyurtmalar
- 🔥 Tayyorlanayotgan buyurtmalar
- ✅ Tayyor buyurtmalar
- 📦 Mahsulot va kategoriya boshqaruvi
- 📺 Jonli monitor

## 🚛 Courier Panel

Kuryer xodimlari uchun panel (`/courier/`):
- 🚚 Yetkazish uchun buyurtmalar
- 📍 Marshrut optimizatsiyasi
- ✅ Yetkazilgan buyurtmalar
- 📊 Statistika

## ⚙️ Admin Panel

To'liq tizim boshqaruvi (`/admin/`):
- 👥 Foydalanuvchilar
- 🛒 Buyurtmalar
- 🍕 Mahsulotlar va kategoriyalar
- 🏠 Yotoqxonalar va zonalar
- 👨‍🍳 Kitchen staff
- 🚛 Courier staff

## 🛠️ Development

### Yangi feature qo'shish
1. Fork qiling
2. Feature branch yarating
3. O'zgarishlarni commit qiling
4. Pull request yuboring

### Testing
```bash
python manage.py test
```

### Migration yaratish
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- PyTelegramBotAPI
- SQLite (development) / PostgreSQL (production)

## 🔐 Xavfsizlik

- Environment variables dan foydalaning
- DEBUG=False production'da
- SECRET_KEY ni xavfsiz saqlang
- HTTPS ishlating production'da

## 📞 Aloqa

- **Developer**: @hfazliddin98
- **Email**: hfazliddin98@gmail.com
- **Telegram**: @ttjqdu_bot

## 📄 License

MIT License

---

⭐ Agar loyiha foydali bo'lsa, star bosishni unutmang!

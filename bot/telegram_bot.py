#!/usr/bin/env python
"""
Django App ichida ishlaydigan Telegram bot
"""
import os
import sys
import django
import time
import logging
import requests
from pathlib import Path

# Django sozlamalarini yuklash (agar kerak bo'lsa)
try:
    from django.conf import settings
    if not settings.configured:
        BASE_DIR = Path(__file__).resolve().parent.parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
        django.setup()
except:
    pass

import telebot
from telebot import types
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, DeliveryZone, Dormitory
from decimal import Decimal

# Logging sozlash
logger = logging.getLogger(__name__)

# Bot tokenini environment variable'dan olish yoki to'g'ridan-to'g'ri
BOT_TOKEN = os.getenv('BOT_TOKEN', "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q")

def create_bot_instance():
    """Xatoliksiz bot instance yaratish"""
    try:
        print("🔧 Bot instance yaratilmoqda...")
        
        # Oldingi webhook va updatelarni tozalash
        base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        
        print("📡 Webhook'ni o'chirish...")
        try:
            requests.get(f"{base_url}/deleteWebhook", timeout=30)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Webhook o'chirishda xatolik: {e}")
        
        print("🔄 Pending updatelarni tozalash...")
        try:
            for i in range(3):
                requests.get(f"{base_url}/getUpdates?offset=-1&timeout=1", timeout=10)
                time.sleep(1)
        except Exception as e:
            print(f"⚠️ Update tozalashda xatolik: {e}")
        
        time.sleep(3)
        
        # Bot yaratish
        print("🤖 Bot yaratilmoqda...")
        bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
        
        # Bot ma'lumotlarini tekshirish
        try:
            bot_info = bot.get_me()
            print(f"✅ Bot tayyor: @{bot_info.username}")
            logger.info(f"✅ Bot instance yaratildi: @{bot_info.username}")
            return bot
        except Exception as e:
            print(f"❌ Bot ma'lumotlarini olishda xatolik: {e}")
            return None
        
    except Exception as e:
        logger.error(f"Bot yaratishda xatolik: {e}")
        print(f"❌ Bot yaratishda xatolik: {e}")
        return None

# Global bot instance
bot_instance = None

def get_bot():
    """Bot instance'ni olish yoki yaratish"""
    global bot_instance
    if bot_instance is None:
        bot_instance = create_bot_instance()
    return bot_instance

def send_safe_message(chat_id, text, reply_markup=None, parse_mode=None):
    """Xatoliksiz xabar yuborish"""
    try:
        bot = get_bot()
        if bot:
            return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        return None

def edit_safe_message(chat_id, message_id, text, reply_markup=None):
    """Xatoliksiz xabar tahrirlash"""
    try:
        bot = get_bot()
        if bot:
            return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Xabar tahrirlashda xatolik: {e}")
        return None

def get_main_menu_keyboard():
    """Asosiy menyu klaviaturasi"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🍕 Menyu"),
        types.KeyboardButton("🛒 Savat")
    )
    markup.add(
        types.KeyboardButton("📋 Buyurtmalarim"),
        types.KeyboardButton("ℹ️ Ma'lumot")
    )
    return markup

def start_registration(chat_id, user):
    """Ro'yxatdan o'tkazishni boshlash"""
    welcome_text = f"🎉 Assalomu alaykum {user.first_name or 'Foydalanuvchi'}!\n\n"
    welcome_text += "🍕 Bizning yetkazib berish xizmatiga xush kelibsiz!\n\n"
    welcome_text += "📝 Ro'yxatdan o'tish uchun ma'lumotlaringizni kiriting:\n\n"
    welcome_text += "📱 Avval telefon raqamingizni yuboring:"
    
    # Telefon raqamini so'rash uchun klaviatura
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(contact_btn)
    
    send_safe_message(chat_id, welcome_text, markup)

def show_main_menu(chat_id, user):
    """Asosiy menyuni ko'rsatish"""
    text = f"👋 Salom {user.get_display_name()}!\n\n"
    text += "🍕 Nima qilmoqchisiz?"
    
    send_safe_message(chat_id, text, get_main_menu_keyboard())

def ask_full_name(chat_id, user):
    """To'liq ismni so'rash"""
    text = "✅ Telefon raqam qabul qilindi!\n\n"
    text += "👤 Endi to'liq ismingizni kiriting (Familiya Ism):"
    
    markup = types.ReplyKeyboardRemove()
    send_safe_message(chat_id, text, markup)

def ask_dormitory(chat_id, user):
    """Yotoqxonani tanlashni so'rash"""
    text = "✅ Ism qabul qilindi!\n\n"
    text += "🏠 Yotoqxonangizni tanlang:"
    
    # Yotoqxonalarni ko'rsatish
    dormitories = Dormitory.objects.filter(is_active=True)
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for dorm in dormitories:
        markup.add(types.InlineKeyboardButton(
            f"🏠 {dorm.name}",
            callback_data=f"dorm_{dorm.id}"
        ))
    
    send_safe_message(chat_id, text, markup)

def ask_room_number(chat_id, user):
    """Xona raqamini so'rash"""
    text = "✅ Yotoqxona tanlandi!\n\n"
    text += "🚪 Xona raqamingizni kiriting:"
    
    send_safe_message(chat_id, text)

def complete_registration(chat_id, user):
    """Ro'yxatdan o'tishni tugatish"""
    text = "🎉 Tabriklaymiz! Ro'yxatdan o'tish muvaffaqiyatli tugallandi!\n\n"
    text += f"👤 Ism: {user.full_name}\n"
    text += f"📱 Telefon: {user.phone_number}\n"
    text += f"🏠 Yotoqxona: {user.dormitory.name if user.dormitory else 'Tanlanmagan'}\n"
    text += f"🚪 Xona: {user.room_number}\n\n"
    text += "🍕 Endi buyurtma berishingiz mumkin!"
    
    send_safe_message(chat_id, text, get_main_menu_keyboard())

def show_menu_categories(chat_id, user):
    """Kategoriyalarni ko'rsatish"""
    categories = Category.objects.filter(is_active=True)
    
    if not categories.exists():
        send_safe_message(chat_id, "❌ Hozircha kategoriyalar mavjud emas.", get_main_menu_keyboard())
        return
    
    text = "🍕 Kategoriyalarni tanlang:"
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for category in categories:
        # Kategoriyada nechta mahsulot borligini hisoblash
        product_count = Product.objects.filter(category=category, is_available=True).count()
        
        if product_count > 0:
            markup.add(types.InlineKeyboardButton(
                f"{category.name} ({product_count})",
                callback_data=f"cat_{category.id}"
            ))
    
    # Orqaga qaytish tugmasi
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main"))
    
    send_safe_message(chat_id, text, markup)

def show_category_products(chat_id, user, category_id):
    """Kategoriya mahsulotlarini ko'rsatish"""
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            text = f"❌ {category.name} kategoriyasida hozircha mahsulotlar mavjud emas."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kategoriyalarga qaytish", callback_data="back_to_categories"))
            send_safe_message(chat_id, text, markup)
            return
        
        text = f"🍕 {category.name} kategoriyasi:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for product in products:
            product_text = f"{product.name}\n💰 {product.price:,} so'm"
            if product.description:
                product_text += f"\n📝 {product.description[:50]}..."
            
            markup.add(types.InlineKeyboardButton(
                f"🛒 {product.name} - {product.price:,} so'm",
                callback_data=f"prod_{product.id}"
            ))
        
        # Navigatsiya tugmalari
        markup.add(
            types.InlineKeyboardButton("🔙 Kategoriyalarga qaytish", callback_data="back_to_categories"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Category.DoesNotExist:
        send_safe_message(chat_id, "❌ Kategoriya topilmadi.", get_main_menu_keyboard())

def show_product_details(chat_id, user, product_id):
    """Mahsulot tafsilotlarini ko'rsatish"""
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        
        text = f"🍕 {product.name}\n\n"
        text += f"📝 {product.description}\n\n"
        text += f"💰 Narx: {product.price:,} so'm\n"
        text += f"📂 Kategoriya: {product.category.name}"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Savatga qo'shish tugmasi
        markup.add(types.InlineKeyboardButton(
            "🛒 Savatga qo'shish",
            callback_data=f"add_to_cart_{product.id}"
        ))
        
        # Navigatsiya
        markup.add(
            types.InlineKeyboardButton("🔙 Orqaga", callback_data=f"cat_{product.category.id}"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Product.DoesNotExist:
        send_safe_message(chat_id, "❌ Mahsulot topilmadi.", get_main_menu_keyboard())

def add_to_cart(chat_id, user, product_id):
    """Mahsulotni savatga qo'shish"""
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        
        # Savatda allaqachon bor yoki yo'qligini tekshirish
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            # Agar allaqachon savatda bo'lsa, miqdorni oshirish
            cart_item.quantity += 1
            cart_item.save()
            text = f"✅ {product.name} savatga qo'shildi!\n"
            text += f"📦 Savatingizdagi miqdor: {cart_item.quantity} ta"
        else:
            text = f"✅ {product.name} savatga qo'shildi!"
        
        # Savatdagi umumiy mahsulotlar sonini ko'rsatish
        total_items = Cart.objects.filter(user=user).count()
        text += f"\n\n🛒 Savatingizda jami: {total_items} xil mahsulot"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Yana qo'shish", callback_data=f"add_to_cart_{product.id}"),
            types.InlineKeyboardButton("🛒 Savatni ko'rish", callback_data="view_cart")
        )
        markup.add(
            types.InlineKeyboardButton("🔙 Orqaga", callback_data=f"cat_{product.category.id}"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Product.DoesNotExist:
        send_safe_message(chat_id, "❌ Mahsulot topilmadi.", get_main_menu_keyboard())

def show_cart(chat_id, user):
    """Savatni ko'rsatish"""
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        text = "🛒 Savatingiz bo'sh\n\n"
        text += "🍕 Mahsulotlarni ko'rish uchun 'Menyu' tugmasini bosing."
        send_safe_message(chat_id, text, get_main_menu_keyboard())
        return
    
    text = "🛒 Sizning savatingiz:\n\n"
    total_price = Decimal('0')
    
    for item in cart_items:
        item_total = item.get_total_price()
        total_price += item_total
        text += f"🍕 {item.product.name}\n"
        text += f"💰 {item.product.price:,} so'm x {item.quantity} = {item_total:,} so'm\n\n"
    
    text += f"💳 Jami: {total_price:,} so'm"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Har bir mahsulot uchun boshqaruv tugmalari
    for item in cart_items:
        markup.add(
            types.InlineKeyboardButton(f"➖ {item.product.name}", callback_data=f"decrease_{item.product.id}"),
            types.InlineKeyboardButton(f"➕ {item.product.name}", callback_data=f"increase_{item.product.id}")
        )
    
    # Asosiy tugmalar
    markup.add(
        types.InlineKeyboardButton("🗑️ Savatni tozalash", callback_data="clear_cart"),
        types.InlineKeyboardButton("✅ Buyurtma berish", callback_data="place_order")
    )
    markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
    
    send_safe_message(chat_id, text, markup)

def show_user_orders(chat_id, user):
    """Foydalanuvchi buyurtmalarini ko'rsatish"""
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]  # So'nggi 10 ta
    
    if not orders.exists():
        text = "📋 Sizda hali buyurtmalar yo'q\n\n"
        text += "🍕 Birinchi buyurtmangizni berish uchun 'Menyu' tugmasini bosing!"
        send_safe_message(chat_id, text, get_main_menu_keyboard())
        return
    
    text = "📋 Sizning buyurtmalaringiz:\n\n"
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'preparing': '👨‍🍳',
            'delivering': '🚗',
            'completed': '✅',
            'cancelled': '❌'
        }.get(order.status, '❓')
        
        text += f"{status_emoji} Buyurtma #{order.id}\n"
        text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"💰 {order.total_amount:,} so'm\n"
        text += f"📍 {order.get_status_display()}\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
    
    send_safe_message(chat_id, text, markup)

def place_order(chat_id, user):
    """Buyurtma berish"""
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        send_safe_message(chat_id, "❌ Savatingiz bo'sh! Avval mahsulot qo'shing.", get_main_menu_keyboard())
        return
    
    try:
        # Buyurtma yaratish
        total_amount = Decimal('0')
        for item in cart_items:
            total_amount += item.get_total_price()
        
        # Yetkazib berish manzili
        delivery_address = f"{user.dormitory.name}, {user.room_number}-xona" if user.dormitory else "Aniqlanmagan"
        
        # Buyurtma yaratish
        order = Order.objects.create(
            user=user,
            dormitory=user.dormitory,
            delivery_address=delivery_address,
            room_number=user.room_number,
            phone_number=user.phone_number,
            total_amount=total_amount,
            status='pending'
        )
        
        # Buyurtma mahsulotlarini yaratish
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Savatni tozalash
        cart_items.delete()
        
        # Buyurtma tasdiqlanganini yuborish
        text = f"✅ Buyurtma #{order.id} muvaffaqiyatli qabul qilindi!\n\n"
        text += f"📅 Vaqt: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"💰 Summa: {total_amount:,} so'm\n"
        text += f"📍 Manzil: {delivery_address}\n"
        text += f"📱 Telefon: {user.phone_number}\n\n"
        text += "⏳ Buyurtmangiz ko'rib chiqilmoqda...\n"
        text += "📞 Tez orada siz bilan bog'lanamiz!"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders"))
        markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
        
        send_safe_message(chat_id, text, markup)
        
        # Admin/kitchen'ga xabar yuborish (keyinchalik qo'shiladi)
        logger.info(f"Yangi buyurtma: #{order.id} - {user.full_name} - {total_amount} so'm")
        
    except Exception as e:
        logger.error(f"Buyurtma berishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Buyurtma berishda xatolik yuz berdi. Qaytadan urinib ko'ring.", get_main_menu_keyboard())

# Bot handler'lari
def setup_handlers():
    """Bot handler'larni sozlash"""
    bot = get_bot()
    if not bot:
        return
    
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        """Start buyrug'i"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or ""
            first_name = message.from_user.first_name or ""
            
            # Foydalanuvchini bazaga saqlash
            user, created = TelegramUser.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'is_active': True
                }
            )
            
            # Agar foydalanuvchi ro'yxatdan o'tmagan bo'lsa, ro'yxatdan o'tkazish
            if not user.is_registered:
                start_registration(message.chat.id, user)
            else:
                # Ro'yxatdan o'tgan foydalanuvchi uchun asosiy menyu
                show_main_menu(message.chat.id, user)
            
        except Exception as e:
            logger.error(f"Start xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

    @bot.message_handler(content_types=['contact'])
    def handle_contact(message):
        """Telefon raqamini qabul qilish"""
        try:
            user_id = message.from_user.id
            user = TelegramUser.objects.get(user_id=user_id)
            
            if message.contact and message.contact.user_id == user_id:
                # O'z telefon raqamini yuborgan
                user.phone_number = message.contact.phone_number
                user.save()
                
                # Keyingi qadam - to'liq ismni so'rash
                ask_full_name(message.chat.id, user)
            else:
                # Boshqa birovning telefon raqamini yuborgan
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                contact_btn = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
                markup.add(contact_btn)
                
                send_safe_message(
                    message.chat.id,
                    "❌ Iltimos, o'zingizning telefon raqamingizni yuboring!",
                    markup
                )
                
        except Exception as e:
            logger.error(f"Contact handling xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call):
        """Callback query'larni qayta ishlash"""
        try:
            user_id = call.from_user.id
            user = TelegramUser.objects.get(user_id=user_id)
            data = call.data
            
            if data.startswith("dorm_"):
                # Yotoqxona tanlash
                dorm_id = int(data.split("_")[1])
                dormitory = Dormitory.objects.get(id=dorm_id)
                user.dormitory = dormitory
                user.save()
                
                ask_room_number(call.message.chat.id, user)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
            elif data.startswith("cat_"):
                # Kategoriya tanlash
                category_id = int(data.split("_")[1])
                show_category_products(call.message.chat.id, user, category_id)
                
            elif data.startswith("prod_"):
                # Mahsulot tanlash
                product_id = int(data.split("_")[1])
                show_product_details(call.message.chat.id, user, product_id)
                
            elif data.startswith("add_to_cart_"):
                # Savatga qo'shish
                product_id = int(data.split("_")[3])
                add_to_cart(call.message.chat.id, user, product_id)
                
            elif data.startswith("increase_"):
                # Savatda miqdorni oshirish
                product_id = int(data.split("_")[1])
                try:
                    cart_item = Cart.objects.get(user=user, product_id=product_id)
                    cart_item.quantity += 1
                    cart_item.save()
                    show_cart(call.message.chat.id, user)
                except Cart.DoesNotExist:
                    bot.answer_callback_query(call.id, "❌ Mahsulot savatda topilmadi")
                    
            elif data.startswith("decrease_"):
                # Savatda miqdorni kamaytirish
                product_id = int(data.split("_")[1])
                try:
                    cart_item = Cart.objects.get(user=user, product_id=product_id)
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()
                    show_cart(call.message.chat.id, user)
                except Cart.DoesNotExist:
                    bot.answer_callback_query(call.id, "❌ Mahsulot savatda topilmadi")
                    
            elif data == "clear_cart":
                # Savatni tozalash
                Cart.objects.filter(user=user).delete()
                send_safe_message(call.message.chat.id, "🗑️ Savat tozalandi!", get_main_menu_keyboard())
                
            elif data == "view_cart":
                # Savatni ko'rish
                show_cart(call.message.chat.id, user)
                
            elif data == "back_to_categories":
                # Kategoriyalarga qaytish
                show_menu_categories(call.message.chat.id, user)
                
            elif data == "back_to_main":
                # Bosh menyuga qaytish
                show_main_menu(call.message.chat.id, user)
                
            elif data == "place_order":
                # Buyurtma berish
                place_order(call.message.chat.id, user)
                
            elif data == "my_orders":
                # Buyurtmalarni ko'rish
                show_user_orders(call.message.chat.id, user)
            
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            logger.error(f"Callback handling xatosi: {e}")
            bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

    @bot.message_handler(func=lambda message: True)
    def handle_text_messages(message):
        """Barcha matnli xabarlarni qayta ishlash"""
        try:
            user_id = message.from_user.id
            text = message.text.strip()
            
            try:
                user = TelegramUser.objects.get(user_id=user_id)
            except TelegramUser.DoesNotExist:
                # Foydalanuvchi mavjud emas, start buyrug'ini yuborish
                send_safe_message(message.chat.id, "Iltimos, /start buyrug'ini bosing.")
                return
            
            # Ro'yxatdan o'tish jarayoni
            if not user.is_registered:
                # To'liq ismni kutmoqda
                if not user.full_name and user.phone_number:
                    user.full_name = text
                    user.save()
                    ask_dormitory(message.chat.id, user)
                    return
                
                # Xona raqamini kutmoqda
                if not user.room_number and user.dormitory:
                    user.room_number = text
                    user.is_registered = True
                    from django.utils import timezone
                    user.registration_date = timezone.now()
                    user.save()
                    
                    # Ro'yxatdan o'tish tugallandi
                    complete_registration(message.chat.id, user)
                    return
            
            # Ro'yxatdan o'tgan foydalanuvchi uchun asosiy xabarlar
            if text == "🍕 Menyu":
                show_menu_categories(message.chat.id, user)
            elif text == "🛒 Savat":
                show_cart(message.chat.id, user)
            elif text == "📋 Buyurtmalarim":
                show_user_orders(message.chat.id, user)
            elif text == "ℹ️ Ma'lumot":
                info_text = f"ℹ️ Sizning ma'lumotlaringiz:\n\n"
                info_text += f"👤 Ism: {user.full_name}\n"
                info_text += f"📱 Telefon: {user.phone_number}\n"
                info_text += f"🏠 Yotoqxona: {user.dormitory.name if user.dormitory else 'Tanlanmagan'}\n"
                info_text += f"🚪 Xona: {user.room_number}"
                send_safe_message(message.chat.id, info_text, get_main_menu_keyboard())
            else:
                # Noma'lum xabar
                send_safe_message(message.chat.id, "Iltimos, quyidagi tugmalardan birini tanlang:", get_main_menu_keyboard())
                
        except Exception as e:
            logger.error(f"Text message handling xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

def start_bot():
    """Botni ishga tushirish"""
    try:
        print("🚀 Bot ishga tushirish jarayoni boshlandi...")
        bot = get_bot()
        if not bot:
            logger.error("❌ Bot yaratilmadi!")
            print("❌ Bot yaratilmadi!")
            return
        
        setup_handlers()
        
        logger.info("🚀 Bot polling rejimida ishga tushmoqda...")
        print("🚀 Bot polling rejimida ishga tushmoqda...")
        
        # Bot'ni polling rejimida ishga tushirish - xatolikdan himoyalash bilan
        while True:
            try:
                bot.infinity_polling(timeout=10, long_polling_timeout=5, none_stop=False, interval=1)
                break  # Agar muvaffaqiyatli ishga tushsa, break
            except Exception as polling_error:
                logger.error(f"Polling xatosi: {polling_error}")
                print(f"⚠️ Polling xatosi: {polling_error}")
                
                # Agar 409 xatosi bo'lsa, kutish va qaytadan urinish
                if "409" in str(polling_error):
                    print("⏳ 409 xatosi - 10 soniya kutish...")
                    time.sleep(10)
                    # Bot instance'ni qaytadan yaratish
                    global bot_instance
                    bot_instance = None
                    bot = get_bot()
                    if not bot:
                        break
                else:
                    # Boshqa xatoliklar uchun qisqa kutish
                    time.sleep(5)
        
    except Exception as e:
        logger.error(f"Bot ishga tushirishda xatolik: {e}")
        print(f"❌ Bot ishga tushirishda xatolik: {e}")

def stop_bot():
    """Botni to'xtatish"""
    global bot_instance
    if bot_instance:
        try:
            bot_instance.stop_polling()
            bot_instance = None
            logger.info("🛑 Bot to'xtatildi")
        except Exception as e:
            logger.error(f"Bot to'xtatishda xatolik: {e}")

if __name__ == "__main__":
    start_bot()

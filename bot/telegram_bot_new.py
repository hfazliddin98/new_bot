#!/usr/bin/env python
"""
Django App ichida ishlaydigan Telegram bot - To'liq ro'yxatdan o'tkazish bilan
"""
import os
import sys
import django
import time
import logging
import requests
from pathlib import Path
from django.utils import timezone

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
        # Oldingi webhook va updatelarni tozalash
        base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        
        # Webhook o'chirish
        requests.get(f"{base_url}/deleteWebhook", timeout=10)
        
        # Pending updatelarni tozalash
        requests.get(f"{base_url}/getUpdates?offset=-1&timeout=1", timeout=10)
        
        time.sleep(1)
        
        # Bot yaratish
        bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
        logger.info("✅ Bot instance yaratildi")
        return bot
        
    except Exception as e:
        logger.error(f"Bot yaratishda xatolik: {e}")
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

def show_main_menu(chat_id, user):
    """Asosiy menyuni ko'rsatish"""
    text = f"👋 Salom {user.get_display_name()}!\n\n"
    text += "🍕 Nima qilmoqchisiz?"
    
    send_safe_message(chat_id, text, get_main_menu_keyboard())

def show_menu_categories(chat_id, user):
    """Menyu kategoriyalarini ko'rsatish"""
    categories = Category.objects.filter(is_active=True)
    
    if not categories.exists():
        send_safe_message(chat_id, "❌ Hozircha menyu bo'sh")
        return
    
    text = "🍕 Menyu kategoriyalari:\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for category in categories:
        markup.add(types.InlineKeyboardButton(
            f"{category.name}",
            callback_data=f"cat_{category.id}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
    send_safe_message(chat_id, text, markup)

def show_cart(chat_id, user):
    """Savatni ko'rsatish"""
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        text = "🛒 Savatingiz bo'sh\n\n"
        text += "🍕 Menyu bo'limidan mahsulot tanlang!"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🍕 Menyu", callback_data="show_menu"))
        send_safe_message(chat_id, text, markup)
        return
    
    text = "🛒 Savatingizdagi mahsulotlar:\n\n"
    total = 0
    
    for item in cart_items:
        item_total = item.product.price * item.quantity
        total += item_total
        text += f"• {item.product.name}\n"
        text += f"  💰 {item.product.price:,} so'm × {item.quantity} = {item_total:,} so'm\n\n"
    
    text += f"📊 Jami: {total:,} so'm"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Buyurtma berish", callback_data="make_order"),
        types.InlineKeyboardButton("🗑 Tozalash", callback_data="clear_cart")
    )
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
    
    send_safe_message(chat_id, text, markup)

def show_user_orders(chat_id, user):
    """Foydalanuvchi buyurtmalarini ko'rsatish"""
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    
    if not orders.exists():
        text = "📋 Sizda hali buyurtmalar yo'q\n\n"
        text += "🍕 Birinchi buyurtmangizni bering!"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🍕 Menyu", callback_data="show_menu"))
        send_safe_message(chat_id, text, markup)
        return
    
    text = "📋 Oxirgi buyurtmalaringiz:\n\n"
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'preparing': '👨‍🍳',
            'ready': '🍕',
            'delivered': '🚚',
            'cancelled': '❌'
        }
        
        text += f"{status_emoji.get(order.status, '📋')} Buyurtma #{order.id}\n"
        text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"💰 {order.total_amount:,} so'm\n"
        text += f"🏠 {order.dormitory.name if order.dormitory else 'Yotoqxona ko'rsatilmagan'}\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
    send_safe_message(chat_id, text, markup)

def show_info(chat_id, user):
    """Ma'lumot ko'rsatish"""
    text = "ℹ️ Xizmat haqida ma'lumot:\n\n"
    text += "🕐 Ish vaqti: 8:00 - 23:00\n"
    text += "📞 Aloqa: +998 90 123 45 67\n"
    text += "🚚 Yetkazib berish: Bepul\n"
    text += "💳 To'lov: Naqd pul\n\n"
    text += "📋 Sizning ma'lumotlaringiz:\n"
    text += f"👤 Ism: {user.full_name}\n"
    text += f"📱 Telefon: {user.phone_number}\n"
    text += f"🏠 Yotoqxona: {user.dormitory.name if user.dormitory else 'Tanlanmagan'}\n"
    text += f"🚪 Xona: {user.room_number}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_main"))
    send_safe_message(chat_id, text, markup)

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
            
            # Foydalanuvchini bazadan olish yoki yaratish
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
                
            elif data == "back_main":
                # Asosiy menyuga qaytish
                show_main_menu(call.message.chat.id, user)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
            elif data == "show_menu":
                # Menyuni ko'rsatish
                show_menu_categories(call.message.chat.id, user)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
            # Qo'shimcha callback'lar...
            
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
                show_info(message.chat.id, user)
            else:
                # Noma'lum xabar
                send_safe_message(message.chat.id, "Iltimos, quyidagi tugmalardan birini tanlang:", get_main_menu_keyboard())
                
        except Exception as e:
            logger.error(f"Text message handling xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

def start_bot():
    """Botni ishga tushirish"""
    try:
        bot = get_bot()
        if not bot:
            logger.error("Bot yaratilmadi!")
            return
        
        setup_handlers()
        
        logger.info("🚀 Bot ishga tushmoqda...")
        print("🚀 Bot ishga tushmoqda...")
        
        # Bot'ni polling rejimida ishga tushirish
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
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

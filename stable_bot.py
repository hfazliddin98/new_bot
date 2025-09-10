#!/usr/bin/env python
"""
Xatoliksiz Telegram bot - Retry va Error Handling bilan
"""
import os
import sys
import django
import time
import logging
import requests
from pathlib import Path

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

import telebot
from telebot import types
from bot.models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, DeliveryZone, Dormitory
from decimal import Decimal

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot tokenini to'g'ridan-to'g'ri yozamiz
BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"

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
        bot = telebot.TeleBot(BOT_TOKEN)
        
        # Bot holatini tekshirish
        me = bot.get_me()
        logger.info(f"Bot ishga tushdi: @{me.username}")
        
        return bot
        
    except Exception as e:
        logger.error(f"Bot yaratishda xatolik: {e}")
        return None

# Bot yaratish
bot = create_bot_instance()
if not bot:
    print("❌ Bot yaratilmadi!")
    sys.exit(1)

# Global o'zgaruvchilar
user_states = {}

class UserState:
    MENU = "menu"
    SELECT_DORMITORY = "select_dormitory"
    SELECT_ROOM = "select_room"
    ORDER_PHONE = "order_phone"
    ORDER_NOTES = "order_notes"

def safe_send_message(chat_id, text, **kwargs):
    """Xavfsiz xabar yuborish"""
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        logger.error(f"Xabar yuborishda xatolik: {e}")
        return None

def safe_edit_message(chat_id, message_id, text, **kwargs):
    """Xavfsiz xabar tahrirlash"""
    try:
        return bot.edit_message_text(text, chat_id, message_id, **kwargs)
    except Exception as e:
        logger.error(f"Xabar tahrirlashda xatolik: {e}")
        return None

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start buyrug'i"""
    try:
        user_data = message.from_user
        
        # Foydalanuvchini saqlash
        telegram_user, created = TelegramUser.objects.get_or_create(
            user_id=user_data.id,
            defaults={
                'username': user_data.username or '',
                'first_name': user_data.first_name or '',
                'last_name': user_data.last_name or '',
            }
        )
        
        if not created:
            telegram_user.first_name = user_data.first_name or ''
            telegram_user.save()
        
        # Asosiy menyu
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🍽️ Menyu')
        btn2 = types.KeyboardButton('🛒 Savatcha')
        btn3 = types.KeyboardButton('🏠 Yotoqxonalar')
        btn4 = types.KeyboardButton('📞 Aloqa')
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        
        welcome_text = f"""🍽️ *Salom {telegram_user.first_name}!*

Yotoqxonalarga yetkazib berish botiga xush kelibsiz!

🥘 Mazali taomlar
🏠 Yotoqxonalarga yetkazib berish
🚚 Tez yetkazib berish
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
        
        safe_send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
        logger.info(f"Start buyrug'i: {telegram_user.first_name}")
        
    except Exception as e:
        logger.error(f"Start xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan /start bosing.")

@bot.message_handler(func=lambda message: message.text == '🏠 Yotoqxonalar')
def dormitories_handler(message):
    """Yotoqxonalar ro'yxati"""
    try:
        zones = DeliveryZone.objects.filter(is_active=True)
        
        if not zones.exists():
            safe_send_message(message.chat.id, "❌ Yetkazib berish zonalari mavjud emas!")
            return
        
        text = "🏠 *Yotoqxonalar ro'yxati:*\n\n"
        
        for zone in zones:
            dorms = Dormitory.objects.filter(zone=zone, is_active=True)
            if dorms.exists():
                text += f"📍 *{zone.name}* ({zone.delivery_fee:,.0f} so'm)\n"
                text += f"⏱️ Yetkazib berish: {zone.delivery_time} daqiqa\n\n"
                
                for dorm in dorms:
                    text += f"🏠 {dorm.name}\n"
                    text += f"📍 {dorm.address}\n"
                    if dorm.contact_person:
                        text += f"👤 {dorm.contact_person} - {dorm.contact_phone}\n"
                    text += "\n"
                text += "➖➖➖➖➖➖➖➖➖➖\n\n"
        
        markup = types.InlineKeyboardMarkup()
        for zone in zones:
            dorms_count = Dormitory.objects.filter(zone=zone, is_active=True).count()
            if dorms_count > 0:
                btn = types.InlineKeyboardButton(
                    f"{zone.name} ({dorms_count} ta)",
                    callback_data=f'zone_{zone.id}'
                )
                markup.add(btn)
        
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxonalar xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Yotoqxonalar ma'lumotini yuklab bo'lmadi.")

@bot.message_handler(func=lambda message: message.text == '🍽️ Menyu')
def menu_handler(message):
    """Menyu bo'limi"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            safe_send_message(message.chat.id, "❌ Kategoriyalar mavjud emas!")
            return
        
        text = "🍽️ *Kategoriyani tanlang:*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for category in categories:
            products_count = Product.objects.filter(category=category, is_available=True).count()
            btn_text = f"{category.name} ({products_count} ta)"
            btn = types.InlineKeyboardButton(btn_text, callback_data=f'cat_{category.id}')
            markup.add(btn)
            text += f"• {category.name} - {products_count} ta mahsulot\n"
        
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Menu xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Menyu ma'lumotini yuklab bo'lmadi.")

@bot.message_handler(func=lambda message: message.text == '🛒 Savatcha')
def cart_handler(message):
    """Savatcha"""
    try:
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            safe_send_message(message.chat.id, "🛒 Savatchangiz bo'sh")
            return
        
        total = sum(item.get_total_price() for item in cart_items)
        text = "🛒 *Savatchangiz:*\n\n"
        
        for item in cart_items:
            text += f"• {item.product.name}\n"
            text += f"  {item.quantity} x {item.product.price:,.0f} = {item.get_total_price():,.0f} so'm\n\n"
        
        text += f"💰 *Jami: {total:,.0f} so'm*"
        
        markup = types.InlineKeyboardMarkup()
        order_btn = types.InlineKeyboardButton('📋 Buyurtma berish', callback_data='create_order')
        clear_btn = types.InlineKeyboardButton('🗑️ Tozalash', callback_data='clear_cart')
        markup.add(order_btn)
        markup.add(clear_btn)
        
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except TelegramUser.DoesNotExist:
        safe_send_message(message.chat.id, "❌ Avval /start buyrug'ini bosing")
    except Exception as e:
        logger.error(f"Savatcha xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Savatcha ma'lumotini yuklab bo'lmadi.")

@bot.message_handler(func=lambda message: message.text == '📞 Aloqa')
def contact_handler(message):
    """Aloqa"""
    contact_text = """📞 *Aloqa ma'lumotlari:*

📱 Telefon: +998 90 123 45 67
📧 Email: info@delivery.uz
📍 Manzil: Toshkent sh.

⏰ *Ish vaqti:*
09:00 - 23:00 (har kuni)

🏠 *Yetkazib berish hududlari:*
• Universitet hududi (15 daq)
• Shahar markazi (25 daq)  
• Chetki hududlar (35 daq)"""
    
    safe_send_message(message.chat.id, contact_text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Barcha callback querylarni boshqarish"""
    try:
        # Callback ni confirm qilish
        bot.answer_callback_query(call.id)
        
        if call.data.startswith('zone_'):
            zone_callback(call)
        elif call.data.startswith('dorm_'):
            dormitory_callback(call)
        elif call.data.startswith('select_dorm_'):
            select_dormitory_callback(call)
        elif call.data.startswith('cat_'):
            category_callback(call)
        elif call.data.startswith('prod_'):
            product_callback(call)
        elif call.data.startswith('add_'):
            add_to_cart_callback(call)
        elif call.data == 'create_order':
            create_order_callback(call)
        elif call.data == 'show_dormitories':
            show_dormitories_callback(call)
        elif call.data.startswith('order_zone_'):
            order_zone_callback(call)
        elif call.data.startswith('order_dorm_'):
            order_dormitory_callback(call)
        elif call.data == 'back_to_menu':
            back_to_menu_callback(call)
        elif call.data == 'clear_cart':
            clear_cart_callback(call)
        else:
            logger.warning(f"Noma'lum callback: {call.data}")
            
    except Exception as e:
        logger.error(f"Callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def zone_callback(call):
    """Zona tanlash"""
    try:
        zone_id = int(call.data.split('_')[1])
        zone = DeliveryZone.objects.get(id=zone_id, is_active=True)
        dorms = Dormitory.objects.filter(zone=zone, is_active=True)
        
        if not dorms.exists():
            bot.answer_callback_query(call.id, "❌ Bu zonada yotoqxonalar yo'q")
            return
        
        text = f"🏠 *{zone.name}*\n\n"
        text += f"💰 Yetkazib berish haqi: {zone.delivery_fee:,.0f} so'm\n"
        text += f"⏱️ Yetkazib berish vaqti: {zone.delivery_time} daqiqa\n\n"
        text += "Yotoqxonani tanlang:\n\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for dorm in dorms:
            btn = types.InlineKeyboardButton(
                f"🏠 {dorm.name}",
                callback_data=f'dorm_{dorm.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('⬅️ Orqaga', callback_data='back_to_zones')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Zona callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def dormitory_callback(call):
    """Yotoqxona tanlash"""
    try:
        dorm_id = int(call.data.split('_')[1])
        dorm = Dormitory.objects.get(id=dorm_id, is_active=True)
        
        text = f"🏠 *{dorm.name}*\n\n"
        text += f"📍 Manzil: {dorm.address}\n"
        text += f"🏷️ Zona: {dorm.zone.name}\n"
        text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n"
        text += f"⏱️ Vaqt: {dorm.zone.delivery_time} daqiqa\n\n"
        
        if dorm.contact_person:
            text += f"👤 Mas'ul: {dorm.contact_person}\n"
            text += f"📞 Telefon: {dorm.contact_phone}\n\n"
        
        if dorm.notes:
            text += f"📝 Qo'shimcha: {dorm.notes}\n\n"
        
        text += "Bu yotoqxonani tanlaysizmi?"
        
        markup = types.InlineKeyboardMarkup()
        select_btn = types.InlineKeyboardButton(
            '✅ Tanlash', 
            callback_data=f'select_dorm_{dorm.id}'
        )
        back_btn = types.InlineKeyboardButton(
            '⬅️ Orqaga', 
            callback_data=f'zone_{dorm.zone.id}'
        )
        markup.add(select_btn)
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxona callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def select_dormitory_callback(call):
    """Yotoqxonani tanlash"""
    try:
        dorm_id = int(call.data.split('_')[2])
        dorm = Dormitory.objects.get(id=dorm_id, is_active=True)
        
        # Foydalanuvchi holatini saqlash
        user_states[call.from_user.id] = {
            'state': UserState.SELECT_ROOM,
            'dormitory_id': dorm_id
        }
        
        text = f"🏠 *{dorm.name}* tanlandi!\n\n"
        text += "📝 Iltimos, xona raqamingizni kiriting:\n"
        text += "(Masalan: 101, 205, A-15)"
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, parse_mode='Markdown')
        bot.answer_callback_query(call.id, f"✅ {dorm.name} tanlandi!")
        
    except Exception as e:
        logger.error(f"Yotoqxona tanlash xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def category_callback(call):
    """Kategoriya tanlash"""
    try:
        category_id = int(call.data.split('_')[1])
        category = Category.objects.get(id=category_id, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            bot.answer_callback_query(call.id, "❌ Bu kategoriyada mahsulotlar yo'q")
            return
        
        text = f"🍽️ *{category.name}*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for product in products:
            btn = types.InlineKeyboardButton(
                f"{product.name} - {product.price:,.0f} so'm",
                callback_data=f'prod_{product.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('⬅️ Orqaga', callback_data='back_to_menu')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Kategoriya callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def product_callback(call):
    """Mahsulot tanlash"""
    try:
        product_id = int(call.data.split('_')[1])
        product = Product.objects.get(id=product_id, is_available=True)
        
        text = f"🍽️ *{product.name}*\n\n"
        text += f"📝 {product.description}\n\n"
        text += f"💰 Narx: *{product.price:,.0f} so'm*"
        
        markup = types.InlineKeyboardMarkup()
        add_btn = types.InlineKeyboardButton(
            '➕ Savatchaga qo\'shish', 
            callback_data=f'add_{product.id}'
        )
        back_btn = types.InlineKeyboardButton(
            '⬅️ Orqaga', 
            callback_data=f'cat_{product.category.id}'
        )
        markup.add(add_btn)
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Mahsulot callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def add_to_cart_callback(call):
    """Savatchaga qo'shish"""
    try:
        product_id = int(call.data.split('_')[1])
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        product = Product.objects.get(id=product_id, is_available=True)
        
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        bot.answer_callback_query(
            call.id, 
            f"✅ {product.name} savatchaga qo'shildi! (Jami: {cart_item.quantity})"
        )
        
    except Exception as e:
        logger.error(f"Savatchaga qo'shish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def create_order_callback(call):
    """Buyurtma yaratish"""
    try:
        text = """📋 *Buyurtma berish*

Buyurtma berish uchun avval yotoqxonangizni tanlang.

🏠 Yotoqxonalar ro'yxatini ko'rish uchun asosiy menyudan "🏠 Yotoqxonalar" tugmasini bosing."""
        
        markup = types.InlineKeyboardMarkup()
        dorms_btn = types.InlineKeyboardButton('🏠 Yotoqxonalar', callback_data='show_dormitories')
        markup.add(dorms_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma yaratish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def show_dormitories_callback(call):
    """Yotoqxonalarni ko'rsatish"""
    try:
        zones = DeliveryZone.objects.filter(is_active=True)
        
        text = "🏠 *Yotoqxonani tanlang:*\n\n"
        markup = types.InlineKeyboardMarkup()
        
        for zone in zones:
            dorms_count = Dormitory.objects.filter(zone=zone, is_active=True).count()
            if dorms_count > 0:
                btn = types.InlineKeyboardButton(
                    f"{zone.name} ({dorms_count} ta)",
                    callback_data=f'order_zone_{zone.id}'
                )
                markup.add(btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxonalar ko'rsatish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def order_zone_callback(call):
    """Buyurtma uchun zona tanlash"""
    try:
        zone_id = int(call.data.split('_')[2])
        zone = DeliveryZone.objects.get(id=zone_id, is_active=True)
        dorms = Dormitory.objects.filter(zone=zone, is_active=True)
        
        text = f"🏠 *{zone.name}*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for dorm in dorms:
            btn = types.InlineKeyboardButton(
                f"🏠 {dorm.name}",
                callback_data=f'order_dorm_{dorm.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('⬅️ Orqaga', callback_data='show_dormitories')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma zona callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def order_dormitory_callback(call):
    """Buyurtma uchun yotoqxona tanlash"""
    try:
        dorm_id = int(call.data.split('_')[2])
        dorm = Dormitory.objects.get(id=dorm_id, is_active=True)
        
        # Foydalanuvchi holatini saqlash
        user_states[call.from_user.id] = {
            'state': UserState.SELECT_ROOM,
            'dormitory_id': dorm_id,
            'order_mode': True
        }
        
        text = f"🏠 *{dorm.name}* tanlandi!\n\n"
        text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n\n"
        text += "📝 Iltimos, xona raqamingizni kiriting:"
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma yotoqxona callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def back_to_menu_callback(call):
    """Menyuga qaytish"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        text = "🍽️ *Kategoriyani tanlang:*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for category in categories:
            products_count = Product.objects.filter(category=category, is_available=True).count()
            btn_text = f"{category.name} ({products_count} ta)"
            btn = types.InlineKeyboardButton(btn_text, callback_data=f'cat_{category.id}')
            markup.add(btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Menyuga qaytish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def clear_cart_callback(call):
    """Savatchani tozalash"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        Cart.objects.filter(user=user).delete()
        
        safe_edit_message(call.message.chat.id, call.message.message_id, "🗑️ Savatcha tozalandi!")
        bot.answer_callback_query(call.id, "✅ Savatcha tozalandi!")
        
    except Exception as e:
        logger.error(f"Savatcha tozalash xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_input(message):
    """Foydalanuvchi kiritmalari"""
    try:
        user_id = message.from_user.id
        state_data = user_states.get(user_id)
        
        if not state_data:
            return
        
        if state_data['state'] == UserState.SELECT_ROOM:
            room_number = message.text.strip()
            
            if len(room_number) < 1 or len(room_number) > 20:
                safe_send_message(message.chat.id, "❌ Xona raqami noto'g'ri. Qaytdan kiriting:")
                return
            
            dorm = Dormitory.objects.get(id=state_data['dormitory_id'])
            
            if state_data.get('order_mode'):
                # Buyurtma yaratish
                user_states[user_id]['room_number'] = room_number
                user_states[user_id]['state'] = UserState.ORDER_PHONE
                
                text = f"✅ *Buyurtma ma'lumotlari:*\n\n"
                text += f"🏠 Yotoqxona: {dorm.name}\n"
                text += f"🚪 Xona: {room_number}\n"
                text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n\n"
                text += "📞 Telefon raqamingizni kiriting:\n"
                text += "(Masalan: +998901234567)"
                
                safe_send_message(message.chat.id, text, parse_mode='Markdown')
            else:
                # Oddiy ma'lumot ko'rsatish
                del user_states[user_id]
                
                text = f"✅ *Ma'lumotlar saqlandi!*\n\n"
                text += f"🏠 Yotoqxona: {dorm.name}\n"
                text += f"🚪 Xona: {room_number}\n"
                text += f"📍 Manzil: {dorm.address}\n"
                text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm"
                
                safe_send_message(message.chat.id, text, parse_mode='Markdown')
        
        elif state_data['state'] == UserState.ORDER_PHONE:
            phone = message.text.strip()
            
            if len(phone) < 9:
                safe_send_message(message.chat.id, "❌ Telefon raqami noto'g'ri. Qaytadan kiriting:")
                return
            
            # Buyurtma yaratish
            user = TelegramUser.objects.get(user_id=user_id)
            dorm = Dormitory.objects.get(id=state_data['dormitory_id'])
            cart_items = Cart.objects.filter(user=user)
            
            if not cart_items.exists():
                safe_send_message(message.chat.id, "❌ Savatchangiz bo'sh!")
                del user_states[user_id]
                return
            
            # Umumiy summa hisoblash
            products_total = sum(item.get_total_price() for item in cart_items)
            delivery_fee = dorm.zone.delivery_fee
            total_amount = products_total + delivery_fee
            
            # Buyurtma yaratish
            order = Order.objects.create(
                user=user,
                dormitory=dorm,
                delivery_zone=dorm.zone,
                delivery_address=f"{dorm.name}, {dorm.address}",
                room_number=state_data['room_number'],
                phone_number=phone,
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                status='pending'
            )
            
            # Buyurtma mahsulotlarini saqlash
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Savatchani tozalash
            cart_items.delete()
            
            # Holatni o'chirish
            del user_states[user_id]
            
            # Buyurtma tasdiqlash
            text = f"✅ *Buyurtma #{order.id} qabul qilindi!*\n\n"
            text += f"🏠 Yotoqxona: {dorm.name}\n"
            text += f"🚪 Xona: {state_data['room_number']}\n"
            text += f"📞 Telefon: {phone}\n\n"
            text += f"💰 Mahsulotlar: {products_total:,.0f} so'm\n"
            text += f"🚚 Yetkazib berish: {delivery_fee:,.0f} so'm\n"
            text += f"💳 *Jami: {total_amount:,.0f} so'm*\n\n"
            text += f"⏱️ Yetkazib berish vaqti: {dorm.zone.delivery_time} daqiqa\n"
            text += f"📋 Holat: Kutilmoqda"
            
            safe_send_message(message.chat.id, text, parse_mode='Markdown')
            logger.info(f"Buyurtma yaratildi: #{order.id}")
            
    except Exception as e:
        logger.error(f"Foydalanuvchi kiritma xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Barcha boshqa xabarlar"""
    if message.from_user.id not in user_states:
        safe_send_message(message.chat.id, "❓ Kerakli tugmani tanlang yoki /start buyrug'ini bosing")

def main():
    """Asosiy bot funksiya"""
    global bot  # Global o'zgaruvchi
    
    print("🤖 Xatoliksiz Telegram bot ishga tushmoqda...")
    print("🔗 Admin panel: http://127.0.0.1:8000/admin")
    print("⏹️ To'xtatish uchun Ctrl+C bosing")
    
    # Polling boshqaruvi
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info("Bot polling boshlandi")
            bot.infinity_polling(
                none_stop=True, 
                interval=2, 
                timeout=30,
                skip_pending=True  # Oldingi updatelarni o'tkazib yuborish
            )
            break
            
        except KeyboardInterrupt:
            print("\n🛑 Bot to'xtatildi")
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"Bot xatosi ({retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                wait_time = min(10 * retry_count, 60)  # Progressiv kutish
                print(f"🔄 {wait_time} soniyadan so'ng qayta urinish...")
                time.sleep(wait_time)
                
                # Bot instanceni qayta yaratish
                bot = create_bot_instance()
                if not bot:
                    print("❌ Bot qayta yaratilmadi!")
                    break
            else:
                print("❌ Maksimal urinishlar tugadi!")
                break

if __name__ == "__main__":
    main()

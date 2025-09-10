#!/usr/bin/env python
"""
Registratsiya tizimi bilan Telegram bot
"""
import os
import sys
import django
import time
import logging
import requests
import re
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
from django.utils import timezone
from datetime import timedelta

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
    # Registratsiya
    REGISTRATION_NAME = "registration_name"
    REGISTRATION_AGE = "registration_age"
    REGISTRATION_PHONE = "registration_phone"
    
    # Asosiy funksiyalar
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

def is_user_registered(user_id):
    """Foydalanuvchi ro'yxatdan o'tganligini tekshirish"""
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        return user.is_registered
    except TelegramUser.DoesNotExist:
        return False

def create_main_menu():
    """Asosiy menyu yaratish"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🍽️ Menyu')
    btn2 = types.KeyboardButton('🛒 Savatcha')
    btn3 = types.KeyboardButton('🏠 Yotoqxonalar')
    btn4 = types.KeyboardButton('⏰ Ish soatlari')
    btn5 = types.KeyboardButton('👤 Profil')
    btn6 = types.KeyboardButton('📞 Aloqa')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start buyrug'i va registratsiya"""
    try:
        user_data = message.from_user
        
        # Foydalanuvchini saqlash yoki olish
        telegram_user, created = TelegramUser.objects.get_or_create(
            user_id=user_data.id,
            defaults={
                'username': user_data.username or '',
                'first_name': user_data.first_name or '',
                'last_name': user_data.last_name or '',
            }
        )
        
        if not created:
            # Mavjud foydalanuvchi ma'lumotlarini yangilash
            telegram_user.username = user_data.username or telegram_user.username
            telegram_user.first_name = user_data.first_name or telegram_user.first_name
            telegram_user.last_name = user_data.last_name or telegram_user.last_name
            telegram_user.save()
        
        # Registratsiya tekshirish
        if not telegram_user.is_registered:
            start_registration(message, telegram_user)
        else:
            show_main_menu(message, telegram_user)
        
        logger.info(f"Start buyrug'i: {telegram_user.get_display_name()}")
        
    except Exception as e:
        logger.error(f"Start xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan /start bosing.")

def start_registration(message, telegram_user):
    """Registratsiyani boshlash"""
    try:
        welcome_text = f"""👋 *Salom {telegram_user.first_name or 'Foydalanuvchi'}!*

🍽️ Yotoqxonalarga yetkazib berish botiga xush kelibsiz!

📝 Xizmatimizdan foydalanish uchun iltimos qisqa ro'yxatdan o'ting.

👤 *Birinchi qadam:*
To'liq ismingizni kiriting (Ism Familiya):

*Masalan:* Aziz Karimov"""
        
        safe_send_message(message.chat.id, welcome_text, parse_mode='Markdown')
        
        # Foydalanuvchi holatini saqlash
        user_states[message.from_user.id] = {
            'state': UserState.REGISTRATION_NAME,
            'user_obj': telegram_user
        }
        
    except Exception as e:
        logger.error(f"Registratsiya boshlash xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Registratsiyada xatolik. Qaytadan /start bosing.")

def show_main_menu(message, telegram_user):
    """Asosiy menyuni ko'rsatish"""
    try:
        markup = create_main_menu()
        
        welcome_text = f"""🍽️ *Xush kelibsiz, {telegram_user.get_display_name()}!*

Yotoqxonalarga yetkazib berish botiga qaytgan kunlar bilan!

🥘 Mazali taomlar
🏠 Yotoqxonalarga yetkazib berish
🚚 Tez yetkazib berish
⏰ Aniq yetkazib berish vaqti
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
        
        safe_send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Asosiy menyu xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Menyu yuklanmadi. Qaytadan /start bosing.")

@bot.message_handler(func=lambda message: message.text == '👤 Profil')
def profile_handler(message):
    """Profil ma'lumotlari"""
    try:
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        
        text = f"""👤 *Profil ma'lumotlari:*

👤 To'liq ism: {user.full_name or 'Kiritilmagan'}
🎂 Yosh: {user.age or 'Kiritilmagan'}
📞 Telefon: {user.phone_number or 'Kiritilmagan'}
📱 Username: @{user.username or 'Yo\'q'}
📅 Ro'yxatdan o'tgan: {user.registration_date.strftime('%d.%m.%Y %H:%M') if user.registration_date else 'Noma\'lum'}
🛒 Buyurtmalar soni: {Order.objects.filter(user=user).count()}

📝 Ma'lumotlarni yangilash uchun /start buyrug'ini bosing."""
        
        markup = types.InlineKeyboardMarkup()
        edit_btn = types.InlineKeyboardButton('✏️ Tahrirlash', callback_data='edit_profile')
        markup.add(edit_btn)
        
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Profil xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Profil ma'lumotini yuklab bo'lmadi.")

@bot.message_handler(func=lambda message: message.text == '⏰ Ish soatlari')
def working_hours_handler(message):
    """Ish soatlari ma'lumoti"""
    try:
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
        zones = DeliveryZone.objects.filter(is_active=True)
        
        if not zones.exists():
            safe_send_message(message.chat.id, "❌ Yetkazib berish zonalari mavjud emas!")
            return
        
        current_time = timezone.now()
        text = "⏰ *Yetkazib berish soatlari:*\n\n"
        text += f"🕐 Hozirgi vaqt: {current_time.strftime('%H:%M')}\n\n"
        
        for zone in zones:
            text += f"📍 *{zone.name}*\n"
            text += f"🕐 Ish soatlari: {zone.get_working_hours_display()}\n"
            
            if zone.is_working_now():
                text += "✅ Hozir ishlaydi\n"
                text += f"💰 Yetkazib berish: {zone.delivery_fee:,.0f} so'm\n"
                text += f"⏱️ Vaqt: {zone.delivery_time} daqiqa\n"
            else:
                text += "❌ Hozir ishlamaydi\n"
                next_opening = "Ertaga " + zone.working_hours_start.strftime('%H:%M')
                text += f"🔄 Keyingi ochilish: {next_opening}\n"
            
            text += "\n"
        
        text += "📝 *Eslatma:* Buyurtma faqat ish soatlarida qabul qilinadi."
        
        safe_send_message(message.chat.id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ish soatlari xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Ish soatlari ma'lumotini yuklab bo'lmadi.")

@bot.message_handler(func=lambda message: message.text == '🏠 Yotoqxonalar')
def dormitories_handler(message):
    """Yotoqxonalar ro'yxati"""
    try:
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
        zones = DeliveryZone.objects.filter(is_active=True)
        
        if not zones.exists():
            safe_send_message(message.chat.id, "❌ Yetkazib berish zonalari mavjud emas!")
            return
        
        text = "🏠 *Yotoqxonalar ro'yxati:*\n\n"
        
        for zone in zones:
            dorms = Dormitory.objects.filter(zone=zone, is_active=True)
            if dorms.exists():
                # Zona holati
                status_icon = "✅" if zone.is_working_now() else "❌"
                text += f"📍 *{zone.name}* {status_icon}\n"
                text += f"🕐 {zone.get_working_hours_display()}\n"
                text += f"💰 {zone.delivery_fee:,.0f} so'm | ⏱️ {zone.delivery_time} daq\n\n"
                
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
                # Holat ko'rsatkichi
                status = "✅" if zone.is_working_now() else "❌"
                btn_text = f"{status} {zone.name} ({dorms_count} ta)"
                btn = types.InlineKeyboardButton(
                    btn_text,
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
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
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
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
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
• Universitet hududi: 08:00 - 22:00
• Shahar markazi: 09:00 - 23:00  
• Chetki hududlar: 10:00 - 21:00

🚚 *Yetkazib berish:*
• Har kuni ish soatlarida
• Aniq vaqt ko'rsatiladi
• SMS orqali tasdiqlash

🤖 *Bot haqida:*
• 24/7 buyurtma qabul qilish
• Avtomatik order tracking
• Tez va ishonchli xizmat"""
    
    safe_send_message(message.chat.id, contact_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_input(message):
    """Foydalanuvchi kiritmalari"""
    try:
        user_id = message.from_user.id
        state_data = user_states.get(user_id)
        
        if not state_data:
            return
        
        # Registratsiya jarayoni
        if state_data['state'] == UserState.REGISTRATION_NAME:
            full_name = message.text.strip()
            
            if len(full_name) < 2 or len(full_name) > 100:
                safe_send_message(message.chat.id, "❌ Ism noto'g'ri. Iltimos, to'liq ismingizni kiriting (2-100 belgi):")
                return
            
            # Ismni saqlash
            user_states[user_id]['full_name'] = full_name
            user_states[user_id]['state'] = UserState.REGISTRATION_AGE
            
            text = f"✅ *Ism saqlandi: {full_name}*\n\n"
            text += "🎂 *Ikkinchi qadam:*\n"
            text += "Yoshingizni kiriting (12-100):\n\n"
            text += "*Masalan:* 20"
            
            safe_send_message(message.chat.id, text, parse_mode='Markdown')
        
        elif state_data['state'] == UserState.REGISTRATION_AGE:
            try:
                age = int(message.text.strip())
                
                if age < 12 or age > 100:
                    safe_send_message(message.chat.id, "❌ Yosh noto'g'ri. 12-100 orasida kiriting:")
                    return
                
                # Yoshni saqlash
                user_states[user_id]['age'] = age
                user_states[user_id]['state'] = UserState.REGISTRATION_PHONE
                
                text = f"✅ *Yosh saqlandi: {age}*\n\n"
                text += "📞 *Uchinchi qadam:*\n"
                text += "Telefon raqamingizni kiriting:\n\n"
                text += "*Format:* +998901234567 yoki 901234567"
                
                # Telefon raqam tugmasini qo'shish
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                phone_btn = types.KeyboardButton('📞 Telefon raqamni yuborish', request_contact=True)
                markup.add(phone_btn)
                
                safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
                
            except ValueError:
                safe_send_message(message.chat.id, "❌ Noto'g'ri format. Faqat raqam kiriting:")
        
        elif state_data['state'] == UserState.REGISTRATION_PHONE:
            # Telefon raqamni olish
            phone = None
            
            if message.contact:
                # Telefon tugmasi orqali
                phone = message.contact.phone_number
            else:
                # Qo'lda kiritilgan
                phone_text = message.text.strip()
                # Telefon raqam formatini tekshirish
                phone_pattern = r'^(\+998|998|0)?([0-9]{9})$'
                match = re.match(phone_pattern, phone_text)
                
                if match:
                    phone = f"+998{match.group(2)}"
                else:
                    safe_send_message(message.chat.id, "❌ Noto'g'ri telefon format. Qaytadan kiriting yoki tugmani bosing:")
                    return
            
            # Registratsiyani yakunlash
            telegram_user = state_data['user_obj']
            telegram_user.full_name = state_data['full_name']
            telegram_user.age = state_data['age']
            telegram_user.phone_number = phone
            telegram_user.is_registered = True
            telegram_user.registration_date = timezone.now()
            telegram_user.save()
            
            # Holatni o'chirish
            del user_states[user_id]
            
            # Tabriklar va asosiy menyu
            text = f"🎉 *Tabriklaymiz!*\n\n"
            text += f"👤 {telegram_user.full_name}\n"
            text += f"🎂 {telegram_user.age} yosh\n"
            text += f"📞 {telegram_user.phone_number}\n\n"
            text += "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            text += "Endi barcha xizmatlardan foydalanishingiz mumkin."
            
            markup = create_main_menu()
            safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
            
            logger.info(f"Yangi foydalanuvchi ro'yxatdan o'tdi: {telegram_user.full_name}")
        
        # Asosiy funksiyalar (buyurtma berish)
        elif state_data['state'] == UserState.SELECT_ROOM:
            handle_room_selection(message, state_data)
        
        elif state_data['state'] == UserState.ORDER_PHONE:
            handle_order_phone(message, state_data)
            
    except Exception as e:
        logger.error(f"Foydalanuvchi kiritma xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]

def handle_room_selection(message, state_data):
    """Xona tanlash"""
    try:
        room_number = message.text.strip()
        
        if len(room_number) < 1 or len(room_number) > 20:
            safe_send_message(message.chat.id, "❌ Xona raqami noto'g'ri. Qaytdan kiriting:")
            return
        
        dorm = Dormitory.objects.get(id=state_data['dormitory_id'])
        
        # Zona holatini tekshirish
        if not dorm.zone.is_working_now():
            safe_send_message(message.chat.id, f"❌ {dorm.zone.name} hozir ishlamaydi. Ish soatlari: {dorm.zone.get_working_hours_display()}")
            del user_states[message.from_user.id]
            return
        
        if state_data.get('order_mode'):
            # Buyurtma yaratish
            user_states[message.from_user.id]['room_number'] = room_number
            user_states[message.from_user.id]['state'] = UserState.ORDER_PHONE
            
            # Kutilayotgan yetkazib berish vaqtini hisoblash
            current_time = timezone.now()
            expected_delivery = current_time + timedelta(minutes=dorm.zone.delivery_time)
            
            text = f"✅ *Buyurtma ma'lumotlari:*\n\n"
            text += f"🏠 Yotoqxona: {dorm.name}\n"
            text += f"🚪 Xona: {room_number}\n"
            text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n"
            text += f"🕐 Kutilayotgan vaqt: {expected_delivery.strftime('%H:%M')}\n\n"
            text += "📞 Telefon raqamingizni kiriting yoki tasdiqlang:\n"
            text += "(Masalan: +998901234567)"
            
            # Saqlangan telefon raqamni ko'rsatish
            user = TelegramUser.objects.get(user_id=message.from_user.id)
            if user.phone_number:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                confirm_btn = types.KeyboardButton(f"✅ {user.phone_number}")
                new_phone_btn = types.KeyboardButton('📞 Boshqa raqam', request_contact=True)
                markup.add(confirm_btn)
                markup.add(new_phone_btn)
                
                text += f"\n\n💾 *Saqlangan raqam:* {user.phone_number}"
                safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
            else:
                safe_send_message(message.chat.id, text, parse_mode='Markdown')
        else:
            # Oddiy ma'lumot ko'rsatish
            del user_states[message.from_user.id]
            
            text = f"✅ *Ma'lumotlar saqlandi!*\n\n"
            text += f"🏠 Yotoqxona: {dorm.name}\n"
            text += f"🚪 Xona: {room_number}\n"
            text += f"📍 Manzil: {dorm.address}\n"
            text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n"
            text += f"🕐 Ish vaqti: {dorm.zone.get_working_hours_display()}"
            
            safe_send_message(message.chat.id, text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Xona tanlash xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Xatolik yuz berdi.")

def handle_order_phone(message, state_data):
    """Buyurtma telefon raqami"""
    try:
        phone = None
        
        if message.contact:
            # Telefon tugmasi orqali
            phone = message.contact.phone_number
        else:
            # Matn orqali
            phone_text = message.text.strip()
            
            # Tasdiqlangan telefon raqamni tekshirish
            if phone_text.startswith('✅'):
                phone = phone_text.replace('✅ ', '').strip()
            else:
                # Yangi telefon raqam
                phone_pattern = r'^(\+998|998|0)?([0-9]{9})$'
                match = re.match(phone_pattern, phone_text)
                
                if match:
                    phone = f"+998{match.group(2)}"
                else:
                    safe_send_message(message.chat.id, "❌ Noto'g'ri telefon format. Qaytadan kiriting:")
                    return
        
        # Buyurtma yaratish
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        dorm = Dormitory.objects.get(id=state_data['dormitory_id'])
        cart_items = Cart.objects.filter(user=user)
        
        # Zona holatini qayta tekshirish
        if not dorm.zone.is_working_now():
            safe_send_message(message.chat.id, f"❌ {dorm.zone.name} hozir ishlamaydi!")
            del user_states[message.from_user.id]
            return
        
        if not cart_items.exists():
            safe_send_message(message.chat.id, "❌ Savatchangiz bo'sh!")
            del user_states[message.from_user.id]
            return
        
        # Umumiy summa hisoblash
        products_total = sum(item.get_total_price() for item in cart_items)
        delivery_fee = dorm.zone.delivery_fee
        total_amount = products_total + delivery_fee
        
        # Kutilayotgan yetkazib berish vaqtini hisoblash
        current_time = timezone.now()
        expected_delivery = current_time + timedelta(minutes=dorm.zone.delivery_time)
        
        # Buyurtma yaratish
        order = Order.objects.create(
            user=user,
            dormitory=dorm,
            delivery_zone=dorm.zone,
            delivery_address=f"{dorm.name}, {dorm.address}",
            room_number=state_data['room_number'],
            phone_number=phone,
            delivery_time=expected_delivery,
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
        
        # Telefon raqamni yangilash (agar yangi bo'lsa)
        if phone != user.phone_number:
            user.phone_number = phone
            user.save()
        
        # Holatni o'chirish
        del user_states[message.from_user.id]
        
        # Buyurtma tasdiqlash
        text = f"✅ *Buyurtma #{order.id} qabul qilindi!*\n\n"
        text += f"👤 Mijoz: {user.get_display_name()}\n"
        text += f"🏠 Yotoqxona: {dorm.name}\n"
        text += f"🚪 Xona: {state_data['room_number']}\n"
        text += f"📞 Telefon: {phone}\n\n"
        text += f"💰 Mahsulotlar: {products_total:,.0f} so'm\n"
        text += f"🚚 Yetkazib berish: {delivery_fee:,.0f} so'm\n"
        text += f"💳 *Jami: {total_amount:,.0f} so'm*\n\n"
        text += f"🕐 Kutilayotgan vaqt: {expected_delivery.strftime('%H:%M')}\n"
        text += f"📋 Holat: Kutilmoqda\n\n"
        text += "🚚 Yetkazuvchi tez orada aloqaga chiqadi!"
        
        markup = create_main_menu()
        safe_send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
        logger.info(f"Buyurtma yaratildi: #{order.id} - {user.get_display_name()} - {expected_delivery.strftime('%H:%M')}")
        
    except Exception as e:
        logger.error(f"Buyurtma telefon xatosi: {e}")
        safe_send_message(message.chat.id, "❌ Buyurtmada xatolik yuz berdi.")

# Callback handlerlar (qisqartirilgan)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Barcha callback querylarni boshqarish"""
    try:
        # Registratsiya tekshirish
        if not is_user_registered(call.from_user.id) and not call.data.startswith('edit_profile'):
            bot.answer_callback_query(call.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
            return
        
        # Callback ni confirm qilish
        bot.answer_callback_query(call.id)
        
        if call.data == 'edit_profile':
            edit_profile_callback(call)
        elif call.data.startswith('zone_'):
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
        elif call.data == 'view_cart':
            view_cart_callback(call)
        elif call.data == 'show_menu':
            show_menu_callback(call)
        else:
            logger.warning(f"Noma'lum callback: {call.data}")
            
    except Exception as e:
        logger.error(f"Callback xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def edit_profile_callback(call):
    """Profilni tahrirlash"""
    try:
        text = """✏️ *Profilni tahrirlash*

Ma'lumotlaringizni yangilash uchun /start buyrug'ini bosing va qaytadan ro'yxatdan o'ting.

Yangi ma'lumotlar eski ma'lumotlar ustiga yoziladi."""
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Profil tahrirlash xatosi: {e}")

def zone_callback(call):
    """Zona callback"""
    try:
        zone_id = int(call.data.split('_')[1])
        zone = DeliveryZone.objects.get(id=zone_id)
        
        dorms = Dormitory.objects.filter(zone=zone, is_active=True)
        
        text = f"🏠 *{zone.name} yotoqxonalari:*\n\n"
        text += f"🕐 Ish vaqti: {zone.get_working_hours_display()}\n"
        text += f"💰 Yetkazib berish: {zone.delivery_fee:,.0f} so'm\n"
        text += f"⏱️ Vaqt: {zone.delivery_time} daqiqa\n\n"
        
        if zone.is_working_now():
            text += "✅ Hozir ishlaydi\n\n"
        else:
            text += "❌ Hozir ishlamaydi\n\n"
        
        markup = types.InlineKeyboardMarkup()
        for dorm in dorms:
            btn = types.InlineKeyboardButton(
                f"🏠 {dorm.name}",
                callback_data=f'dorm_{dorm.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Orqaga', callback_data='back_to_menu')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Zona callback xatosi: {e}")

def dormitory_callback(call):
    """Yotoqxona callback"""
    try:
        dorm_id = int(call.data.split('_')[1])
        dorm = Dormitory.objects.get(id=dorm_id)
        
        text = f"🏠 *{dorm.name}*\n\n"
        text += f"📍 Manzil: {dorm.address}\n"
        text += f"🚚 Zona: {dorm.zone.name}\n"
        text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n"
        text += f"⏱️ Vaqt: {dorm.zone.delivery_time} daqiqa\n"
        text += f"🕐 Ish vaqti: {dorm.zone.get_working_hours_display()}\n\n"
        
        if dorm.contact_person:
            text += f"👤 Mas'ul: {dorm.contact_person}\n"
            text += f"📞 Telefon: {dorm.contact_phone}\n\n"
        
        status = "✅ Ishlaydi" if dorm.zone.is_working_now() else "❌ Ishlamaydi"
        text += f"📊 Holat: {status}"
        
        markup = types.InlineKeyboardMarkup()
        select_btn = types.InlineKeyboardButton(
            '🎯 Tanlash',
            callback_data=f'select_dorm_{dorm.id}'
        )
        back_btn = types.InlineKeyboardButton('🔙 Orqaga', callback_data=f'zone_{dorm.zone.id}')
        markup.add(select_btn)
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxona callback xatosi: {e}")

def select_dormitory_callback(call):
    """Yotoqxona tanlash"""
    try:
        dorm_id = int(call.data.split('_')[2])
        dorm = Dormitory.objects.get(id=dorm_id)
        
        text = f"🏠 *{dorm.name} tanlandi*\n\n"
        text += f"🚪 Xona raqamingizni kiriting:\n\n"
        text += "*Masalan:* 101, A-205, 3-15"
        
        # Foydalanuvchi holatini saqlash
        user_states[call.from_user.id] = {
            'state': UserState.SELECT_ROOM,
            'dormitory_id': dorm_id,
            'order_mode': False
        }
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxona tanlash xatosi: {e}")

def category_callback(call):
    """Kategoriya callback"""
    try:
        category_id = int(call.data.split('_')[1])
        category = Category.objects.get(id=category_id)
        
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            safe_edit_message(call.message.chat.id, call.message.message_id, f"❌ {category.name} bo'limida mahsulotlar mavjud emas.")
            return
        
        text = f"🍽️ *{category.name}*\n\n"
        
        markup = types.InlineKeyboardMarkup()
        for product in products:
            btn_text = f"{product.name} - {product.price:,.0f} so'm"
            btn = types.InlineKeyboardButton(btn_text, callback_data=f'prod_{product.id}')
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Kategoriyalar', callback_data='back_to_menu')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Kategoriya callback xatosi: {e}")

def product_callback(call):
    """Mahsulot callback"""
    try:
        product_id = int(call.data.split('_')[1])
        product = Product.objects.get(id=product_id)
        
        text = f"🍽️ *{product.name}*\n\n"
        text += f"💰 Narx: {product.price:,.0f} so'm\n"
        if product.description:
            text += f"📝 Tavsif: {product.description}\n"
        text += f"\n⚖️ Mavjud: {'✅ Ha' if product.is_available else '❌ Yo\'q'}"
        
        markup = types.InlineKeyboardMarkup()
        if product.is_available:
            add_btn = types.InlineKeyboardButton('🛒 Savatga qo\'shish', callback_data=f'add_{product.id}')
            markup.add(add_btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Orqaga', callback_data=f'cat_{product.category.id}')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Mahsulot callback xatosi: {e}")

def add_to_cart_callback(call):
    """Savatga qo'shish"""
    try:
        product_id = int(call.data.split('_')[1])
        product = Product.objects.get(id=product_id)
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        
        if not product.is_available:
            bot.answer_callback_query(call.id, "❌ Mahsulot mavjud emas")
            return
        
        # Savatda mavjudligini tekshirish
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            message = f"✅ {product.name} miqdori {cart_item.quantity} ga ko'paytirildi"
        else:
            message = f"✅ {product.name} savatga qo'shildi"
        
        bot.answer_callback_query(call.id, message)
        
        # Mahsulot ma'lumotini yangilash
        text = f"🍽️ *{product.name}*\n\n"
        text += f"💰 Narx: {product.price:,.0f} so'm\n"
        if product.description:
            text += f"📝 Tavsif: {product.description}\n"
        text += f"\n✅ Savatga qo'shildi!"
        
        markup = types.InlineKeyboardMarkup()
        add_btn = types.InlineKeyboardButton('🛒 Yana qo\'shish', callback_data=f'add_{product.id}')
        cart_btn = types.InlineKeyboardButton('🛒 Savatcha', callback_data='view_cart')
        back_btn = types.InlineKeyboardButton('🔙 Orqaga', callback_data=f'cat_{product.category.id}')
        markup.add(add_btn)
        markup.add(cart_btn)
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Savatga qo'shish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def create_order_callback(call):
    """Buyurtma yaratish boshlash"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            bot.answer_callback_query(call.id, "❌ Savatchangiz bo'sh")
            return
        
        # Yetkazib berish zonalarini ko'rsatish
        zones = DeliveryZone.objects.filter(is_active=True)
        
        if not zones.exists():
            safe_edit_message(call.message.chat.id, call.message.message_id, "❌ Yetkazib berish zonalari mavjud emas!")
            return
        
        text = "🛒 *Buyurtma berish*\n\n"
        text += "📍 Yetkazib berish zonasini tanlang:"
        
        markup = types.InlineKeyboardMarkup()
        for zone in zones:
            # Holat ko'rsatkichi
            status = "✅" if zone.is_working_now() else "❌"
            btn_text = f"{status} {zone.name}"
            btn = types.InlineKeyboardButton(btn_text, callback_data=f'order_zone_{zone.id}')
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Savatcha', callback_data='view_cart')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma yaratish xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def show_dormitories_callback(call):
    """Yotoqxonalar ko'rsatish callback"""
    try:
        # Bu funksiya dormitories_handler bilan bir xil
        zones = DeliveryZone.objects.filter(is_active=True)
        
        if not zones.exists():
            safe_edit_message(call.message.chat.id, call.message.message_id, "❌ Yetkazib berish zonalari mavjud emas!")
            return
        
        text = "🏠 *Yotoqxonalar ro'yxati:*\n\n"
        
        markup = types.InlineKeyboardMarkup()
        for zone in zones:
            dorms_count = Dormitory.objects.filter(zone=zone, is_active=True).count()
            if dorms_count > 0:
                status = "✅" if zone.is_working_now() else "❌"
                btn_text = f"{status} {zone.name} ({dorms_count} ta)"
                btn = types.InlineKeyboardButton(btn_text, callback_data=f'zone_{zone.id}')
                markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Asosiy menyu', callback_data='back_to_menu')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxonalar ko'rsatish xatosi: {e}")

def order_zone_callback(call):
    """Buyurtma uchun zona tanlash"""
    try:
        zone_id = int(call.data.split('_')[2])
        zone = DeliveryZone.objects.get(id=zone_id)
        
        # Zona holatini tekshirish
        if not zone.is_working_now():
            bot.answer_callback_query(call.id, f"❌ {zone.name} hozir ishlamaydi!")
            return
        
        dorms = Dormitory.objects.filter(zone=zone, is_active=True)
        
        if not dorms.exists():
            bot.answer_callback_query(call.id, "❌ Bu zonada yotoqxonalar mavjud emas!")
            return
        
        text = f"🏠 *{zone.name} - Yotoqxona tanlang:*\n\n"
        text += f"💰 Yetkazib berish: {zone.delivery_fee:,.0f} so'm\n"
        text += f"⏱️ Vaqt: {zone.delivery_time} daqiqa\n\n"
        
        markup = types.InlineKeyboardMarkup()
        for dorm in dorms:
            btn = types.InlineKeyboardButton(
                f"🏠 {dorm.name}",
                callback_data=f'order_dorm_{dorm.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('🔙 Orqaga', callback_data='create_order')
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma zona xatosi: {e}")

def order_dormitory_callback(call):
    """Buyurtma uchun yotoqxona tanlash"""
    try:
        dorm_id = int(call.data.split('_')[2])
        dorm = Dormitory.objects.get(id=dorm_id)
        
        # Zona holatini qayta tekshirish
        if not dorm.zone.is_working_now():
            bot.answer_callback_query(call.id, f"❌ {dorm.zone.name} hozir ishlamaydi!")
            return
        
        text = f"🏠 *{dorm.name} tanlandi*\n\n"
        text += f"📍 Manzil: {dorm.address}\n"
        text += f"💰 Yetkazib berish: {dorm.zone.delivery_fee:,.0f} so'm\n\n"
        text += f"🚪 Xona raqamingizni kiriting:"
        
        # Foydalanuvchi holatini saqlash
        user_states[call.from_user.id] = {
            'state': UserState.SELECT_ROOM,
            'dormitory_id': dorm_id,
            'order_mode': True
        }
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtma yotoqxona xatosi: {e}")

def back_to_menu_callback(call):
    """Asosiy menyuga qaytish"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        show_main_menu_text = f"""🍽️ *Xush kelibsiz, {user.get_display_name()}!*

Yotoqxonalarga yetkazib berish botiga qaytgan kunlar bilan!

🥘 Mazali taomlar
🏠 Yotoqxonalarga yetkazib berish
🚚 Tez yetkazib berish
⏰ Aniq yetkazib berish vaqti
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
        
        # Inline keyboardni o'chirish
        safe_edit_message(call.message.chat.id, call.message.message_id, show_main_menu_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Asosiy menyu xatosi: {e}")

def clear_cart_callback(call):
    """Savatchani tozalash"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        Cart.objects.filter(user=user).delete()
        
        text = "🗑️ *Savatcha tozalandi*\n\nYangi mahsulotlar qo'shishingiz mumkin."
        
        markup = types.InlineKeyboardMarkup()
        menu_btn = types.InlineKeyboardButton('🍽️ Menyuga o\'tish', callback_data='show_menu')
        back_btn = types.InlineKeyboardButton('🔙 Asosiy menyu', callback_data='back_to_menu')
        markup.add(menu_btn)
        markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
        bot.answer_callback_query(call.id, "✅ Savatcha tozalandi")
        
    except Exception as e:
        logger.error(f"Savatcha tozalash xatosi: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

def view_cart_callback(call):
    """Savatchani ko'rish"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            text = "🛒 *Savatchangiz bo'sh*\n\nMahsulotlar qo'shish uchun menyuga o'ting."
            markup = types.InlineKeyboardMarkup()
            menu_btn = types.InlineKeyboardButton('🍽️ Menyu', callback_data='show_menu')
            markup.add(menu_btn)
        else:
            total = sum(item.get_total_price() for item in cart_items)
            text = "🛒 *Savatchangiz:*\n\n"
            
            for item in cart_items:
                text += f"• {item.product.name}\n"
                text += f"  {item.quantity} x {item.product.price:,.0f} = {item.get_total_price():,.0f} so'm\n\n"
            
            text += f"💰 *Jami: {total:,.0f} so'm*"
            
            markup = types.InlineKeyboardMarkup()
            order_btn = types.InlineKeyboardButton('📋 Buyurtma berish', callback_data='create_order')
            clear_btn = types.InlineKeyboardButton('🗑️ Tozalash', callback_data='clear_cart')
            menu_btn = types.InlineKeyboardButton('🍽️ Menyu', callback_data='show_menu')
            markup.add(order_btn)
            markup.add(clear_btn)
            markup.add(menu_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Savatcha ko'rish xatosi: {e}")

def show_menu_callback(call):
    """Menyuni ko'rsatish"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            text = "❌ Kategoriyalar mavjud emas!"
            markup = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton('🔙 Asosiy menyu', callback_data='back_to_menu')
            markup.add(back_btn)
        else:
            text = "🍽️ *Kategoriyani tanlang:*\n\n"
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            for category in categories:
                products_count = Product.objects.filter(category=category, is_available=True).count()
                btn_text = f"{category.name} ({products_count} ta)"
                btn = types.InlineKeyboardButton(btn_text, callback_data=f'cat_{category.id}')
                markup.add(btn)
                text += f"• {category.name} - {products_count} ta mahsulot\n"
            
            back_btn = types.InlineKeyboardButton('🔙 Asosiy menyu', callback_data='back_to_menu')
            markup.add(back_btn)
        
        safe_edit_message(call.message.chat.id, call.message.message_id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Menu ko'rsatish xatosi: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Barcha boshqa xabarlar"""
    if message.from_user.id not in user_states:
        if not is_user_registered(message.from_user.id):
            safe_send_message(message.chat.id, "👋 Xush kelibsiz! Ro'yxatdan o'tish uchun /start buyrug'ini bosing.")
        else:
            safe_send_message(message.chat.id, "❓ Kerakli tugmani tanlang yoki /start buyrug'ini bosing.")

def main():
    """Asosiy bot funksiya"""
    global bot  # Global o'zgaruvchi
    
    print("🤖 Registratsiya tizimi bilan Telegram bot ishga tushmoqda...")
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

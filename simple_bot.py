#!/usr/bin/env python
"""
Oddiy Telegram bot - faqat polling bilan
"""
import os
import sys
import django
from pathlib import Path

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

import telebot
from telebot import types
from bot.models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem
from django.conf import settings

# Bot tokenini olish
BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"
bot = telebot.TeleBot(BOT_TOKEN)

# Global o'zgaruvchilar
user_states = {}

class UserState:
    MENU = "menu"
    ORDER_ADDRESS = "order_address" 
    ORDER_PHONE = "order_phone"

def get_user_state(user_id):
    return user_states.get(user_id, {}).get("state", UserState.MENU)

def set_user_state(user_id, state, data=None):
    user_states[user_id] = {"state": state, "data": data or {}}

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start buyrug'i"""
    user_data = message.from_user
    
    try:
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
            telegram_user.username = user_data.username or ''
            telegram_user.first_name = user_data.first_name or ''
            telegram_user.last_name = user_data.last_name or ''
            telegram_user.save()
        
        set_user_state(message.from_user.id, UserState.MENU)
        send_main_menu(message.chat.id, telegram_user.first_name)
        
    except Exception as e:
        print(f"Start xatosi: {e}")
        bot.send_message(message.chat.id, "Botda xatolik yuz berdi. Qayta urinib ko'ring.")

def send_main_menu(chat_id, first_name=""):
    """Asosiy menyu"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🍽️ Menyu')
    btn2 = types.KeyboardButton('🛒 Savatcha')
    btn3 = types.KeyboardButton('📋 Buyurtmalarim')
    btn4 = types.KeyboardButton('📞 Aloqa')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    welcome_text = f"""🍽️ *Salom {first_name}!*

Yetkazib berish botiga xush kelibsiz!

🥘 Mazali taomlar
🚚 Tez yetkazib berish  
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🍽️ Menyu')
def menu_handler(message):
    """Menyu bo'limi"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        print(f"Kategoriyalar soni: {categories.count()}")
        
        if not categories.exists():
            # Kategoriya yo'q bo'lsa, test kategoriya yaratamiz
            Category.objects.create(name="🍕 Test Pizza", description="Test kategoriya", is_active=True)
            categories = Category.objects.filter(is_active=True)
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        for category in categories:
            btn = types.InlineKeyboardButton(
                f"{category.name}", 
                callback_data=f'cat_{category.id}'
            )
            markup.add(btn)
        
        bot.send_message(
            message.chat.id, 
            "🍽️ *Kategoriyani tanlang:*", 
            reply_markup=markup, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Menu xatosi: {e}")
        bot.send_message(message.chat.id, f"Menyu yuklashda xatolik: {e}")

@bot.message_handler(func=lambda message: message.text == '📞 Aloqa')
def contact_handler(message):
    """Aloqa bo'limi"""
    contact_text = """📞 *Aloqa ma'lumotlari:*

📱 Telefon: +998 90 123 45 67
📧 Email: info@delivery.uz  
🌐 Website: www.delivery.uz
📍 Manzil: Toshkent sh., Amir Temur ko'chasi

⏰ *Ish vaqti:*
Dushanba - Yakshanba: 09:00 - 23:00

Savollaringiz bo'lsa, biz bilan bog'laning! 😊"""
    
    bot.send_message(message.chat.id, contact_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🛒 Savatcha')
def cart_handler(message):
    """Savatcha bo'limi"""
    bot.send_message(message.chat.id, "🛒 Savatcha funksiyasi tez orada qo'shiladi!")

@bot.message_handler(func=lambda message: message.text == '📋 Buyurtmalarim')
def orders_handler(message):
    """Buyurtmalar bo'limi"""
    bot.send_message(message.chat.id, "📋 Buyurtmalar funksiyasi tez orada qo'shiladi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def category_callback(call):
    """Kategoriya tanlash"""
    try:
        category_id = int(call.data.split('_')[1])
        category = Category.objects.get(id=category_id, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            bot.answer_callback_query(call.id, "Bu kategoriyada mahsulotlar yo'q")
            return
        
        text = f"🍽️ *{category.name}*\n\nMahsulotlar:"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for product in products:
            btn = types.InlineKeyboardButton(
                f"{product.name} - {product.price:,.0f} so'm",
                callback_data=f'prod_{product.id}'
            )
            markup.add(btn)
        
        back_btn = types.InlineKeyboardButton('⬅️ Orqaga', callback_data='back_to_categories')
        markup.add(back_btn)
        
        bot.edit_message_text(
            text, 
            call.message.chat.id, 
            call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Kategoriya callback xatosi: {e}")
        bot.answer_callback_query(call.id, f"Xatolik: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Barcha boshqa xabarlar"""
    bot.send_message(message.chat.id, "Kerakli tugmani tanlang yoki /start buyrug'ini bosing")

if __name__ == "__main__":
    print("🤖 Telegram bot ishga tushmoqda...")
    print("⚠️  Avval admin paneldan kategoriya va mahsulotlar qo'shing:")
    print("🔗 http://127.0.0.1:8000/admin")
    print("👤 Login: admin")  
    print("🔑 Parol: admin123")
    print("\n⏹️ To'xtatish uchun Ctrl+C bosing")
    
    try:
        bot.infinity_polling(none_stop=True, interval=1, timeout=30)
    except KeyboardInterrupt:
        print("\n🛑 Bot to'xtatildi")
    except Exception as e:
        print(f"Bot xatosi: {e}")

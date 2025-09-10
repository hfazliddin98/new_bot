#!/usr/bin/env python
"""
Yangi Telegram bot - xatosiz versiya
"""
import os
import sys
import django
import time
from pathlib import Path

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

import telebot
from telebot import types
from bot.models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem
from decimal import Decimal

# Bot tokenini to'g'ridan-to'g'ri yozamiz
BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"
bot = telebot.TeleBot(BOT_TOKEN)

def create_sample_data():
    """Namuna ma'lumotlarni yaratish"""
    try:
        # Kategoriyalar mavjudligini tekshirish
        if Category.objects.count() == 0:
            print("📂 Kategoriyalar yaratilmoqda...")
            
            cat1 = Category.objects.create(
                name="🍕 Pizza",
                description="Mazali pizzalar",
                is_active=True
            )
            
            cat2 = Category.objects.create(
                name="🍔 Burger", 
                description="Fast food burgerlar",
                is_active=True
            )
            
            cat3 = Category.objects.create(
                name="🥤 Ichimliklar",
                description="Sovuq va issiq ichimliklar",
                is_active=True
            )
            
            # Mahsulotlar yaratish
            Product.objects.create(
                name="Pepperoni Pizza",
                description="Pepperoni bilan klassik pizza",
                price=Decimal('45000'),
                category=cat1,
                is_available=True
            )
            
            Product.objects.create(
                name="Big Burger",
                description="Katta go'sht burger",
                price=Decimal('25000'),
                category=cat2,
                is_available=True
            )
            
            Product.objects.create(
                name="Coca Cola",
                description="Sovuq ichimlik",
                price=Decimal('8000'),
                category=cat3,
                is_available=True
            )
            
            print("✅ Test ma'lumotlari yaratildi!")
        
        print(f"📂 Kategoriyalar: {Category.objects.count()}")
        print(f"🍽️ Mahsulotlar: {Product.objects.count()}")
        
    except Exception as e:
        print(f"Ma'lumot yaratishda xato: {e}")

# Global o'zgaruvchilar
user_states = {}

class UserState:
    MENU = "menu"
    ORDER_ADDRESS = "order_address"
    ORDER_PHONE = "order_phone"

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
        btn3 = types.KeyboardButton('📞 Aloqa')
        btn4 = types.KeyboardButton('📋 Test')
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        
        welcome_text = f"""🍽️ *Salom {telegram_user.first_name}!*

Yetkazib berish botiga xush kelibsiz!

🥘 Mazali taomlar
🚚 Tez yetkazib berish
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Start xatosi: {e}")
        bot.send_message(message.chat.id, f"Xatolik: {e}")

@bot.message_handler(func=lambda message: message.text == '🍽️ Menyu')
def menu_handler(message):
    """Menyu bo'limi"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            bot.send_message(message.chat.id, "❌ Kategoriyalar mavjud emas!")
            return
        
        text = "🍽️ *Kategoriyani tanlang:*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for category in categories:
            products_count = Product.objects.filter(category=category, is_available=True).count()
            btn_text = f"{category.name} ({products_count} ta)"
            btn = types.InlineKeyboardButton(btn_text, callback_data=f'cat_{category.id}')
            markup.add(btn)
            text += f"• {category.name} - {products_count} ta mahsulot\n"
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Menu xatosi: {e}")
        bot.send_message(message.chat.id, f"Menu xatosi: {e}")

@bot.message_handler(func=lambda message: message.text == '🛒 Savatcha')
def cart_handler(message):
    """Savatcha"""
    try:
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            bot.send_message(message.chat.id, "🛒 Savatchangiz bo'sh")
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
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "❌ Avval /start buyrug'ini bosing")
    except Exception as e:
        bot.send_message(message.chat.id, f"Savatcha xatosi: {e}")

@bot.message_handler(func=lambda message: message.text == '📞 Aloqa')
def contact_handler(message):
    """Aloqa"""
    contact_text = """📞 *Aloqa ma'lumotlari:*

📱 Telefon: +998 90 123 45 67
📧 Email: info@delivery.uz
📍 Manzil: Toshkent sh.

⏰ *Ish vaqti:*
09:00 - 23:00 (har kuni)"""
    
    bot.send_message(message.chat.id, contact_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '📋 Test')
def test_handler(message):
    """Test funksiya"""
    try:
        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        users_count = TelegramUser.objects.count()
        
        text = f"""📋 *Test ma'lumotlari:*

📂 Kategoriyalar: {categories_count}
🍽️ Mahsulotlar: {products_count}
👥 Foydalanuvchilar: {users_count}

🔗 Admin panel: http://127.0.0.1:8000/admin"""
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Test xatosi: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
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
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id, 
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"Mahsulot xatosi: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
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
        bot.answer_callback_query(call.id, f"Xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
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
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"Xatolik: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Barcha boshqa xabarlar"""
    bot.send_message(message.chat.id, "❓ Kerakli tugmani tanlang yoki /start buyrug'ini bosing")

if __name__ == "__main__":
    print("🤖 Telegram yetkazib berish boti ishga tushmoqda...")
    print("🔗 Admin panel: http://127.0.0.1:8000/admin")
    print("⏹️ To'xtatish uchun Ctrl+C bosing")
    
    # Test ma'lumotlarni yaratish
    create_sample_data()
    
    # Bot ishga tushirish
    try:
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        bot.infinity_polling(none_stop=True, interval=1, timeout=30)
    except KeyboardInterrupt:
        print("\n🛑 Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Bot xatosi: {e}")
        print("🔄 10 soniyadan so'ng qayta urinish...")
        time.sleep(10)
        bot.infinity_polling(none_stop=True, interval=1, timeout=30)

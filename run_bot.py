#!/usr/bin/env python
"""
Telegram bot va Django serverni parallel ishga tushiruvchi skript
"""
import os
import sys
import django
import threading
import time
from pathlib import Path

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from django.core.management import execute_from_command_line
import telebot
from telebot import types
from bot.models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem
from django.conf import settings

# Bot instanceni yaratish
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

# Global o'zgaruvchilar
user_states = {}  # Foydalanuvchi holatlarini saqlash

class UserState:
    MENU = "menu"
    CATEGORY = "category" 
    PRODUCT = "product"
    CART = "cart"
    ORDER_ADDRESS = "order_address"
    ORDER_PHONE = "order_phone"
    ORDER_CONFIRM = "order_confirm"

def get_user_state(user_id):
    return user_states.get(user_id, UserState.MENU)

def set_user_state(user_id, state, data=None):
    user_states[user_id] = {"state": state, "data": data or {}}

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start buyrug'i"""
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
        telegram_user.username = user_data.username or ''
        telegram_user.first_name = user_data.first_name or ''
        telegram_user.last_name = user_data.last_name or ''
        telegram_user.save()
    
    set_user_state(message.from_user.id, UserState.MENU)
    send_main_menu(message.chat.id, telegram_user.first_name)

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
    categories = Category.objects.filter(is_active=True)
    
    if not categories.exists():
        bot.send_message(message.chat.id, "Hozircha kategoriyalar mavjud emas 😔")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for category in categories:
        btn = types.InlineKeyboardButton(
            f"🍽️ {category.name}", 
            callback_data=f'cat_{category.id}'
        )
        markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        "🍽️ *Kategoriyani tanlang:*", 
        reply_markup=markup, 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == '🛒 Savatcha')
def cart_handler(message):
    """Savatcha bo'limi"""
    try:
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            bot.send_message(message.chat.id, "🛒 Savatchangiz bo'sh")
            return
        
        total = sum(item.get_total_price() for item in cart_items)
        cart_text = "🛒 *Savatchangiz:*\n\n"
        
        for item in cart_items:
            cart_text += f"• *{item.product.name}*\n"
            cart_text += f"  {item.quantity} x {item.product.price:,.0f} = {item.get_total_price():,.0f} so'm\n\n"
        
        cart_text += f"💰 *Jami: {total:,.0f} so'm*"
        
        markup = types.InlineKeyboardMarkup()
        order_btn = types.InlineKeyboardButton('📋 Buyurtma berish', callback_data='create_order')
        clear_btn = types.InlineKeyboardButton('🗑️ Tozalash', callback_data='clear_cart')
        markup.add(order_btn)
        markup.add(clear_btn)
        
        bot.send_message(message.chat.id, cart_text, reply_markup=markup, parse_mode='Markdown')
        
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "Iltimos /start buyrug'ini bosing")

@bot.message_handler(func=lambda message: message.text == '📋 Buyurtmalarim')
def orders_handler(message):
    """Buyurtmalar bo'limi"""
    try:
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        
        if not orders.exists():
            bot.send_message(message.chat.id, "📋 Sizda hali buyurtmalar yo'q")
            return
        
        orders_text = "📋 *Sizning buyurtmalaringiz:*\n\n"
        
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅', 
            'preparing': '👨‍🍳',
            'delivering': '🚚',
            'completed': '✅',
            'cancelled': '❌'
        }
        
        for order in orders:
            emoji = status_emoji.get(order.status, '❓')
            orders_text += f"{emoji} *#{order.id}* - {order.total_amount:,.0f} so'm\n"
            orders_text += f"Holat: {order.get_status_display()}\n"
            orders_text += f"Vaqt: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        bot.send_message(message.chat.id, orders_text, parse_mode='Markdown')
        
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "Iltimos /start buyrug'ini bosing")

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

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def category_callback(call):
    """Kategoriya tanlash"""
    category_id = int(call.data.split('_')[1])
    
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            bot.answer_callback_query(call.id, "Bu kategoriyada mahsulotlar yo'q")
            return
        
        text = f"🍽️ *{category.name}*\n\nMahsulotlarni tanlang:"
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
        
    except Category.DoesNotExist:
        bot.answer_callback_query(call.id, "Kategoriya topilmadi")

@bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
def product_callback(call):
    """Mahsulot tanlash"""
    product_id = int(call.data.split('_')[1])
    
    try:
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
        
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, "Mahsulot topilmadi")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart_callback(call):
    """Savatchaga qo'shish"""
    product_id = int(call.data.split('_')[1])
    
    try:
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
            f"✅ {product.name} savatchaga qo'shildi!"
        )
        
    except (TelegramUser.DoesNotExist, Product.DoesNotExist):
        bot.answer_callback_query(call.id, "Xatolik yuz berdi")

@bot.callback_query_handler(func=lambda call: call.data == 'create_order')
def create_order_callback(call):
    """Buyurtma yaratishni boshlash"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            bot.answer_callback_query(call.id, "Savatchangiz bo'sh!")
            return
        
        set_user_state(call.from_user.id, UserState.ORDER_ADDRESS)
        
        bot.send_message(
            call.message.chat.id,
            "📍 *Yetkazib berish manzilini kiriting:*\n\nMasalan: Toshkent sh., Chilonzor t., 12-kv",
            parse_mode='Markdown'
        )
        
    except TelegramUser.DoesNotExist:
        bot.answer_callback_query(call.id, "Iltimos /start buyrug'ini bosing")

@bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')
def clear_cart_callback(call):
    """Savatchani tozalash"""
    try:
        user = TelegramUser.objects.get(user_id=call.from_user.id)
        Cart.objects.filter(user=user).delete()
        
        bot.answer_callback_query(call.id, "🗑️ Savatcha tozalandi!")
        bot.edit_message_text(
            "🛒 Savatchangiz bo'sh",
            call.message.chat.id,
            call.message.message_id
        )
        
    except TelegramUser.DoesNotExist:
        bot.answer_callback_query(call.id, "Iltimos /start buyrug'ini bosing")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    """Matn xabarlarini qayta ishlash"""
    user_state_data = user_states.get(message.from_user.id, {})
    current_state = user_state_data.get("state", UserState.MENU)
    
    try:
        user = TelegramUser.objects.get(user_id=message.from_user.id)
        
        # Xabarni saqlash
        Message.objects.create(
            telegram_user=user,
            message_text=message.text,
            message_type='text'
        )
        
        if current_state == UserState.ORDER_ADDRESS:
            # Manzilni saqlash
            set_user_state(message.from_user.id, UserState.ORDER_PHONE, {"address": message.text})
            
            bot.send_message(
                message.chat.id,
                "📱 *Telefon raqamingizni kiriting:*\n\nMasalan: +998901234567",
                parse_mode='Markdown'
            )
            
        elif current_state == UserState.ORDER_PHONE:
            # Telefon raqamni saqlash va buyurtmani yaratish
            address = user_state_data.get("data", {}).get("address", "")
            phone = message.text
            
            # Buyurtmani yaratish
            cart_items = Cart.objects.filter(user=user)
            if not cart_items.exists():
                bot.send_message(message.chat.id, "Savatchangiz bo'sh!")
                return
            
            total_amount = sum(item.get_total_price() for item in cart_items)
            delivery_fee = 10000  # 10,000 so'm yetkazib berish haqi
            
            order = Order.objects.create(
                user=user,
                delivery_address=address,
                phone_number=phone,
                total_amount=total_amount + delivery_fee,
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
            
            # Buyurtma tasdiqini yuborish
            order_text = f"""✅ *Buyurtma qabul qilindi!*

🆔 Buyurtma raqami: #{order.id}
📍 Manzil: {address}
📱 Telefon: {phone}
💰 Mahsulotlar: {total_amount:,.0f} so'm
🚚 Yetkazib berish: {delivery_fee:,.0f} so'm
💳 *Jami: {order.total_amount:,.0f} so'm*

⏰ Buyurtmangiz 30-45 daqiqada yetkaziladi!
📞 Savol bo'lsa: +998901234567"""
            
            bot.send_message(message.chat.id, order_text, parse_mode='Markdown')
            
            # Holatni qayta tiklash
            set_user_state(message.from_user.id, UserState.MENU)
            
            # Asosiy menyuga qaytarish
            send_main_menu(message.chat.id, user.first_name)
            
        else:
            # Noma'lum xabar
            bot.send_message(
                message.chat.id, 
                "Kerakli tugmani tanlang yoki /start buyrug'ini bosing"
            )
            
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "Iltimos /start buyrug'ini bosing")

def run_django_server():
    """Django serverni ishga tushirish"""
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

def run_telegram_bot():
    """Telegram botni ishga tushirish"""
    print("🤖 Telegram bot ishga tushmoqda...")
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Bot xatosi: {e}")
        time.sleep(5)
        run_telegram_bot()

if __name__ == "__main__":
    print("🚀 Django + Telegram Bot ishga tushmoqda...")
    
    # Django serverni alohida threadda ishga tushirish
    django_thread = threading.Thread(target=run_django_server, daemon=True)
    django_thread.start()
    
    print("🌐 Django server: http://127.0.0.1:8000")
    print("📊 Admin panel: http://127.0.0.1:8000/admin")
    print("📈 Statistika: http://127.0.0.1:8000/bot/stats")
    
    # Telegram botni asosiy threadda ishga tushirish
    time.sleep(3)  # Django serverning ishga tushishini kutish
    run_telegram_bot()

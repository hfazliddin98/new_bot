import telebot
from telebot import types
from django.conf import settings
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem

# Bot instanceni yaratish
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

def handle_telegram_update(update_data):
    """Telegram updateni qayta ishlash"""
    try:
        if 'message' in update_data:
            message_data = update_data['message']
            user_data = message_data['from']
            
            # Foydalanuvchini saqlash yoki yangilash
            telegram_user, created = TelegramUser.objects.get_or_create(
                user_id=user_data['id'],
                defaults={
                    'username': user_data.get('username', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                }
            )
            
            # Agar foydalanuvchi mavjud bo'lsa, ma'lumotlarni yangilash
            if not created:
                telegram_user.username = user_data.get('username', '')
                telegram_user.first_name = user_data.get('first_name', '')
                telegram_user.last_name = user_data.get('last_name', '')
                telegram_user.save()
            
            # Xabarni saqlash
            if 'text' in message_data:
                Message.objects.create(
                    telegram_user=telegram_user,
                    message_text=message_data['text'],
                    message_type='text'
                )
                
                # Bot javobini yuborish
                send_bot_response(message_data, telegram_user)
                
    except Exception as e:
        print(f"Update qayta ishlashda xato: {e}")

def send_bot_response(message_data, telegram_user):
    """Bot javobini yuborish"""
    chat_id = message_data['chat']['id']
    text = message_data.get('text', '')
    
    try:
        if text == '/start':
            send_welcome_message(chat_id)
        elif text == '🍽️ Menyu':
            send_menu_categories(chat_id)
        elif text == '� Savatcha':
            send_cart(chat_id, telegram_user)
        elif text == '� Buyurtmalarim':
            send_user_orders(chat_id, telegram_user)
        elif text == '📞 Aloqa':
            send_contact_info(chat_id)
        elif text == '⚙️ Sozlamalar':
            send_settings_menu(chat_id)
        elif text.startswith('� Telefon raqam:'):
            # Telefon raqamni saqlash
            phone = text.replace('📱 Telefon raqam:', '').strip()
            telegram_user.phone_number = phone
            telegram_user.save()
            bot.send_message(chat_id, "Telefon raqamingiz saqlandi! ✅")
        else:
            # Kategoriya yoki mahsulot tanlash
            handle_menu_selection(chat_id, text, telegram_user)
            
    except Exception as e:
        print(f"Javob yuborishda xato: {e}")

def send_welcome_message(chat_id):
    """Xush kelibsiz xabarini yuborish"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🍽️ Menyu')
    btn2 = types.KeyboardButton('🛒 Savatcha')
    btn3 = types.KeyboardButton('📋 Buyurtmalarim')
    btn4 = types.KeyboardButton('📞 Aloqa')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    welcome_text = """🍽️ *Yetkazib berish botiga xush kelibsiz!*

🥘 Mazali taomlar
🚚 Tez yetkazib berish
� Qulay to'lov

Kerakli bo'limni tanlang:"""
    
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

def send_menu_categories(chat_id):
    """Kategoriyalarni yuborish"""
    categories = Category.objects.filter(is_active=True)
    
    if not categories:
        bot.send_message(chat_id, "Hozircha kategoriyalar mavjud emas 😔")
        return
    
    markup = types.InlineKeyboardMarkup()
    for category in categories:
        btn = types.InlineKeyboardButton(category.name, callback_data=f'cat_{category.id}')
        markup.add(btn)
    
    bot.send_message(chat_id, "🍽️ *Kategoriyani tanlang:*", reply_markup=markup, parse_mode='Markdown')

def send_cart(chat_id, telegram_user):
    """Savatchani yuborish"""
    cart_items = Cart.objects.filter(user=telegram_user)
    
    if not cart_items:
        bot.send_message(chat_id, "🛒 Savatchangiz bo'sh")
        return
    
    total = sum(item.get_total_price() for item in cart_items)
    cart_text = "🛒 *Savatchangiz:*\n\n"
    
    for item in cart_items:
        cart_text += f"• {item.product.name}\n"
        cart_text += f"  {item.quantity} x {item.product.price} = {item.get_total_price()} so'm\n\n"
    
    cart_text += f"💰 *Jami: {total} so'm*"
    
    markup = types.InlineKeyboardMarkup()
    order_btn = types.InlineKeyboardButton('� Buyurtma berish', callback_data='create_order')
    clear_btn = types.InlineKeyboardButton('🗑️ Savatchani tozalash', callback_data='clear_cart')
    markup.add(order_btn)
    markup.add(clear_btn)
    
    bot.send_message(chat_id, cart_text, reply_markup=markup, parse_mode='Markdown')

def send_user_orders(chat_id, telegram_user):
    """Foydalanuvchi buyurtmalarini yuborish"""
    orders = Order.objects.filter(user=telegram_user)[:5]  # So'nggi 5 ta buyurtma
    
    if not orders:
        bot.send_message(chat_id, "📋 Sizda hali buyurtmalar yo'q")
        return
    
    orders_text = "📋 *Sizning buyurtmalaringiz:*\n\n"
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'preparing': '👨‍🍳',
            'delivering': '🚚',
            'completed': '✅',
            'cancelled': '❌'
        }
        
        orders_text += f"{status_emoji.get(order.status, '❓')} *#{order.id}* - {order.total_amount} so'm\n"
        orders_text += f"Holat: {order.get_status_display()}\n"
        orders_text += f"Vaqt: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    bot.send_message(chat_id, orders_text, parse_mode='Markdown')

def send_contact_info(chat_id):
    """Aloqa ma'lumotlarini yuborish"""
    contact_text = """📞 *Aloqa ma'lumotlari:*

📱 Telefon: +998 90 123 45 67
📧 Email: info@delivery.uz
🌐 Website: www.delivery.uz
📍 Manzil: Toshkent sh., Amir Temur ko'chasi

⏰ *Ish vaqti:*
Dushanba - Yakshanba: 09:00 - 23:00

Savollaringiz bo'lsa, biz bilan bog'laning! �"""
    
    # Telefon raqam so'rash tugmasi
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton('📱 Telefon raqamni yuborish', request_contact=True)
    markup.add(contact_btn)
    
    bot.send_message(chat_id, contact_text, parse_mode='Markdown')
    bot.send_message(chat_id, "Telefon raqamingizni yuboring:", reply_markup=markup)

def send_settings_menu(chat_id):
    """Sozlamalar menyusini yuborish"""
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🗣️ Tilni o\'zgartirish', callback_data='lang')
    btn2 = types.InlineKeyboardButton('🔔 Bildirishnomalar', callback_data='notif')
    btn3 = types.InlineKeyboardButton('📱 Telefon raqam', callback_data='phone')
    inline_markup.add(btn1)
    inline_markup.add(btn2)
    inline_markup.add(btn3)
    
    bot.send_message(chat_id, "⚙️ Sozlamalar:", reply_markup=inline_markup)

def handle_menu_selection(chat_id, text, telegram_user):
    """Menyu tanlashni qayta ishlash"""
    # Bu yerda kategoriya yoki mahsulot tanlanishini qayta ishlaymiz
    bot.send_message(chat_id, f"Siz tanladingiz: {text}\nTez orada bu funksiya qo'shiladi! 🔄")

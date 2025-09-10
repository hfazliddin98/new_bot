import telebot
from telebot import types
from django.conf import settings
from .models import TelegramUser, Message

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
                send_bot_response(message_data)
                
    except Exception as e:
        print(f"Update qayta ishlashda xato: {e}")

def send_bot_response(message_data):
    """Bot javobini yuborish"""
    chat_id = message_data['chat']['id']
    text = message_data.get('text', '')
    
    try:
        if text == '/start':
            send_welcome_message(chat_id)
        elif text == '📊 Ma\'lumot':
            bot.send_message(chat_id, "Bu bot haqida ma'lumot:\n🤖 Django + Telegram bot\n📅 Yaratilgan: 2025\n👨‍💻 Dasturchi: Python + Django")
        elif text == '🔍 Qidiruv':
            bot.send_message(chat_id, "Qidiruv funksiyasi tez orada qo'shiladi! 🔍")
        elif text == '⚙️ Sozlamalar':
            send_settings_menu(chat_id)
        elif text == '📞 Aloqa':
            bot.send_message(chat_id, "Aloqa uchun:\n📧 Email: admin@example.com\n📱 Telegram: @admin")
        else:
            bot.send_message(chat_id, f"Siz yozdingiz: {text}\nKerakli tugmani tanlang yoki /start bosing!")
            
    except Exception as e:
        print(f"Javob yuborishda xato: {e}")

def send_welcome_message(chat_id):
    """Xush kelibsiz xabarini yuborish"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 Ma\'lumot')
    btn2 = types.KeyboardButton('🔍 Qidiruv')
    btn3 = types.KeyboardButton('⚙️ Sozlamalar')
    btn4 = types.KeyboardButton('📞 Aloqa')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.send_message(chat_id, "Salom! Django + Telegram botga xush kelibsiz! 👋\nKerakli tugmani tanlang:", reply_markup=markup)

def send_settings_menu(chat_id):
    """Sozlamalar menyusini yuborish"""
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Tilni o\'zgartirish', callback_data='lang')
    btn2 = types.InlineKeyboardButton('Bildirishnomalar', callback_data='notif')
    inline_markup.add(btn1)
    inline_markup.add(btn2)
    
    bot.send_message(chat_id, "Sozlamalar:", reply_markup=inline_markup)

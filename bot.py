import telebot
import os
from telebot import types

# Bot tokenlarini bu yerda belgilang
TELEGRAM_BOT_TOKEN = '7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q'

# Environment o'zgaruvchisidan tokenni olish
token = os.getenv('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN)
bot = telebot.TeleBot(token)

# /start buyrug'i uchun
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 Ma\'lumot')
    btn2 = types.KeyboardButton('🔍 Qidiruv')
    btn3 = types.KeyboardButton('⚙️ Sozlamalar')
    btn4 = types.KeyboardButton('📞 Aloqa')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.send_message(message.chat.id, "Salom! Botga xush kelibsiz! 👋\nKerakli tugmani tanlang:", reply_markup=markup)

# Tugmalar uchun javoblar
@bot.message_handler(func=lambda message: message.text == '📊 Ma\'lumot')
def info_handler(message):
    bot.send_message(message.chat.id, "Bu bot haqida ma'lumot:\n🤖 Telegram bot\n📅 Yaratilgan: 2025\n👨‍💻 Dasturchi: Python")

@bot.message_handler(func=lambda message: message.text == '🔍 Qidiruv')
def search_handler(message):
    bot.send_message(message.chat.id, "Qidiruv funksiyasi tez orada qo'shiladi! 🔍")

@bot.message_handler(func=lambda message: message.text == '⚙️ Sozlamalar')
def settings_handler(message):
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Tilni o\'zgartirish', callback_data='lang')
    btn2 = types.InlineKeyboardButton('Bildirishnomalar', callback_data='notif')
    inline_markup.add(btn1)
    inline_markup.add(btn2)
    
    bot.send_message(message.chat.id, "Sozlamalar:", reply_markup=inline_markup)

@bot.message_handler(func=lambda message: message.text == '📞 Aloqa')
def contact_handler(message):
    bot.send_message(message.chat.id, "Aloqa uchun:\n📧 Email: admin@example.com\n📱 Telegram: @admin")

# Inline tugmalar uchun callback
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'lang':
        bot.answer_callback_query(call.id, "Til o'zgartirish funksiyasi!")
    elif call.data == 'notif':
        bot.answer_callback_query(call.id, "Bildirishnomalar sozlandi!")

# Boshqa barcha xabarlar uchun
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Siz yozdingiz: {message.text}\nKerakli tugmani tanlang yoki /start bosing!")

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)

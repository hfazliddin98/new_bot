#!/usr/bin/env python
"""
Django management command - Telegram bot ishga tushirish
"""
import os
import time
import logging
import requests
import re
import threading
from decimal import Decimal
from datetime import timedelta

import telebot
from telebot import types
from django.core.management.base import BaseCommand
from django.utils import timezone
from bot.models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, Dormitory

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

# Bot token
BOT_TOKEN = "7908094134:AAHhj28h-QmV8hqEqOZAUnU9ebXBEwwKuA0"

# Global o'zgaruvchilar
user_states = {}

class UserState:
    # Registratsiya
    REGISTRATION_NAME = "registration_name"
    REGISTRATION_AGE = "registration_age"
    REGISTRATION_PHONE = "registration_phone"
    REGISTRATION_ROOM = "registration_room"
    
    # Asosiy funksiyalar
    MENU = "menu"
    SELECT_DORMITORY = "select_dormitory"
    SELECT_ROOM = "select_room"
    ORDER_ADDRESS = "order_address"
    ORDER_PHONE = "order_phone"
    ORDER_NOTES = "order_notes"

class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def create_bot_instance(self):
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

    def safe_send_message(self, bot, chat_id, text, **kwargs):
        """Xavfsiz xabar yuborish"""
        try:
            return bot.send_message(chat_id, text, **kwargs)
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")
            return None

    def safe_edit_message(self, bot, chat_id, message_id, text, **kwargs):
        """Xavfsiz xabar tahrirlash"""
        try:
            return bot.edit_message_text(text, chat_id, message_id, **kwargs)
        except Exception as e:
            logger.error(f"Xabar tahrirlashda xatolik: {e}")
            return None

    def is_user_registered(self, user_id):
        """Foydalanuvchi ro'yxatdan o'tganligini tekshirish"""
        try:
            user = TelegramUser.objects.get(user_id=user_id)
            return user.is_registered
        except TelegramUser.DoesNotExist:
            return False

    def create_main_menu(self):
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

    def start_command(self, bot, message):
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
                self.start_registration(bot, message, telegram_user)
            else:
                self.show_main_menu(bot, message, telegram_user)
            
            logger.info(f"Start buyrug'i: {telegram_user.get_display_name()}")
            
        except Exception as e:
            logger.error(f"Start xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Xatolik yuz berdi. Qaytadan /start bosing.")

    def start_registration(self, bot, message, telegram_user):
        """Registratsiyani boshlash"""
        try:
            welcome_text = f"""👋 *Salom {telegram_user.first_name or 'Foydalanuvchi'}!*

🍽️ Yotoqxonalarga yetkazib berish botiga xush kelibsiz!

📝 Xizmatimizdan foydalanish uchun iltimos qisqa ro'yxatdan o'ting.

👤 *1-qadam:*
To'liq ismingizni kiriting (Ism Familiya):

*Masalan:* Aziz Karimov"""
            
            self.safe_send_message(bot, message.chat.id, welcome_text, parse_mode='Markdown')
            
            # Foydalanuvchi holatini saqlash
            user_states[message.from_user.id] = {
                'state': UserState.REGISTRATION_NAME,
                'user_obj': telegram_user
            }
            
        except Exception as e:
            logger.error(f"Registratsiya boshlash xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Registratsiyada xatolik. Qaytadan /start bosing.")

    def show_main_menu(self, bot, message, telegram_user):
        """Asosiy menyuni ko'rsatish"""
        try:
            markup = self.create_main_menu()
            
            welcome_text = f"""🍽️ *Xush kelibsiz, {telegram_user.get_display_name()}!*

Yotoqxonalarga yetkazib berish botiga qaytgan kunlar bilan!

🥘 Mazali taomlar
🏠 Yotoqxonalarga yetkazib berish  
🚚 Tez yetkazib berish
⏰ Aniq yetkazib berish vaqti
💳 Qulay to'lov

Kerakli bo'limni tanlang:"""
            
            self.safe_send_message(bot, message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Asosiy menyu xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Menyu yuklanmadi. Qaytadan /start bosing.")

    def handle_user_input(self, bot, message):
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
                    self.safe_send_message(bot, message.chat.id, "❌ Ism noto'g'ri. Iltimos, to'liq ismingizni kiriting (2-100 belgi):")
                    return
                
                # Ismni saqlash
                user_states[user_id]['full_name'] = full_name
                user_states[user_id]['state'] = UserState.REGISTRATION_AGE
                
                text = f"✅ *Ism saqlandi: {full_name}*\n\n"
                text += "🎂 *2-qadam:*\n"
                text += "Yoshingizni kiriting (12-100):\n\n"
                text += "*Masalan:* 20"
                
                self.safe_send_message(bot, message.chat.id, text, parse_mode='Markdown')
            
            elif state_data['state'] == UserState.REGISTRATION_AGE:
                try:
                    age = int(message.text.strip())
                    
                    if age < 12 or age > 100:
                        self.safe_send_message(bot, message.chat.id, "❌ Yosh noto'g'ri. 12-100 orasida kiriting:")
                        return
                    
                    # Yoshni saqlash
                    user_states[user_id]['age'] = age
                    user_states[user_id]['state'] = UserState.REGISTRATION_PHONE
                    
                    text = f"✅ *Yosh saqlandi: {age}*\n\n"
                    text += "📞 *3-qadam:*\n"
                    text += "Telefon raqamingizni kiriting:\n\n"
                    text += "*Format:* +998901234567 yoki 901234567"
                    
                    # Telefon raqam tugmasini qo'shish
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                    phone_btn = types.KeyboardButton('📞 Telefon raqamni yuborish', request_contact=True)
                    markup.add(phone_btn)
                    
                    self.safe_send_message(bot, message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
                    
                except ValueError:
                    self.safe_send_message(bot, message.chat.id, "❌ Noto'g'ri format. Faqat raqam kiriting:")
            
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
                        self.safe_send_message(bot, message.chat.id, "❌ Noto'g'ri telefon format. Qaytadan kiriting yoki tugmani bosing:")
                        return
                
                # Telefon saqlash va xona so'rash
                user_states[user_id]['phone'] = phone
                user_states[user_id]['state'] = UserState.REGISTRATION_ROOM
                
                # Yotoqxonalar ro'yxatini ko'rsatish
                dorms = Dormitory.objects.filter(is_active=True)
                text = f"✅ *Telefon saqlandi: {phone}*\n\n"
                text += "🏠 *4-qadam:*\n"
                text += "Yotoqxonangizni va xona raqamingizni kiriting:\n\n"
                
                if dorms.exists():
                    text += f"📍 *Yotoqxonalar:*\n"
                    for dorm in dorms:
                        text += f"• {dorm.name}\n"
                    text += "\n"
                
                text += "*Format:* Yotoqxona nomi, Xona raqami\n"
                text += "*Masalan:* 1-yotoqxona, 101\n"
                text += "*Yoki:* Pedagogika instituti, A-205"
                
                self.safe_send_message(bot, message.chat.id, text, parse_mode='Markdown')
                
            elif state_data['state'] == UserState.REGISTRATION_ROOM:
                room_info = message.text.strip()
                
                if ',' not in room_info or len(room_info) < 5:
                    self.safe_send_message(bot, message.chat.id, "❌ Noto'g'ri format. 'Yotoqxona nomi, Xona raqami' formatida kiriting:")
                    return
                
                # Yotoqxona va xona raqamini ajratish
                parts = room_info.split(',', 1)
                dorm_name = parts[0].strip()
                room_number = parts[1].strip()
                
                # Yotoqxonani topish
                dorm = None
                for d in Dormitory.objects.filter(is_active=True):
                    if dorm_name.lower() in d.name.lower() or d.name.lower() in dorm_name.lower():
                        dorm = d
                        break
                
                if not dorm:
                    self.safe_send_message(bot, message.chat.id, f"❌ '{dorm_name}' yotoqxonasi topilmadi. Ro'yxatdan to'g'ri nom tanlang:")
                    return
                
                # Registratsiyani yakunlash
                telegram_user = state_data['user_obj']
                telegram_user.full_name = state_data['full_name']
                telegram_user.age = state_data['age']
                telegram_user.phone_number = state_data['phone']
                telegram_user.dormitory = dorm
                telegram_user.room_number = room_number
                telegram_user.is_registered = True
                telegram_user.registration_date = timezone.now()
                telegram_user.save()
                
                # Holatni o'chirish
                del user_states[user_id]
                
                # Tabriklar va asosiy menyu
                text = f"🎉 *Tabriklaymiz!*\n\n"
                text += f"👤 {telegram_user.full_name}\n"
                text += f"🎂 {telegram_user.age} yosh\n"
                text += f"📞 {telegram_user.phone_number}\n"
                text += f"🏠 {dorm.name}\n"
                text += f"🚪 Xona: {room_number}\n\n"
                text += "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                text += "Endi barcha xizmatlardan foydalanishingiz mumkin."
                
                markup = self.create_main_menu()
                self.safe_send_message(bot, message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
                
                logger.info(f"Yangi foydalanuvchi ro'yxatdan o'tdi: {telegram_user.full_name} - {dorm.name}, {room_number}")
                
        except Exception as e:
            logger.error(f"Foydalanuvchi kiritma xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]

    def profile_handler(self, bot, message):
        """Profil ma'lumotlari"""
        try:
            if not self.is_user_registered(message.from_user.id):
                self.safe_send_message(bot, message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
                return
            
            user = TelegramUser.objects.get(user_id=message.from_user.id)
            
            text = f"""👤 *Profil ma'lumotlari:*

👤 To'liq ism: {user.full_name or 'Kiritilmagan'}
🎂 Yosh: {user.age or 'Kiritilmagan'}
📞 Telefon: {user.phone_number or 'Kiritilmagan'}
🏠 Yotoqxona: {user.dormitory.name if user.dormitory else 'Kiritilmagan'}
🚪 Xona: {user.room_number or 'Kiritilmagan'}
📱 Username: @{user.username or 'Yo\'q'}
📅 Ro'yxatdan o'tgan: {user.registration_date.strftime('%d.%m.%Y %H:%M') if user.registration_date else 'Noma\'lum'}
🛒 Buyurtmalar soni: {Order.objects.filter(user=user).count()}

📝 Ma'lumotlarni yangilash uchun /start buyrug'ini bosing."""
            
            self.safe_send_message(bot, message.chat.id, text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Profil xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Profil ma'lumotini yuklab bo'lmadi.")

    def menu_handler(self, bot, message):
        """Menyu bo'limi"""
        try:
            if not self.is_user_registered(message.from_user.id):
                self.safe_send_message(bot, message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
                return
            
            categories = Category.objects.filter(is_active=True)
            
            if not categories.exists():
                self.safe_send_message(bot, message.chat.id, "❌ Kategoriyalar mavjud emas!")
                return
            
            text = "🍽️ *Kategoriyani tanlang:*\n\n"
            
            for category in categories:
                products_count = Product.objects.filter(category=category, is_available=True).count()
                text += f"• {category.name} - {products_count} ta mahsulot\n"
            
            self.safe_send_message(bot, message.chat.id, text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Menu xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Menyu ma'lumotini yuklab bo'lmadi.")

    def working_hours_handler(self, bot, message):
        """Ish soatlari ma'lumoti"""
        try:
            if not self.is_user_registered(message.from_user.id):
                self.safe_send_message(bot, message.chat.id, "❌ Avval ro'yxatdan o'ting. /start bosing.")
                return
            
            dorms = Dormitory.objects.filter(is_active=True)
            
            if not dorms.exists():
                self.safe_send_message(bot, message.chat.id, "❌ Yotoqxonalar mavjud emas!")
                return
            
            current_time = timezone.now()
            text = "⏰ *Yetkazib berish soatlari:*\n\n"
            text += f"🕐 Hozirgi vaqt: {current_time.strftime('%H:%M')}\n\n"
            
            for dorm in dorms:
                text += f"📍 *{dorm.name}*\n"
                text += f"📧 Manzil: {dorm.address}\n"
                    text += f"💰 Yetkazib berish: {zone.delivery_fee:,.0f} so'm\n"
                    text += f"⏱️ Vaqt: {zone.delivery_time} daqiqa\n"
                else:
                    text += "❌ Hozir ishlamaydi\n"
                    next_opening = "Ertaga " + zone.working_hours_start.strftime('%H:%M')
                    text += f"🔄 Keyingi ochilish: {next_opening}\n"
                
                text += "\n"
            
            text += "📝 *Eslatma:* Buyurtma faqat ish soatlarida qabul qilinadi."
            
            self.safe_send_message(bot, message.chat.id, text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ish soatlari xatosi: {e}")
            self.safe_send_message(bot, message.chat.id, "❌ Ish soatlari ma'lumotini yuklab bo'lmadi.")

    def contact_handler(self, bot, message):
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
        
        self.safe_send_message(bot, message.chat.id, contact_text, parse_mode='Markdown')

    def handle_all_messages(self, bot, message):
        """Barcha boshqa xabarlar"""
        if message.from_user.id not in user_states:
            if not self.is_user_registered(message.from_user.id):
                self.safe_send_message(bot, message.chat.id, "👋 Xush kelibsiz! Ro'yxatdan o'tish uchun /start buyrug'ini bosing.")
            else:
                self.safe_send_message(bot, message.chat.id, "❓ Kerakli tugmani tanlang yoki /start buyrug'ini bosing.")

    def setup_handlers(self, bot):
        """Bot handlerlarini sozlash"""
        
        @bot.message_handler(commands=['start'])
        def start_handler(message):
            self.start_command(bot, message)
        
        @bot.message_handler(func=lambda message: message.text == '👤 Profil')
        def profile_handler_wrapper(message):
            self.profile_handler(bot, message)
        
        @bot.message_handler(func=lambda message: message.text == '🍽️ Menyu')
        def menu_handler_wrapper(message):
            self.menu_handler(bot, message)
        
        @bot.message_handler(func=lambda message: message.text == '⏰ Ish soatlari')
        def working_hours_handler_wrapper(message):
            self.working_hours_handler(bot, message)
        
        @bot.message_handler(func=lambda message: message.text == '📞 Aloqa')
        def contact_handler_wrapper(message):
            self.contact_handler(bot, message)
        
        @bot.message_handler(func=lambda message: message.from_user.id in user_states)
        def user_input_handler(message):
            self.handle_user_input(bot, message)
        
        @bot.message_handler(func=lambda message: True)
        def all_messages_handler(message):
            self.handle_all_messages(bot, message)

    def run_bot(self):
        """Botni ishga tushirish"""
        global user_states
        
        print("🤖 Registratsiya tizimi bilan Telegram bot ishga tushmoqda...")
        print("🔗 Admin panel: http://127.0.0.1:8000/admin")
        
        # Bot yaratish
        bot = self.create_bot_instance()
        if not bot:
            print("❌ Bot yaratilmadi!")
            return
        
        # Handlerlarni sozlash
        self.setup_handlers(bot)
        
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
                    skip_pending=True
                )
                break
                
            except KeyboardInterrupt:
                print("\n🛑 Bot to'xtatildi")
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Bot xatosi ({retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    wait_time = min(10 * retry_count, 60)
                    print(f"🔄 {wait_time} soniyadan so'ng qayta urinish...")
                    time.sleep(wait_time)
                    
                    # Bot instanceni qayta yaratish
                    bot = self.create_bot_instance()
                    if not bot:
                        print("❌ Bot qayta yaratilmadi!")
                        break
                    
                    # Handlerlarni qayta sozlash
                    self.setup_handlers(bot)
                else:
                    print("❌ Maksimal urinishlar tugadi!")
                    break

    def handle(self, *args, **options):
        """Django command handler"""
        
        def run_in_thread():
            """Bot threadda ishga tushirish"""
            try:
                self.run_bot()
            except Exception as e:
                logger.error(f"Bot thread xatosi: {e}")
        
        # Botni alohida threadda ishga tushirish
        bot_thread = threading.Thread(target=run_in_thread, daemon=True)
        bot_thread.start()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Telegram bot ishga tushdi!')
        )

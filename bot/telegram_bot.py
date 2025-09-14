#!/usr/bin/env python
"""
Django App ichida ishlaydigan Telegram bot
"""
import os
import sys
import django
import time
import logging
import requests
from pathlib import Path

# Django sozlamalarini yuklash
try:
    from django.conf import settings
    if not settings.configured:
        BASE_DIR = Path(__file__).resolve().parent.parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
        django.setup()
except Exception as e:
    print(f"Django sozlash xatosi: {e}")

import telebot
from telebot import types
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, Dormitory, OrderSession
from decimal import Decimal

# Logging sozlash
logger = logging.getLogger(__name__)

# Bot tokenini environment variable'dan olish
try:
    from django.conf import settings
    BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
except:
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7908094134:AAHhj28h-QmV8hqEqOZAUnU9ebXBEwwKuA0')

# Global bot instance
bot_instance = None

def get_bot():
    """Bot instance'ni olish yoki yaratish"""
    global bot_instance
    if bot_instance is None:
        try:
            print('🤖 Bot instance yaratilmoqda...')
            bot_instance = telebot.TeleBot(BOT_TOKEN, threaded=True)
            bot_info = bot_instance.get_me()
            print(f'✅ Bot tayyor: @{bot_info.username}')
            return bot_instance
        except Exception as e:
            print(f'❌ Bot yaratishda xatolik: {e}')
            return None
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

def show_main_menu(chat_id, user):
    """Asosiy menyuni ko'rsatish"""
    text = f"👋 Salom {user.get_display_name()}!\n\n"
    text += "🍕 Nima qilmoqchisiz?"
    
    send_safe_message(chat_id, text, get_main_menu_keyboard())

def show_menu_categories(chat_id, user):
    """Kategoriyalarni ko'rsatish"""
    try:
        categories = Category.objects.filter(is_active=True)
        
        if not categories.exists():
            send_safe_message(chat_id, "❌ Hozircha kategoriyalar mavjud emas.", get_main_menu_keyboard())
            return
        
        text = "🍕 Kategoriyalarni tanlang:"
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for category in categories:
            # Kategoriyada nechta mahsulot borligini hisoblash
            product_count = Product.objects.filter(category=category, is_available=True).count()
            
            if product_count > 0:
                markup.add(types.InlineKeyboardButton(
                    f"{category.name} ({product_count})",
                    callback_data=f"cat_{category.id}"
                ))
        
        # Orqaga qaytish tugmasi
        markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_main"))
        
        send_safe_message(chat_id, text, markup)
    except Exception as e:
        logger.error(f"Kategoriyalar ko'rsatishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def show_category_products(chat_id, user, category_id):
    """Kategoriya mahsulotlarini ko'rsatish"""
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
        
        if not products.exists():
            text = f"❌ {category.name} kategoriyasida hozircha mahsulotlar mavjud emas."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kategoriyalarga qaytish", callback_data="back_to_categories"))
            send_safe_message(chat_id, text, markup)
            return
        
        text = f"🍕 {category.name} kategoriyasi:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for product in products:
            markup.add(types.InlineKeyboardButton(
                f"🛒 {product.name} - {product.price:,} so'm",
                callback_data=f"prod_{product.id}"
            ))
        
        # Navigatsiya tugmalari
        markup.add(
            types.InlineKeyboardButton("🔙 Kategoriyalarga qaytish", callback_data="back_to_categories"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Category.DoesNotExist:
        send_safe_message(chat_id, "❌ Kategoriya topilmadi.", get_main_menu_keyboard())
    except Exception as e:
        logger.error(f"Mahsulotlar ko'rsatishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def show_product_details(chat_id, user, product_id):
    """Mahsulot tafsilotlarini ko'rsatish"""
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        
        text = f"🍕 {product.name}\n\n"
        text += f"📝 {product.description}\n\n"
        text += f"💰 Narx: {product.price:,} so'm\n"
        text += f"📂 Kategoriya: {product.category.name}"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Savatga qo'shish tugmasi
        markup.add(types.InlineKeyboardButton(
            "🛒 Savatga qo'shish",
            callback_data=f"add_to_cart_{product.id}"
        ))
        
        # Navigatsiya
        markup.add(
            types.InlineKeyboardButton("🔙 Orqaga", callback_data=f"cat_{product.category.id}"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Product.DoesNotExist:
        send_safe_message(chat_id, "❌ Mahsulot topilmadi.", get_main_menu_keyboard())
    except Exception as e:
        logger.error(f"Mahsulot tafsilotlarida xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def add_to_cart(chat_id, user, product_id):
    """Mahsulotni savatga qo'shish"""
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        
        # Savatda allaqachon bor yoki yo'qligini tekshirish
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            # Agar allaqachon savatda bo'lsa, miqdorni oshirish
            cart_item.quantity += 1
            cart_item.save()
            text = f"✅ {product.name} savatga qo'shildi!\n"
            text += f"📦 Savatingizdagi miqdor: {cart_item.quantity} ta"
        else:
            text = f"✅ {product.name} savatga qo'shildi!"
        
        # Savatdagi umumiy mahsulotlar sonini ko'rsatish
        total_items = Cart.objects.filter(user=user).count()
        text += f"\n\n🛒 Savatingizda jami: {total_items} xil mahsulot"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Yana qo'shish", callback_data=f"add_to_cart_{product.id}"),
            types.InlineKeyboardButton("🛒 Savatni ko'rish", callback_data="view_cart")
        )
        markup.add(
            types.InlineKeyboardButton("🔙 Orqaga", callback_data=f"cat_{product.category.id}"),
            types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")
        )
        
        send_safe_message(chat_id, text, markup)
        
    except Product.DoesNotExist:
        send_safe_message(chat_id, "❌ Mahsulot topilmadi.", get_main_menu_keyboard())
    except Exception as e:
        logger.error(f"Savatga qo'shishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def show_cart(chat_id, user):
    """Savatni ko'rsatish"""
    try:
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            text = "🛒 Savatingiz bo'sh\n\n"
            text += "🍕 Mahsulotlarni ko'rish uchun 'Menyu' tugmasini bosing."
            send_safe_message(chat_id, text, get_main_menu_keyboard())
            return
        
        text = "🛒 Sizning savatingiz:\n\n"
        total_price = Decimal('0')
        
        for item in cart_items:
            item_total = item.get_total_price()
            total_price += item_total
            text += f"🍕 {item.product.name}\n"
            text += f"💰 {item.product.price:,} so'm x {item.quantity} = {item_total:,} so'm\n\n"
        
        text += f"💳 Jami: {total_price:,} so'm"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Har bir mahsulot uchun boshqaruv tugmalari
        for item in cart_items:
            markup.add(
                types.InlineKeyboardButton(f"➖ {item.product.name[:15]}...", callback_data=f"decrease_{item.product.id}"),
                types.InlineKeyboardButton(f"➕ {item.product.name[:15]}...", callback_data=f"increase_{item.product.id}")
            )
        
        # Asosiy tugmalar
        markup.add(
            types.InlineKeyboardButton("🗑️ Savatni tozalash", callback_data="clear_cart"),
            types.InlineKeyboardButton("✅ Buyurtma berish", callback_data="place_order")
        )
        markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
        
        send_safe_message(chat_id, text, markup)
        
    except Exception as e:
        logger.error(f"Savatni ko'rsatishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def place_order(chat_id, user):
    """Buyurtma berish - yotoqxona tanlash"""
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        send_safe_message(chat_id, "❌ Savatingiz bo'sh! Avval mahsulot qo'shing.", get_main_menu_keyboard())
        return
    
    # To'g'ridan-to'g'ri yotoqxonalarni ko'rsatish
    show_dormitories(chat_id, user)

def show_my_orders(chat_id, user):
    """Foydalanuvchining buyurtmalarini ko'rsatish"""
    try:
        orders = Order.objects.filter(user=user).order_by('-created_at')[:10]  # So'nggi 10 ta buyurtma
        
        if not orders.exists():
            text = "📋 Sizda hali buyurtmalar yo'q\n\n"
            text += "🍕 Birinchi buyurtmangizni berish uchun 'Menyu' tugmasini bosing!"
            send_safe_message(chat_id, text, get_main_menu_keyboard())
            return
        
        text = "📋 **Sizning buyurtmalaringiz:**\n\n"
        
        for order in orders:
            # Status emoji
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅', 
                'preparing': '👨‍🍳',
                'delivering': '🚚',
                'delivered': '📦',
                'completed': '🎉',
                'cancelled': '❌'
            }.get(order.status, '📦')
            
            text += f"{status_emoji} **Buyurtma #{order.id}**\n"
            text += f"📅 {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            text += f"📍 {order.delivery_address}\n"
            text += f"💰 {order.total_amount:,} so'm\n"
            text += f"📊 Holat: **{order.get_status_display()}**\n"
            
            # Yetkazish vaqti
            if order.dormitory and order.status in ['confirmed', 'preparing', 'delivering']:
                expected_time = order.get_expected_delivery_time()
                if expected_time:
                    text += f"⏰ Kutilayotgan vaqt: {expected_time.strftime('%H:%M')}\n"
            elif order.status == 'delivered':
                text += f"✅ Yetkazildi: {order.updated_at.strftime('%H:%M')}\n"
            
            text += "\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
        
        send_safe_message(chat_id, text, markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Buyurtmalarni ko'rsatishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def show_dormitories(chat_id, user):
    """Barcha yotoqxonalarni to'liq ma'lumot bilan ko'rsatish"""
    try:
        dormitories = Dormitory.objects.filter(is_active=True)
        
        if not dormitories.exists():
            send_safe_message(chat_id, "❌ Hozircha yotoqxonalar mavjud emas.", get_main_menu_keyboard())
            return
        
        text = "🏠 Yotoqxonangizni tanlang:\n\n"
        
        # Har bir yotoqxona haqida to'liq ma'lumot
        for dormitory in dormitories:
            text += f"🏢 **{dormitory.name}**\n"
            text += f"📍 {dormitory.address}\n"
            
            # Yetkazish haqi
            if dormitory.delivery_fee > 0:
                text += f"💰 Yetkazish haqi: {dormitory.delivery_fee:,} so'm\n"
            else:
                text += "💰 Yetkazish: **BEPUL** 🎉\n"
            
            # Yetkazish vaqti
            if dormitory.delivery_time:
                text += f"⏰ Yetkazish vaqti: ~{dormitory.delivery_time} daqiqa\n"
            
            # Ish vaqti
            if dormitory.is_24_hours:
                text += "🕐 Ish vaqti: **24/7** 🌙\n"
            else:
                text += f"🕐 Ish vaqti: {dormitory.get_working_hours_display()}\n"
            
            # Mas'ul shaxs ma'lumotlari
            if dormitory.contact_person:
                text += f"👤 Mas'ul: {dormitory.contact_person}\n"
            if dormitory.contact_phone:
                text += f"📞 Telefon: {dormitory.contact_phone}\n"
            
            # Hozir ishlaydimi
            if dormitory.is_working_now():
                text += "✅ **HOZIR FAOL**\n"
            else:
                text += "❌ **HOZIR YOPIQ**\n"
            
            text += "➖➖➖➖➖➖➖➖➖➖\n\n"
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for dormitory in dormitories:
            # Tugma matnini qisqartirish
            status_icon = "✅" if dormitory.is_working_now() else "❌"
            button_text = f"{status_icon} {dormitory.name}"
            
            if dormitory.delivery_fee > 0:
                button_text += f" ({dormitory.delivery_fee:,} so'm)"
            else:
                button_text += " (BEPUL)"
            
            markup.add(types.InlineKeyboardButton(
                button_text,
                callback_data=f"select_dorm_{dormitory.id}"
            ))
        
        markup.add(types.InlineKeyboardButton("🔙 Savatga qaytish", callback_data="view_cart"))
        
        send_safe_message(chat_id, text, markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Yotoqxonalar ko'rsatishda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())



def ask_room_number(chat_id, user, dormitory_id):
    """Xona raqamini so'rash - yotoqxona ma'lumotlari bilan"""
    try:
        dormitory = Dormitory.objects.get(id=dormitory_id, is_active=True)
        
        # Yotoqxona hozir ishlaydimi tekshirish
        if not dormitory.is_working_now():
            text = f"❌ **{dormitory.name}** hozir yopiq!\n\n"
            text += f"🕐 Ish vaqti: {dormitory.get_working_hours_display()}\n\n"
            text += "Iltimos, boshqa yotoqxonani tanlang yoki ish vaqtida qaytib keling."
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Yotoqxonalar", callback_data="place_order"))
            markup.add(types.InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main"))
            
            send_safe_message(chat_id, text, markup, parse_mode='Markdown')
            return
        
        # OrderSession yaratish
        OrderSession.objects.filter(user=user, is_completed=False).delete()
        
        session = OrderSession.objects.create(
            user=user,
            dormitory=dormitory,
            delivery_address=dormitory.name,
            phone_number=user.phone_number or ""
        )
        
        text = f"✅ **{dormitory.name}** tanlandi!\n\n"
        text += f"📍 Manzil: {dormitory.address}\n"
        
        # Yetkazish ma'lumotlari
        if dormitory.delivery_fee > 0:
            text += f"💰 Yetkazish haqi: {dormitory.delivery_fee:,} so'm\n"
        else:
            text += "💰 Yetkazish: **BEPUL** 🎉\n"
        
        if dormitory.delivery_time:
            text += f"⏰ Taxminiy yetkazish vaqti: ~{dormitory.delivery_time} daqiqa\n"
        
        # Mas'ul shaxs
        if dormitory.contact_person and dormitory.contact_phone:
            text += f"👤 Mas'ul: {dormitory.contact_person} ({dormitory.contact_phone})\n"
        
        text += "\n📝 **Iltimos, xona raqamingizni kiriting:**\n\n"
        text += "Masalan: `101`, `205A`, `315-B`, `12`"
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔙 Yotoqxonalar", callback_data="place_order"),
            types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")
        )
        
        send_safe_message(chat_id, text, markup, parse_mode='Markdown')
        
    except Dormitory.DoesNotExist:
        send_safe_message(chat_id, "❌ Yotoqxona topilmadi.", get_main_menu_keyboard())
    except Exception as e:
        logger.error(f"Xona raqami so'rashda xatolik: {e}")
        send_safe_message(chat_id, "❌ Xatolik yuz berdi.", get_main_menu_keyboard())

def confirm_order(chat_id, user, room_number):
    """Buyurtmani tasdiqlash"""
    try:
        # OrderSession olish
        session = OrderSession.objects.filter(user=user, is_completed=False).first()
        if not session:
            send_safe_message(chat_id, "❌ Sessiya topilmadi. Qaytadan urinib ko'ring.", get_main_menu_keyboard())
            return
        
        # Savatni tekshirish
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            send_safe_message(chat_id, "❌ Savatingiz bo'sh!", get_main_menu_keyboard())
            return
        
        # Umumiy summani hisoblash
        total_amount = Decimal('0')
        for item in cart_items:
            total_amount += item.get_total_price()
        
        # Yetkazish haqini qo'shish
        delivery_fee = session.dormitory.delivery_fee or Decimal('0')
        final_total = total_amount + delivery_fee
        
        # Buyurtma yaratish
        order = Order.objects.create(
            user=user,
            dormitory=session.dormitory,
            delivery_address=f"{session.dormitory.name}, {room_number}-xona",
            room_number=room_number,
            phone_number=user.phone_number or "",
            total_amount=final_total,
            status='pending'
        )
        
        # Buyurtma mahsulotlarini yaratish
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Savatni tozalash
        cart_items.delete()
        
        # Sessiyani tugallash
        session.is_completed = True
        session.save()
        
        # Tasdiqlash xabari
        text = f"✅ Buyurtma #{order.id} muvaffaqiyatli qabul qilindi!\n\n"
        text += f"📅 Vaqt: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"🍕 Mahsulotlar: {total_amount:,} so'm\n"
        
        if delivery_fee > 0:
            text += f"� Yetkazish: {delivery_fee:,} so'm\n"
            text += f"💰 Jami: {final_total:,} so'm\n"
        else:
            text += f"🚚 Yetkazish: Bepul\n"
            text += f"�💰 Jami: {final_total:,} so'm\n"
        
        text += f"📍 Manzil: {order.delivery_address}\n\n"
        text += "⏳ Buyurtmangiz oshpazga yuborildi!\n"
        text += "📞 Tez orada siz bilan bog'lanamiz!"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 Buyurtmalarim", callback_data="my_orders"))
        markup.add(types.InlineKeyboardButton("🔙 Bosh menyu", callback_data="back_to_main"))
        
        send_safe_message(chat_id, text, markup)
        
        # Oshpazga xabar yuborish (keyinroq qo'shiladi)
        send_order_to_kitchen(order)
        
        logger.info(f"Yangi buyurtma: #{order.id} - {user.first_name} - {final_total:,} so'm")
        
    except Exception as e:
        logger.error(f"Buyurtma tasdiqlashda xatolik: {e}")
        send_safe_message(chat_id, "❌ Buyurtma berishda xatolik yuz berdi.", get_main_menu_keyboard())

def send_order_to_kitchen(order):
    """Buyurtmani oshpazga yuborish"""
    try:
        # Kitchen staff'larga xabar yuborish
        from users.models import KitchenStaff
        kitchen_staff = KitchenStaff.objects.filter(is_active=True)
        
        text = f"🔔 YANGI BUYURTMA!\n\n"
        text += f"📋 Buyurtma #{order.id}\n"
        text += f"👤 Mijoz: {order.user.first_name or 'Noma\'lum'}\n"
        text += f"📱 Telefon: {order.phone_number}\n"
        text += f"📍 Manzil: {order.delivery_address}\n"
        text += f" Summa: {order.total_amount:,} so'm\n"
        text += f"📅 Vaqt: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        text += "📦 Mahsulotlar:\n"
        for item in order.items.all():
            text += f"• {item.product.name} x{item.quantity} = {item.get_total_price():,} so'm\n"
        
        # Kitchen staff'larga yuborish (agar telegram_id bo'lsa)
        for staff in kitchen_staff:
            if hasattr(staff, 'telegram_user_id') and staff.telegram_user_id:
                try:
                    send_safe_message(staff.telegram_user_id, text)
                except:
                    pass
        
        print(f"📨 Buyurtma #{order.id} oshpazga yuborildi")
        
    except Exception as e:
        logger.error(f"Oshpazga xabar yuborishda xatolik: {e}")

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
            
            # Foydalanuvchini bazaga saqlash
            user, created = TelegramUser.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'is_active': True
                }
            )
            
            # Ro'yxatdan o'tgan foydalanuvchi uchun asosiy menyu
            show_main_menu(message.chat.id, user)
            
        except Exception as e:
            logger.error(f"Start xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call):
        """Callback query'larni qayta ishlash"""
        try:
            user_id = call.from_user.id
            user = TelegramUser.objects.get(user_id=user_id)
            data = call.data
            
            if data.startswith("cat_"):
                # Kategoriya tanlash
                category_id = int(data.split("_")[1])
                show_category_products(call.message.chat.id, user, category_id)
                
            elif data.startswith("prod_"):
                # Mahsulot tanlash
                product_id = int(data.split("_")[1])
                show_product_details(call.message.chat.id, user, product_id)
                
            elif data.startswith("add_to_cart_"):
                # Savatga qo'shish
                product_id = int(data.split("_")[3])
                add_to_cart(call.message.chat.id, user, product_id)
                
            elif data.startswith("increase_"):
                # Savatda miqdorni oshirish
                product_id = int(data.split("_")[1])
                try:
                    cart_item = Cart.objects.get(user=user, product_id=product_id)
                    cart_item.quantity += 1
                    cart_item.save()
                    show_cart(call.message.chat.id, user)
                except Cart.DoesNotExist:
                    bot.answer_callback_query(call.id, "❌ Mahsulot savatda topilmadi")
                    
            elif data.startswith("decrease_"):
                # Savatda miqdorni kamaytirish
                product_id = int(data.split("_")[1])
                try:
                    cart_item = Cart.objects.get(user=user, product_id=product_id)
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()
                    show_cart(call.message.chat.id, user)
                except Cart.DoesNotExist:
                    bot.answer_callback_query(call.id, "❌ Mahsulot savatda topilmadi")
                    
            elif data == "clear_cart":
                # Savatni tozalash
                Cart.objects.filter(user=user).delete()
                send_safe_message(call.message.chat.id, "🗑️ Savat tozalandi!", get_main_menu_keyboard())
                
            elif data == "view_cart":
                # Savatni ko'rish
                show_cart(call.message.chat.id, user)
                
            elif data == "place_order":
                # Buyurtma berish
                place_order(call.message.chat.id, user)
                
            elif data.startswith("select_dorm_"):
                # Yotoqxona tanlash - to'g'ridan-to'g'ri xona raqamini so'rash
                dormitory_id = int(data.split("_")[2])
                ask_room_number(call.message.chat.id, user, dormitory_id)
                
            elif data == "cancel_order":
                # Buyurtmani bekor qilish
                OrderSession.objects.filter(user=user, is_completed=False).delete()
                send_safe_message(call.message.chat.id, "❌ Buyurtma bekor qilindi.", get_main_menu_keyboard())
                
            elif data == "my_orders":
                # Buyurtmalarni ko'rish
                show_my_orders(call.message.chat.id, user)
                
            elif data == "back_to_categories":
                # Kategoriyalarga qaytish
                show_menu_categories(call.message.chat.id, user)
                
            elif data == "back_to_main":
                # Bosh menyuga qaytish
                show_main_menu(call.message.chat.id, user)
            
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
            
            # Buyurtma sessiyasi uchun xona raqamini kutish
            active_session = OrderSession.objects.filter(user=user, is_completed=False).first()
            if active_session and not active_session.room_number:
                # Xona raqami kiritildi
                room_number = text.strip()
                if room_number.isdigit() or room_number.replace('-', '').replace('/', '').isalnum():
                    confirm_order(message.chat.id, user, room_number)
                    return
                else:
                    send_safe_message(message.chat.id, "❌ Iltimos, to'g'ri xona raqamini kiriting (masalan: 101, 205, 315)")
                    return
            
            # Asosiy xabarlar
            if text == "🍕 Menyu":
                show_menu_categories(message.chat.id, user)
            elif text == "🛒 Savat":
                show_cart(message.chat.id, user)
            elif text == "📋 Buyurtmalarim":
                show_my_orders(message.chat.id, user)
            elif text == "ℹ️ Ma'lumot":
                info_text = f"ℹ️ Sizning ma'lumotlaringiz:\n\n"
                info_text += f"👤 Ism: {user.first_name or 'Noma\'lum'}\n"
                info_text += f"📱 Username: @{user.username or 'Noma\'lum'}"
                send_safe_message(message.chat.id, info_text, get_main_menu_keyboard())
            else:
                # Noma'lum xabar
                send_safe_message(message.chat.id, "Iltimos, quyidagi tugmalardan birini tanlang:", get_main_menu_keyboard())
                
        except Exception as e:
            logger.error(f"Text message handling xatosi: {e}")
            send_safe_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")

def start_bot():
    """Botni ishga tushirish"""
    try:
        print('🚀 Bot ishga tushirish jarayoni boshlandi...')
        bot = get_bot()
        if not bot:
            print('❌ Bot yaratilmadi!')
            return
        
        # Handler'larni sozlash
        setup_handlers()
        
        print('🚀 Bot polling rejimida ishga tushmoqda...')
        
        while True:
            try:
                bot.infinity_polling(timeout=10, long_polling_timeout=5, none_stop=False, interval=1)
                break
            except Exception as polling_error:
                print(f'⚠️ Polling xatosi: {polling_error}')
                
                if '409' in str(polling_error):
                    print('⏳ 409 xatosi - 10 soniya kutish...')
                    time.sleep(10)
                    global bot_instance
                    bot_instance = None
                    bot = get_bot()
                    if not bot:
                        break
                else:
                    time.sleep(5)
        
    except Exception as e:
        print(f'❌ Bot ishga tushirishda xatolik: {e}')

if __name__ == '__main__':
    start_bot()

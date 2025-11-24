"""
Telegram bot webhook orqali ishga tushirish (hosting uchun)
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from bot.telegram_bot import get_bot, setup_handlers
import telebot

class Command(BaseCommand):
    help = 'Telegram bot webhook orqali ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Webhook URL (masalan: https://yoursite.com/bot/webhook/)',
            required=False
        )

    def handle(self, *args, **options):
        try:
            bot = get_bot()
            if not bot:
                self.stdout.write(self.style.ERROR('❌ Bot yaratilmadi'))
                return

            # Webhook URL
            webhook_url = options.get('url')
            if not webhook_url:
                # settings.py dan olish
                webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
            
            if not webhook_url:
                self.stdout.write(self.style.ERROR('❌ Webhook URL topilmadi'))
                self.stdout.write('settings.py ga TELEGRAM_WEBHOOK_URL qo\'shing yoki --url parameter bering')
                return

            # Eski webhook'ni o'chirish
            self.stdout.write('🔄 Eski webhook o\'chirilmoqda...')
            bot.remove_webhook()
            
            # Yangi webhook o'rnatish
            self.stdout.write(f'🔧 Webhook o\'rnatilmoqda: {webhook_url}')
            result = bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,  # Eski xabarlarni o'chirish
                max_connections=100
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS('✅ Webhook muvaffaqiyatli o\'rnatildi'))
                
                # Webhook ma'lumotlarini tekshirish
                webhook_info = bot.get_webhook_info()
                self.stdout.write(f'📊 Webhook holati:')
                self.stdout.write(f'  - URL: {webhook_info.url}')
                self.stdout.write(f'  - Pending updates: {webhook_info.pending_update_count}')
                if webhook_info.last_error_message:
                    self.stdout.write(self.style.WARNING(f'  - Oxirgi xato: {webhook_info.last_error_message}'))
            else:
                self.stdout.write(self.style.ERROR('❌ Webhook o\'rnatilmadi'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Xatolik: {e}'))

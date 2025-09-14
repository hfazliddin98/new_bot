from django.core.management.base import BaseCommand
from bot.apps import BotConfig
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--background',
            action='store_true',
            help='Bot ni background thread da ishga tushirish',
        )

    def handle(self, *args, **options):
        self.stdout.write("🤖 Telegram bot ishga tushirilmoqda...")
        
        try:
            bot_config = BotConfig('bot', __import__('bot'))
            
            if options['background']:
                # Background da ishga tushirish
                bot_config.start_telegram_bot()
                self.stdout.write(
                    self.style.SUCCESS("✅ Bot background thread da ishga tushdi!")
                )
                
                # Main thread'ni ushlab turish
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write("⏹️  Bot to'xtatildi")
            else:
                # Foreground da ishga tushirish
                from bot.telegram_bot import start_bot
                start_bot()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Bot ishga tushirishda xatolik: {e}")
            )
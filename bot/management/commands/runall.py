from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
import threading
import time
import sys
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Django server va Telegram bot ni birga ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=str,
            default='8000',
            help='Django server porti (default: 8000)',
        )

    def handle(self, *args, **options):
        port = options['port']
        
        self.stdout.write("🚀 Django server va Telegram bot ishga tushirilmoqda...")
        
        try:
            # Bot ni background thread da ishga tushirish
            def start_telegram_bot():
                try:
                    from bot.telegram_bot import start_bot
                    time.sleep(3)  # Django server ishga tushishini kutish
                    self.stdout.write("🤖 Telegram bot ishga tushirilmoqda...")
                    start_bot()
                except Exception as e:
                    logger.error(f"Bot ishga tushirishda xatolik: {e}")
                    self.stdout.write(
                        self.style.ERROR(f"❌ Bot xatolik: {e}")
                    )
            
            # Bot thread yaratish
            bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
            bot_thread.start()
            
            # Django server ishga tushirish
            self.stdout.write(f"🌐 Django server {port} portda ishga tushirilmoqda...")
            
            # sys.argv ni o'zgartirish runserver uchun
            original_argv = sys.argv.copy()
            sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}']
            
            try:
                execute_from_command_line(sys.argv)
            finally:
                sys.argv = original_argv
                
        except KeyboardInterrupt:
            self.stdout.write("⏹️  Server va bot to'xtatildi")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ishga tushirishda xatolik: {e}")
            )
from django.apps import AppConfig
import threading
import logging
import os

logger = logging.getLogger(__name__)


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    verbose_name = 'Telegram Bot'
    
    def ready(self):
        """Django server ishga tushganda bot avtomatik ishga tushadi"""
        import sys
        
        # Test va migration paytida bot ishlatmaslik
        if any(cmd in sys.argv for cmd in ['test', 'migrate', 'makemigrations', 'collectstatic']):
            return
            
        # Runserver'da faqat main process'da ishga tushirish
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                # Runserver'ning main process'i
                print("🚀 Django server ishga tushdi, bot ham ishga tushirilmoqda...")
                self.start_telegram_bot()
        else:
            # Boshqa commandlar uchun (production mode)
            self.start_telegram_bot()
    
    def start_telegram_bot(self):
        """Telegram botni background thread'da ishga tushirish"""
        def bot_runner():
            try:
                import time
                time.sleep(2)  # Django to'liq yuklashini kutish
                
                from .telegram_bot import start_bot
                print("🤖 Telegram bot thread'da ishga tushirilmoqda...")
                start_bot()
                
            except Exception as e:
                logger.error(f"Bot thread'da xatolik: {e}")
                print(f"❌ Bot thread'da xatolik: {e}")
        
        try:
            # Bot'ni alohida thread'da ishga tushirish
            bot_thread = threading.Thread(target=bot_runner, daemon=True)
            bot_thread.start()
            
            logger.info("🤖 Telegram bot thread yaratildi!")
            print("🤖 Telegram bot thread yaratildi!")
            
        except Exception as e:
            logger.error(f"Bot thread yaratishda xatolik: {e}")
            print(f"❌ Bot thread yaratishda xatolik: {e}")

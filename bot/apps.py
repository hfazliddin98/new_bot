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
        import os
        # Faqat asosiy process'da ishga tushirish (autoreload oldini olish)
        if os.environ.get('RUN_MAIN') and not hasattr(self, 'bot_started'):
            self.bot_started = True
            self.start_telegram_bot()
    
    def start_telegram_bot(self):
        """Telegram botni background thread'da ishga tushirish"""
        try:
            from .telegram_bot import start_bot
            
            # Bot'ni alohida thread'da ishga tushirish
            bot_thread = threading.Thread(target=start_bot, daemon=True)
            bot_thread.start()
            
            logger.info("🤖 Telegram bot avtomatik ishga tushdi!")
            print("🤖 Telegram bot avtomatik ishga tushdi!")
            
        except Exception as e:
            logger.error(f"Bot ishga tushirishda xatolik: {e}")
            print(f"❌ Bot ishga tushirishda xatolik: {e}")

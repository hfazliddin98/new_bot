from django.apps import AppConfig
import threading
import logging
import os

logger = logging.getLogger(__name__)


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    verbose_name = 'Telegram Bot'
    bot_thread = None  # Bot thread'ni saqlab turish
    
    def ready(self):
        """Django server ishga tushganda bot avtomatik ishga tushadi"""
        import sys
        
        # Test va migration paytida bot ishlatmaslik
        if any(cmd in sys.argv for cmd in ['test', 'migrate', 'makemigrations', 'collectstatic', 'check']):
            return
        
        # Polling rejimi - avtomatik ishga tushirish
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            # Local development (runserver)
            print("🚀 Django server ishga tushdi (runserver)")
            self.start_telegram_bot()
        elif 'runserver' not in sys.argv and not BotConfig.bot_thread:
            # Production server (Gunicorn, uWSGI, etc.)
            print("🚀 Django server ishga tushdi (production)")
            self.start_telegram_bot()
    
    def start_telegram_bot(self):
        """Telegram botni background thread'da ishga tushirish"""
        # Agar thread allaqachon ishlab tursa, qayta ishga tushirmaslik
        if BotConfig.bot_thread and BotConfig.bot_thread.is_alive():
            print("ℹ️  Bot allaqachon ishlab turibdi")
            return
        
        def bot_runner():
            try:
                import time
                time.sleep(3)  # Django to'liq yuklashini kutish
                
                from .telegram_bot import start_bot
                print("🤖 Telegram bot polling rejimida ishga tushirilmoqda...")
                logger.info("Telegram bot polling started")
                start_bot()
                
            except KeyboardInterrupt:
                print("\n⏹️  Bot to'xtatildi (Ctrl+C)")
                logger.info("Bot stopped by user")
            except Exception as e:
                logger.error(f"Bot thread'da xatolik: {e}", exc_info=True)
                print(f"❌ Bot thread'da xatolik: {e}")
        
        try:
            # Bot'ni alohida thread'da ishga tushirish
            BotConfig.bot_thread = threading.Thread(target=bot_runner, daemon=True, name="TelegramBotThread")
            BotConfig.bot_thread.start()
            
            logger.info("🤖 Telegram bot thread yaratildi!")
            print("✅ Telegram bot thread yaratildi va ishga tushdi!")
            print("📱 Bot @qdutaomttj_bot ga xabar yuborishingiz mumkin")
            
        except Exception as e:
            logger.error(f"Bot thread yaratishda xatolik: {e}")
            print(f"❌ Bot thread yaratishda xatolik: {e}")

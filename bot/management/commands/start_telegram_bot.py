from django.core.management.base import BaseCommand
from bot.telegram_bot import start_bot


class Command(BaseCommand):
    help = 'Telegram botni ishga tushirish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Botni background\'da ishga tushirish',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Telegram bot ishga tushirilmoqda...')
        )
        
        try:
            start_bot()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('🛑 Bot to\'xtatildi')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Bot ishga tushishda xatolik: {e}')
            )
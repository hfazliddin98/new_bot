"""
Telegram Bot Admin Commands - Spam bilan kurashish uchun
"""
from django.core.management.base import BaseCommand
from bot.models import TelegramUser
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Spam foydalanuvchilarni bloklash va boshqarish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--block',
            type=int,
            help='Foydalanuvchi ID sini bloklash',
        )
        parser.add_argument(
            '--unblock',
            type=int,
            help='Foydalanuvchi ID sini blokdan chiqarish',
        )
        parser.add_argument(
            '--list-blocked',
            action='store_true',
            help='Bloklangan foydalanuvchilar ro\'yxatini ko\'rsatish',
        )
        parser.add_argument(
            '--find-spam',
            action='store_true',
            help='Potensial spam foydalanuvchilarni topish',
        )

    def handle(self, *args, **options):
        if options['block']:
            self.block_user(options['block'])
        elif options['unblock']:
            self.unblock_user(options['unblock'])
        elif options['list_blocked']:
            self.list_blocked_users()
        elif options['find_spam']:
            self.find_spam_users()
        else:
            self.stdout.write(self.style.ERROR('Kamida bitta parametr kerak. --help ni ko\'ring'))

    def block_user(self, user_id):
        """Foydalanuvchini bloklash"""
        try:
            user = TelegramUser.objects.get(user_id=user_id)
            user.is_active = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Foydalanuvchi bloklandi: {user_id} (@{user.username})'))
            logger.info(f'Foydalanuvchi bloklandi: {user_id}')
        except TelegramUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Foydalanuvchi topilmadi: {user_id}'))

    def unblock_user(self, user_id):
        """Foydalanuvchini blokdan chiqarish"""
        try:
            user = TelegramUser.objects.get(user_id=user_id)
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Foydalanuvchi blokdan chiqarildi: {user_id} (@{user.username})'))
            logger.info(f'Foydalanuvchi blokdan chiqarildi: {user_id}')
        except TelegramUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Foydalanuvchi topilmadi: {user_id}'))

    def list_blocked_users(self):
        """Bloklangan foydalanuvchilar ro'yxati"""
        blocked_users = TelegramUser.objects.filter(is_active=False)
        
        if not blocked_users.exists():
            self.stdout.write(self.style.WARNING('⚠️ Bloklangan foydalanuvchilar yo\'q'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n📋 Bloklangan foydalanuvchilar ({blocked_users.count()} ta):\n'))
        
        for user in blocked_users:
            self.stdout.write(
                f"  • ID: {user.user_id} | "
                f"Username: @{user.username or 'N/A'} | "
                f"Ism: {user.full_name or user.first_name or 'N/A'}"
            )

    def find_spam_users(self):
        """Potensial spam foydalanuvchilarni topish"""
        from bot.models import Message
        
        self.stdout.write(self.style.WARNING('🔍 Spam foydalanuvchilarni qidiryapman...\n'))
        
        # Spam kalit so'zlari
        spam_keywords = ['mega', 'direct link', 'stream', 'hot_girl', 'porn', 't.me/', 'http']
        
        spam_users = []
        
        # Barcha xabarlarni tekshirish
        messages = Message.objects.all()
        
        for message in messages:
            text_lower = message.message_text.lower()
            for keyword in spam_keywords:
                if keyword in text_lower:
                    spam_users.append({
                        'user': message.telegram_user,
                        'keyword': keyword,
                        'message': message.message_text[:100]
                    })
                    break
        
        if not spam_users:
            self.stdout.write(self.style.SUCCESS('✅ Spam foydalanuvchilar topilmadi'))
            return
        
        self.stdout.write(self.style.ERROR(f'\n⚠️ {len(spam_users)} ta potensial spam topildi:\n'))
        
        for item in spam_users:
            user = item['user']
            self.stdout.write(
                f"  • ID: {user.user_id} | "
                f"Username: @{user.username or 'N/A'} | "
                f"Keyword: '{item['keyword']}' | "
                f"Xabar: {item['message'][:50]}..."
            )
        
        self.stdout.write(
            self.style.WARNING(
                f"\n💡 Bloklash uchun: python manage.py manage_spam --block <user_id>"
            )
        )

from django.contrib import admin
from .models import TelegramUser, Message

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'user_id')
    ordering = ('-created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'message_text_short', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('message_text', 'telegram_user__username')
    ordering = ('-created_at',)
    
    def message_text_short(self, obj):
        return obj.message_text[:50] + "..." if len(obj.message_text) > 50 else obj.message_text
    message_text_short.short_description = 'Xabar matni'

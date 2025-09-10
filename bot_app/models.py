from django.db import models
from django.contrib.auth.models import User

class TelegramUser(models.Model):
    """Telegram foydalanuvchilari modeli"""
    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ism")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Familiya")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")
    
    class Meta:
        verbose_name = "Telegram Foydalanuvchi"
        verbose_name_plural = "Telegram Foydalanuvchilar"
    
    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} (@{self.username})"

class Message(models.Model):
    """Xabarlar modeli"""
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    message_text = models.TextField(verbose_name="Xabar matni")
    message_type = models.CharField(max_length=50, default='text', verbose_name="Xabar turi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqt")
    
    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.telegram_user.first_name}: {self.message_text[:50]}..."

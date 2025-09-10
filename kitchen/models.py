from django.db import models
from django.contrib.auth.models import User
from bot.models import Order, OrderItem

class KitchenStaff(models.Model):
    """Oshxona xodimlari modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    full_name = models.CharField(max_length=200, verbose_name="To'liq ism")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    position = models.CharField(max_length=100, default="Oshpaz", verbose_name="Lavozim")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Oshxona xodimi"
        verbose_name_plural = "Oshxona xodimlari"
    
    def __str__(self):
        return f"{self.full_name} ({self.position})"

class OrderProgress(models.Model):
    """Buyurtma holati"""
    STATUS_CHOICES = [
        ('received', 'Qabul qilindi'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('picked_up', 'Kuryer oldi'),
        ('delivered', 'Yetkazildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Buyurtma")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received', verbose_name="Holat")
    kitchen_staff = models.ForeignKey(KitchenStaff, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Oshxona xodimi")
    preparation_time = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tayyorlash vaqti (daqiqa)")
    notes = models.TextField(blank=True, verbose_name="Izohlar")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Boshlandi")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Tugadi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilandi")
    
    class Meta:
        verbose_name = "Buyurtma holati"
        verbose_name_plural = "Buyurtma holatlari"
    
    def __str__(self):
        return f"Buyurtma #{self.order.id} - {self.get_status_display()}"
    
    def get_status_color(self):
        """Holat rangini qaytarish"""
        colors = {
            'received': 'warning',
            'preparing': 'info', 
            'ready': 'success',
            'picked_up': 'primary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')

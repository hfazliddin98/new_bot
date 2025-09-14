from django.db import models
from django.contrib.auth import get_user_model
from bot.models import Order

User = get_user_model()

class CourierStaff(models.Model):
    """Kuryer xodimlari modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    full_name = models.CharField(max_length=200, verbose_name="To'liq ism")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    vehicle_type = models.CharField(max_length=50, default="Piyoda", verbose_name="Transport turi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Kuryer"
        verbose_name_plural = "Kuryerlar"
    
    def __str__(self):
        return f"{self.full_name} ({self.vehicle_type})"

class Delivery(models.Model):
    """Yetkazib berish modeli"""
    STATUS_CHOICES = [
        ('ready', 'Tayyor'),
        ('assigned', 'Tayinlandi'),
        ('picked_up', 'Olib ketildi'),
        ('on_way', 'Yo\'lda'),
        ('delivered', 'Yetkazildi'),
        ('failed', 'Muvaffaqiyatsiz'),
        ('returned', 'Qaytarildi'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Buyurtma")
    courier = models.ForeignKey(CourierStaff, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kuryer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready', verbose_name="Holat")
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Tayinlangan vaqt")
    picked_up_at = models.DateTimeField(null=True, blank=True, verbose_name="Olingan vaqt")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Yetkazilgan vaqt")
    delivery_address = models.TextField(blank=True, verbose_name="Yetkazib berish manzili")
    delivery_notes = models.TextField(blank=True, verbose_name="Yetkazib berish izohlari")
    customer_feedback = models.TextField(blank=True, verbose_name="Mijoz fikri")
    rating = models.PositiveIntegerField(null=True, blank=True, verbose_name="Baho (1-5)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilandi")
    
    class Meta:
        verbose_name = "Yetkazib berish"
        verbose_name_plural = "Yetkazib berishlar"
    
    def __str__(self):
        return f"Buyurtma #{self.order.id} - {self.get_status_display()}"
    
    def get_status_color(self):
        """Holat rangini qaytarish"""
        colors = {
            'ready': 'warning',
            'assigned': 'info',
            'picked_up': 'primary',
            'on_way': 'primary',
            'delivered': 'success',
            'failed': 'danger',
            'returned': 'secondary'
        }
        return colors.get(self.status, 'secondary')

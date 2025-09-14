from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TelegramUser(models.Model):
    """Telegram foydalanuvchilari modeli"""
    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ism")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Familiya")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqam")
    full_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="To'liq ism")
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name="Yosh")
    dormitory = models.ForeignKey('Dormitory', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Yotoqxona")
    room_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Xona raqami")
    is_registered = models.BooleanField(default=False, verbose_name="Ro'yxatdan o'tgan")
    registration_date = models.DateTimeField(blank=True, null=True, verbose_name="Ro'yxatdan o'tgan sana")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")
    
    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
    
    def __str__(self):
        name = self.full_name or f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{name} (@{self.username})" if name else f"@{self.username}"
    
    def get_display_name(self):
        """Ko'rsatish uchun ism"""
        return self.full_name or self.first_name or self.username or "Foydalanuvchi"

class Category(models.Model):
    """Mahsulot kategoriyalari"""
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Rasm")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Mahsulotlar modeli"""
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Rasm")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
    
    def __str__(self):
        return f"{self.name} - {self.price} so'm"

class Cart(models.Model):
    """Savatcha modeli"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")
    
    class Meta:
        verbose_name = "Savatcha"
        verbose_name_plural = "Savatchalar"
        unique_together = ['user', 'product']
    
    def get_total_price(self):
        return self.quantity * self.product.price
    
    def __str__(self):
        return f"{self.user.first_name} - {self.product.name} x{self.quantity}"

class OrderSession(models.Model):
    """Buyurtma sessiyasi - har bir buyurtma uchun alohida manzil"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    delivery_address = models.TextField(verbose_name="Yetkazib berish manzili")
    room_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Xona raqami")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    dormitory = models.ForeignKey('Dormitory', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Yotoqxona")
    additional_notes = models.TextField(blank=True, verbose_name="Qo'shimcha izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    is_completed = models.BooleanField(default=False, verbose_name="Tugatilgan")
    
    class Meta:
        verbose_name = "Buyurtma sessiyasi"
        verbose_name_plural = "Buyurtma sessiyalari"
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.delivery_address}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('preparing', 'Tayyorlanmoqda'),
        ('delivering', 'Yetkazilmoqda'),
        ('delivered', 'Yetkazildi'),
        ('completed', 'Bajarildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Naqd pul'),
        ('card', 'Plastik karta'),
        ('online', 'Online to\'lov'),
    ]
    
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    dormitory = models.ForeignKey('Dormitory', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Yotoqxona")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holat")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash', verbose_name="To'lov usuli")
    delivery_address = models.TextField(verbose_name="Yetkazib berish manzili")
    room_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Xona raqami")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    delivery_time = models.DateTimeField(blank=True, null=True, verbose_name="Yetkazib berish vaqti")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umumiy summa")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Yetkazib berish haqi")
    notes = models.TextField(blank=True, verbose_name="Izohlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Buyurtma vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Buyurtma #{self.id} - {self.user.first_name} - {self.total_amount} so'm"
    
    def get_expected_delivery_time(self):
        """Kutilayotgan yetkazib berish vaqtini hisoblash"""
        if self.dormitory:
            from django.utils import timezone
            from datetime import timedelta
            return self.created_at + timedelta(minutes=self.dormitory.delivery_time)
        return None
    
    def get_delivery_time_display(self):
        """Yetkazib berish vaqtini ko'rsatish"""
        expected_time = self.get_expected_delivery_time()
        if expected_time:
            return expected_time.strftime('%H:%M')
        return "Noma'lum"

class OrderItem(models.Model):
    """Buyurtma mahsulotlari"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Buyurtma")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Mahsulot")
    quantity = models.PositiveIntegerField(verbose_name="Miqdor")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    
    class Meta:
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"
    
    def get_total_price(self):
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

class Dormitory(models.Model):
    """Yotoqxonalar"""
    name = models.CharField(max_length=100, verbose_name="Yotoqxona nomi")
    address = models.TextField(verbose_name="To'liq manzil")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Mas'ul shaxs")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqam")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Yetkazib berish haqi")
    delivery_time = models.PositiveIntegerField(default=30, verbose_name="Yetkazib berish vaqti (daqiqa)")
    working_hours_start = models.TimeField(default='09:00', verbose_name="Ish boshlanish vaqti")
    working_hours_end = models.TimeField(default='23:00', verbose_name="Ish tugash vaqti")
    is_24_hours = models.BooleanField(default=False, verbose_name="24 soat ishlaydi")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True, verbose_name="Kenglik")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True, verbose_name="Uzunlik")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    notes = models.TextField(blank=True, verbose_name="Qo'shimcha ma'lumot")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    
    class Meta:
        verbose_name = "Yotoqxona"
        verbose_name_plural = "Yotoqxonalar"
    
    def __str__(self):
        return self.name
    
    def is_working_now(self):
        """Hozir ishlayotganligini tekshirish"""
        if self.is_24_hours:
            return True
        
        from django.utils import timezone
        current_time = timezone.now().time()
        
        if self.working_hours_start <= self.working_hours_end:
            return self.working_hours_start <= current_time <= self.working_hours_end
        else:
            return current_time >= self.working_hours_start or current_time <= self.working_hours_end
    
    def get_working_hours_display(self):
        """Ish soatlarini ko'rsatish"""
        if self.is_24_hours:
            return "24 soat"
        return f"{self.working_hours_start.strftime('%H:%M')} - {self.working_hours_end.strftime('%H:%M')}"

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

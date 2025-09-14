from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based permissions
    """
    
    # Role choices
    KITCHEN_STAFF = 'kitchen'
    COURIER = 'courier'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (KITCHEN_STAFF, 'Oshxona xodimi'),
        (COURIER, 'Kuryer'),
        (ADMIN, 'Administrator'),
    ]
    
    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=KITCHEN_STAFF,
        verbose_name='Rol'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefon raqami'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Manzil'
    )
    
    is_active_worker = models.BooleanField(
        default=True,
        verbose_name='Faol xodim'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan sana'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yangilangan sana'
    )
    
    # Shifrlangan bo'lmagan parol (xavfsizlik uchun tavsiya etilmaydi)
    plain_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Ochiq parol'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        db_table = 'users_user'

    def __str__(self):
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"
    
    def is_kitchen_staff(self):
        """Check if user is kitchen staff"""
        return self.role == self.KITCHEN_STAFF
    
    def is_courier(self):
        """Check if user is courier"""
        return self.role == self.COURIER
    
    def is_admin_user(self):
        """Check if user is admin"""
        return self.role == self.ADMIN or self.is_superuser
    
    def can_access_kitchen(self):
        """Check if user can access kitchen panel"""
        return self.role in [self.KITCHEN_STAFF, self.ADMIN] or self.is_superuser
    
    def can_access_courier(self):
        """Check if user can access courier panel"""
        return self.role in [self.COURIER, self.ADMIN] or self.is_superuser
    
    def get_dashboard_url(self):
        """Get user's default dashboard URL based on role"""
        if self.is_kitchen_staff():
            return '/kitchen/'
        elif self.is_courier():
            return '/courier/'
        elif self.is_admin_user():
            return '/admin-panel/'  # Admins go to admin panel
        else:
            return '/accounts/login/'  # Unknown role redirects to login

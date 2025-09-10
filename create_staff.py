#!/usr/bin/env python
"""
Test uchun oshxona va kuryer xodimlarini yaratish
"""
import os
import sys
import django
from pathlib import Path

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from django.contrib.auth.models import User
from kitchen.models import KitchenStaff
from courier.models import CourierStaff
from bot.models import DeliveryZone

def create_test_users():
    """Test foydalanuvchilarini yaratish"""
    
    # Oshxona xodimi
    kitchen_user, created = User.objects.get_or_create(
        username='oshpaz1',
        defaults={
            'first_name': 'Ali',
            'last_name': 'Karimov',
            'email': 'oshpaz@test.com'
        }
    )
    if created:
        kitchen_user.set_password('123456')
        kitchen_user.save()
        print(f"✅ Oshpaz foydalanuvchisi yaratildi: {kitchen_user.username}")
    
    # Oshxona xodimi profili
    kitchen_staff, created = KitchenStaff.objects.get_or_create(
        user=kitchen_user,
        defaults={
            'full_name': 'Ali Karimov',
            'phone_number': '+998901234567',
            'position': 'Bosh oshpaz'
        }
    )
    if created:
        print(f"✅ Oshxona xodimi yaratildi: {kitchen_staff.full_name}")
    
    # Kuryer 1
    courier_user1, created = User.objects.get_or_create(
        username='kuryer1',
        defaults={
            'first_name': 'Bobur',
            'last_name': 'Aliyev',
            'email': 'kuryer1@test.com'
        }
    )
    if created:
        courier_user1.set_password('123456')
        courier_user1.save()
        print(f"✅ Kuryer foydalanuvchisi yaratildi: {courier_user1.username}")
    
    # Kuryer profili
    courier_staff1, created = CourierStaff.objects.get_or_create(
        user=courier_user1,
        defaults={
            'full_name': 'Bobur Aliyev',
            'phone_number': '+998901234568',
            'vehicle_type': 'Mototsikl'
        }
    )
    if created:
        print(f"✅ Kuryer yaratildi: {courier_staff1.full_name}")
        
        # Kuryer zonalarini qo'shish
        zones = DeliveryZone.objects.filter(is_active=True)
        if zones.exists():
            courier_staff1.delivery_zones.set(zones)
            print(f"✅ Kuryerga {zones.count()} ta zona qo'shildi")
    
    # Kuryer 2
    courier_user2, created = User.objects.get_or_create(
        username='kuryer2',
        defaults={
            'first_name': 'Sardor',
            'last_name': 'Usmonov',
            'email': 'kuryer2@test.com'
        }
    )
    if created:
        courier_user2.set_password('123456')
        courier_user2.save()
        print(f"✅ Kuryer foydalanuvchisi yaratildi: {courier_user2.username}")
    
    # Kuryer profili
    courier_staff2, created = CourierStaff.objects.get_or_create(
        user=courier_user2,
        defaults={
            'full_name': 'Sardor Usmonov',
            'phone_number': '+998901234569',
            'vehicle_type': 'Piyoda'
        }
    )
    if created:
        print(f"✅ Kuryer yaratildi: {courier_staff2.full_name}")
        
        # Kuryer zonalarini qo'shish
        zones = DeliveryZone.objects.filter(is_active=True)[:2]  # Faqat 2 ta zona
        if zones.exists():
            courier_staff2.delivery_zones.set(zones)
            print(f"✅ Kuryerga {zones.count()} ta zona qo'shildi")
    
    print("\n🎉 Barcha test foydalanuvchilar yaratildi!")
    print("\n📋 Login ma'lumotlari:")
    print("🍳 Oshxona:")
    print("   Username: oshpaz1")
    print("   Password: 123456")
    print("   URL: http://127.0.0.1:8000/kitchen/")
    print("\n🚚 Kuryer 1:")
    print("   Username: kuryer1")
    print("   Password: 123456")
    print("   URL: http://127.0.0.1:8000/courier/")
    print("\n🚚 Kuryer 2:")
    print("   Username: kuryer2")
    print("   Password: 123456")
    print("   URL: http://127.0.0.1:8000/courier/")

if __name__ == "__main__":
    create_test_users()

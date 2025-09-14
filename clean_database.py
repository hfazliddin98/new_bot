#!/usr/bin/env python
"""
Ma'lumotlar bazasini tekshirish va tozalash skripti
"""
import os
import sys
import django

# Django sozlamalarini yuklash
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from django.contrib.auth import get_user_model
from kitchen.models import KitchenStaff
from courier.models import CourierStaff

User = get_user_model()

def check_database():
    """Ma'lumotlar bazasini tekshirish"""
    print("=== Ma'lumotlar bazasi holati ===")
    
    # Barcha foydalanuvchilar
    users = User.objects.all()
    print(f"Jami foydalanuvchilar: {users.count()}")
    
    for user in users:
        print(f"  User ID: {user.id}, Username: {user.username}, Role: {user.role}")
        
        # KitchenStaff tekshirish
        try:
            kitchen_staff = user.kitchenstaff
            print(f"    -> KitchenStaff ID: {kitchen_staff.id}")
        except:
            print(f"    -> KitchenStaff yo'q")
            
        # CourierStaff tekshirish
        try:
            courier_staff = user.courierstaff
            print(f"    -> CourierStaff ID: {courier_staff.id}")
        except:
            print(f"    -> CourierStaff yo'q")
    
    # Orphaned staff yozuvlari
    print("\n=== Yolg'iz qolgan KitchenStaff yozuvlari ===")
    orphaned_kitchen = KitchenStaff.objects.filter(user__isnull=True)
    for staff in orphaned_kitchen:
        print(f"  KitchenStaff ID: {staff.id}, User bo'sh")
    
    print("\n=== Yolg'iz qolgan CourierStaff yozuvlari ===")
    orphaned_courier = CourierStaff.objects.filter(user__isnull=True)
    for staff in orphaned_courier:
        print(f"  CourierStaff ID: {staff.id}, User bo'sh")

def clean_database():
    """Ma'lumotlar bazasini tozalash"""
    print("\n=== Ma'lumotlar bazasini tozalash ===")
    
    # Yolg'iz qolgan staff yozuvlarini o'chirish
    orphaned_kitchen = KitchenStaff.objects.filter(user__isnull=True)
    if orphaned_kitchen.exists():
        print(f"Yolg'iz qolgan {orphaned_kitchen.count()} ta KitchenStaff yozuvi o'chirildi")
        orphaned_kitchen.delete()
    
    orphaned_courier = CourierStaff.objects.filter(user__isnull=True)
    if orphaned_courier.exists():
        print(f"Yolg'iz qolgan {orphaned_courier.count()} ta CourierStaff yozuvi o'chirildi")
        orphaned_courier.delete()
    
    # Staff rolida bo'lgan lekin staff yozuvi yo'q foydalanuvchilar
    kitchen_users_without_staff = User.objects.filter(role='kitchen').exclude(kitchenstaff__isnull=False)
    if kitchen_users_without_staff.exists():
        print(f"KitchenStaff bo'lmagan {kitchen_users_without_staff.count()} ta kitchen User o'chirildi")
        kitchen_users_without_staff.delete()
    
    courier_users_without_staff = User.objects.filter(role='courier').exclude(courierstaff__isnull=False)
    if courier_users_without_staff.exists():
        print(f"CourierStaff bo'lmagan {courier_users_without_staff.count()} ta courier User o'chirildi")
        courier_users_without_staff.delete()
    
    print("Tozalash tugadi!")

if __name__ == "__main__":
    print("Ma'lumotlar bazasini tekshirish...")
    check_database()
    
    response = input("\nMa'lumotlar bazasini tozalashni xohlaysizmi? (y/n): ")
    if response.lower() == 'y':
        clean_database()
        print("\nTozalashdan keyin holat:")
        check_database()
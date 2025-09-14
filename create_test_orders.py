#!/usr/bin/env python
"""
Test buyurtma yaratish
"""
import os
import django

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from bot.models import TelegramUser, Product, Order, OrderItem, Dormitory
from decimal import Decimal

def create_test_orders():
    """Test buyurtmalar yaratish"""
    try:
        # Test foydalanuvchi topish yoki yaratish
        user, created = TelegramUser.objects.get_or_create(
            user_id=123456789,
            defaults={
                'username': 'test_user',
                'full_name': 'Test Foydalanuvchi',
                'phone_number': '+998901234567',
                'age': 20,
                'room_number': '205',
                'is_registered': True
            }
        )
        
        # Yotoqxona
        dormitory = Dormitory.objects.first()
        if dormitory:
            user.dormitory = dormitory
            user.save()
        
        # Mahsulotlar
        products = Product.objects.filter(is_available=True)[:3]
        
        if not products.exists():
            print("❌ Mahsulotlar topilmadi! Avval create_products.py ishga tushiring.")
            return
        
        # Test buyurtmalar yaratish
        for i in range(3):
            total_amount = Decimal('0')
            
            # Buyurtma yaratish
            order = Order.objects.create(
                user=user,
                dormitory=user.dormitory,
                delivery_address=f"{user.dormitory.name if user.dormitory else 'Test yotoqxona'}, {user.room_number}-xona",
                room_number=user.room_number,
                phone_number=user.phone_number,
                total_amount=Decimal('0'),  # Dastlab 0, keyin yangilanadi
                status='pending',
                notes=f'Test buyurtma #{i+1}'
            )
            
            # Buyurtma mahsulotlari
            for j, product in enumerate(products[:2]):  # Har buyurtmada 2 ta mahsulot
                quantity = j + 1
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total_amount += product.price * quantity
            
            # Umumiy summani yangilash
            order.total_amount = total_amount
            order.save()
            
            print(f"✅ Test buyurtma #{order.id} yaratildi - {total_amount:,} so'm")
        
        print("\n🎉 Test buyurtmalar muvaffaqiyatli yaratildi!")
        print("👨‍🍳 Kitchen dashboard'ga o'ting: http://127.0.0.1:8000/kitchen/")
        print("🔑 Admin login: admin / admin123")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    create_test_orders()
#!/usr/bin/env python
"""
Test ma'lumotlarni qo'shish skripti
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

from bot.models import Category, Product
from decimal import Decimal

def create_test_data():
    """Test ma'lumotlarni yaratish"""
    
    # Avval mavjud ma'lumotlarni o'chirish
    Product.objects.all().delete()
    Category.objects.all().delete()
    
    print("🗑️ Eski ma'lumotlar o'chirildi")
    
    # Kategoriyalar yaratish
    print("📂 Kategoriyalar yaratilmoqda...")
    
    fast_food = Category.objects.create(
        name='🍔 Fast Food',
        description='Tez tayyorlanadigan taomlar',
        is_active=True
    )
    
    pizza = Category.objects.create(
        name='🍕 Pizza', 
        description='Issiq pizzalar',
        is_active=True
    )
    
    drinks = Category.objects.create(
        name='🥤 Ichimliklar',
        description='Sovuq va issiq ichimliklar', 
        is_active=True
    )
    
    # Mahsulotlar yaratish
    print("🍽️ Mahsulotlar yaratilmoqda...")
    
    # Fast Food
    Product.objects.create(
        name='Big Burger',
        description='Katta burger, go\'sht, pomidor, salat bilan',
        price=Decimal('25000'),
        category=fast_food,
        is_available=True
    )
    
    Product.objects.create(
        name='Chicken Burger',
        description='Tovuq go\'shti bilan mazali burger',
        price=Decimal('22000'),
        category=fast_food,
        is_available=True
    )
    
    Product.objects.create(
        name='Fish Burger',
        description='Baliq go\'shti bilan burger',
        price=Decimal('20000'),
        category=fast_food,
        is_available=True
    )
    
    # Pizza
    Product.objects.create(
        name='Pepperoni Pizza',
        description='Pepperoni bilan klassik pizza',
        price=Decimal('45000'),
        category=pizza,
        is_available=True
    )
    
    Product.objects.create(
        name='Margherita Pizza',
        description='Pishloq va pomidor bilan',
        price=Decimal('35000'),
        category=pizza,
        is_available=True
    )
    
    Product.objects.create(
        name='Vegetarian Pizza',
        description='Sabzavotlar bilan pizza',
        price=Decimal('40000'),
        category=pizza,
        is_available=True
    )
    
    # Ichimliklar
    Product.objects.create(
        name='Coca Cola',
        description='Sovuq gaz ichimlik',
        price=Decimal('8000'),
        category=drinks,
        is_available=True
    )
    
    Product.objects.create(
        name='Fanta',
        description='Apelsin ta\'mli ichimlik',
        price=Decimal('8000'),
        category=drinks,
        is_available=True
    )
    
    Product.objects.create(
        name='Choy',
        description='Issiq qora choy',
        price=Decimal('5000'),
        category=drinks,
        is_available=True
    )
    
    Product.objects.create(
        name='Kofe',
        description='Issiq espresso kofe',
        price=Decimal('12000'),
        category=drinks,
        is_available=True
    )
    
    # Statistika
    print("\n✅ Test ma'lumotlari muvaffaqiyatli yaratildi!")
    print(f"📂 Kategoriyalar: {Category.objects.count()}")
    print(f"🍽️ Mahsulotlar: {Product.objects.count()}")
    print(f"✅ Faol kategoriyalar: {Category.objects.filter(is_active=True).count()}")
    print(f"✅ Mavjud mahsulotlar: {Product.objects.filter(is_available=True).count()}")
    
    print("\n📋 Kategoriyalar ro'yxati:")
    for cat in Category.objects.all():
        products_count = Product.objects.filter(category=cat).count()
        print(f"  - {cat.name}: {products_count} ta mahsulot")

if __name__ == "__main__":
    create_test_data()

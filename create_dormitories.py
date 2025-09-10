#!/usr/bin/env python
"""
Yotoqxonalar va yetkazib berish zonalari uchun test ma'lumotlar
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

from bot.models import DeliveryZone, Dormitory
from decimal import Decimal

def create_delivery_data():
    """Yetkazib berish ma'lumotlarini yaratish"""
    try:
        print("📍 Yetkazib berish zonalarini yaratish...")
        
        # Zonalar yaratish
        zone1, created = DeliveryZone.objects.get_or_create(
            name="Universitet hududi",
            defaults={
                'description': "Asosiy universitet kampusi",
                'delivery_fee': Decimal('5000'),
                'delivery_time': 15,
                'is_active': True
            }
        )
        
        zone2, created = DeliveryZone.objects.get_or_create(
            name="Shahar markazi",
            defaults={
                'description': "Shahar markazidagi yotoqxonalar",
                'delivery_fee': Decimal('8000'),
                'delivery_time': 25,
                'is_active': True
            }
        )
        
        zone3, created = DeliveryZone.objects.get_or_create(
            name="Chetki hududlar",
            defaults={
                'description': "Shaharga yaqin hududlar",
                'delivery_fee': Decimal('12000'),
                'delivery_time': 35,
                'is_active': True
            }
        )
        
        print("🏠 Yotoqxonalarni yaratish...")
        
        # Universitet hududi yotoqxonalari
        dorms_data = [
            {
                'name': "1-yotoqxona",
                'address': "Toshkent sh., Universitet ko'chasi 1-uy",
                'zone': zone1,
                'contact_person': "Aziz Karimov",
                'contact_phone': "+998901234567"
            },
            {
                'name': "2-yotoqxona", 
                'address': "Toshkent sh., Universitet ko'chasi 2-uy",
                'zone': zone1,
                'contact_person': "Dilshod Rakhimov",
                'contact_phone': "+998901234568"
            },
            {
                'name': "3-yotoqxona",
                'address': "Toshkent sh., Universitet ko'chasi 3-uy", 
                'zone': zone1,
                'contact_person': "Shohruh Alimov",
                'contact_phone': "+998901234569"
            },
            {
                'name': "4-yotoqxona",
                'address': "Toshkent sh., Universitet ko'chasi 4-uy",
                'zone': zone1,
                'contact_person': "Zarina Nazarova",
                'contact_phone': "+998901234570"
            },
            {
                'name': "5-yotoqxona",
                'address': "Toshkent sh., Universitet ko'chasi 5-uy",
                'zone': zone1,
                'contact_person': "Malika Tosheva",
                'contact_phone': "+998901234571"
            },
            
            # Shahar markazi yotoqxonalari
            {
                'name': "Markaz yotoqxonasi",
                'address': "Toshkent sh., Amir Temur ko'chasi 10-uy",
                'zone': zone2,
                'contact_person': "Bobur Kadirov",
                'contact_phone': "+998901234572"
            },
            {
                'name': "Yoshlar uyi",
                'address': "Toshkent sh., Navoi ko'chasi 25-uy",
                'zone': zone2,
                'contact_person': "Nodira Saidova",
                'contact_phone': "+998901234573"
            },
            {
                'name': "Talabalar shaharchasi",
                'address': "Toshkent sh., Mustaqillik ko'chasi 15-uy",
                'zone': zone2,
                'contact_person': "Jasur Rahmonov",
                'contact_phone': "+998901234574"
            },
            
            # Chetki hududlar
            {
                'name': "Qoraqamish yotoqxonasi",
                'address': "Toshkent sh., Qoraqamish tumani, Sharq ko'chasi 5-uy",
                'zone': zone3,
                'contact_person': "Rustam Umarov",
                'contact_phone': "+998901234575"
            },
            {
                'name': "Sergeli yotoqxonasi",
                'address': "Toshkent sh., Sergeli tumani, Yangi hayot ko'chasi 12-uy",
                'zone': zone3,
                'contact_person': "Feruza Karimova",
                'contact_phone': "+998901234576"
            }
        ]
        
        for dorm_data in dorms_data:
            dorm, created = Dormitory.objects.get_or_create(
                name=dorm_data['name'],
                defaults=dorm_data
            )
            if created:
                print(f"✅ {dorm.name} yaratildi")
        
        print(f"\n📊 Natijalar:")
        print(f"📍 Zonalar: {DeliveryZone.objects.count()}")
        print(f"🏠 Yotoqxonalar: {Dormitory.objects.count()}")
        
        print(f"\n🗂️ Zonalar bo'yicha yotoqxonalar:")
        for zone in DeliveryZone.objects.all():
            count = Dormitory.objects.filter(zone=zone).count()
            print(f"• {zone.name}: {count} ta yotoqxona")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    create_delivery_data()

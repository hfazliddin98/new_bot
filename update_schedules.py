#!/usr/bin/env python
"""
Yetkazib berish soatlari bilan yangilangan test ma'lumotlar
"""
import os
import sys
import django
from pathlib import Path
from datetime import time

# Django sozlamalarini yuklash
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from bot.models import DeliveryZone, Dormitory
from decimal import Decimal

def update_delivery_schedules():
    """Yetkazib berish jadvallarini yangilash"""
    try:
        print("⏰ Yetkazib berish soatlarini yangilash...")
        
        # Zonalarni yangilash
        zones_schedules = [
            {
                'name': "Universitet hududi",
                'working_hours_start': time(8, 0),  # 08:00
                'working_hours_end': time(22, 0),   # 22:00
                'is_24_hours': False
            },
            {
                'name': "Shahar markazi", 
                'working_hours_start': time(9, 0),  # 09:00
                'working_hours_end': time(23, 0),   # 23:00
                'is_24_hours': False
            },
            {
                'name': "Chetki hududlar",
                'working_hours_start': time(10, 0), # 10:00
                'working_hours_end': time(21, 0),   # 21:00
                'is_24_hours': False
            }
        ]
        
        for schedule in zones_schedules:
            try:
                zone = DeliveryZone.objects.get(name=schedule['name'])
                zone.working_hours_start = schedule['working_hours_start']
                zone.working_hours_end = schedule['working_hours_end']
                zone.is_24_hours = schedule['is_24_hours']
                zone.save()
                
                working_hours = zone.get_working_hours_display()
                print(f"✅ {zone.name}: {working_hours}")
                
            except DeliveryZone.DoesNotExist:
                print(f"❌ Zona topilmadi: {schedule['name']}")
        
        print(f"\n📊 Natijalar:")
        print(f"📍 Zonalar: {DeliveryZone.objects.count()}")
        print(f"🏠 Yotoqxonalar: {Dormitory.objects.count()}")
        
        print(f"\n🕐 Ish soatlari:")
        for zone in DeliveryZone.objects.all():
            print(f"• {zone.name}: {zone.get_working_hours_display()}")
            print(f"  Hozir ishlayapti: {'✅ Ha' if zone.is_working_now() else '❌ Yo\'q'}")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    update_delivery_schedules()

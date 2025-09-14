import os
import django
import requests
import subprocess
import time
import sys

# Django o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asosiy.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from kitchen.models import KitchenStaff

def test_kitchen_views():
    """Kitchen view'larini test qilish"""
    print("🧪 Kitchen view'larini test qilayapti...")
    
    client = Client()
    
    try:
        # 1. Kitchen asosiy sahifasini test qilish
        print("1️⃣ Kitchen asosiy sahifasini test qilish...")
        response = client.get('/kitchen/')
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ❌ Xatolik: {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')[:500]
                print(f"   Response: {content}")
        else:
            print("   ✅ Kitchen asosiy sahifa ishlayapti")
            
        # 2. Login sahifasini test qilish
        print("2️⃣ Login sahifasini test qilish...")
        response = client.get('/kitchen/login/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login sahifa ishlayapti")
        else:
            print(f"   ❌ Login sahifa xatosi: {response.status_code}")
            
        # 3. Admin user bilan login qilish
        print("3️⃣ Admin bilan login qilish...")
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            client.force_login(admin_user)
            print("   ✅ Admin bilan login muvaffaqiyatli")
            
            # 4. Dashboard sahifasini test qilish
            print("4️⃣ Dashboard sahifasini test qilish...")
            response = client.get('/kitchen/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Dashboard ishlayapti")
            else:
                print(f"   ❌ Dashboard xatosi: {response.status_code}")
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')[:500]
                    print(f"   Response: {content}")
                    
            # 5. Order detail sahifasini test qilish
            print("5️⃣ Order detail sahifasini test qilish...")
            response = client.get('/kitchen/order/6/')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Order detail ishlayapti")
            else:
                print(f"   ❌ Order detail xatosi: {response.status_code}")
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')[:500]
                    print(f"   Response: {content}")
        else:
            print("   ❌ Admin user topilmadi")
            
    except Exception as e:
        print(f"❌ Test xatosi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kitchen_views()
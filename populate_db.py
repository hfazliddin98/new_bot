from bot.models import Category, Product, Dormitory, DeliveryZone
from decimal import Decimal

print("🍕 Test ma'lumotlari yaratilmoqda...")

# 1. Kategoriyalar yaratish
categories_data = [
    {"name": "🍕 Pitsa", "description": "Turli xil pitsalar"},
    {"name": "🍔 Burger", "description": "Mazali burgerlar"},
    {"name": "🍗 Tovuq", "description": "Tovuq mahsulotlari"},
    {"name": "🍟 Gazak", "description": "Gazaklar va snacklar"},
    {"name": "🥤 Ichimlik", "description": "Sovuq va issiq ichimliklar"},
    {"name": "🍰 Shirinlik", "description": "Dessertlar va shirinliklar"}
]

created_categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data["name"],
        defaults={
            'description': cat_data["description"],
            'is_active': True
        }
    )
    created_categories.append(category)
    status = "✅ Yaratildi" if created else "ℹ️ Mavjud"
    print(f"{status}: {category.name}")

# 2. Mahsulotlar yaratish
products_data = [
    # Pitsa
    {"name": "Margarita", "category": "🍕 Pitsa", "price": 45000, "description": "Pomidor, mozzarella, rayhan"},
    {"name": "Pepperoni", "category": "🍕 Pitsa", "price": 55000, "description": "Pepperoni, mozzarella, pomidor sousi"},
    {"name": "Qo'ziqorin pitsasi", "category": "🍕 Pitsa", "price": 50000, "description": "Qo'ziqorin, mozzarella, pomidor"},
    
    # Burger
    {"name": "Cheeseburger", "category": "🍔 Burger", "price": 35000, "description": "Go'sht, pishloq, salat, pomidor"},
    {"name": "Big Burger", "category": "🍔 Burger", "price": 45000, "description": "Ikki qatlamli go'sht, pishloq, sous"},
    {"name": "Tovuq Burger", "category": "🍔 Burger", "price": 40000, "description": "Tovuq go'shti, salat, mayonez"},
    
    # Tovuq
    {"name": "KFC Style", "category": "🍗 Tovuq", "price": 38000, "description": "6 dona tovuq go'shti"},
    {"name": "Wings", "category": "🍗 Tovuq", "price": 32000, "description": "8 dona tovuq qanoti"},
    {"name": "Nuggets", "category": "🍗 Tovuq", "price": 28000, "description": "10 dona tovuq nuggets"},
    
    # Gazak
    {"name": "Free kartoshka", "category": "🍟 Gazak", "price": 15000, "description": "Katta portion fri"},
    {"name": "Onion Rings", "category": "🍟 Gazak", "price": 18000, "description": "Piyoz halqalari"},
    {"name": "Mozzarella Sticks", "category": "🍟 Gazak", "price": 22000, "description": "Pishloq tayoqchalari"},
    
    # Ichimlik
    {"name": "Coca Cola", "category": "🥤 Ichimlik", "price": 8000, "description": "0.5L Coca Cola"},
    {"name": "Fanta", "category": "🥤 Ichimlik", "price": 8000, "description": "0.5L Fanta"},
    {"name": "Choy", "category": "🥤 Ichimlik", "price": 5000, "description": "Issiq qora choy"},
    {"name": "Kofe", "category": "🥤 Ichimlik", "price": 12000, "description": "Americano kofe"},
    
    # Shirinlik
    {"name": "Shokoladli tort", "category": "🍰 Shirinlik", "price": 25000, "description": "Bir bo'lak shokoladli tort"},
    {"name": "Tiramisu", "category": "🍰 Shirinlik", "price": 28000, "description": "Italyan dessert"},
    {"name": "Muzqaymoq", "category": "🍰 Shirinlik", "price": 15000, "description": "Vanilli muzqaymoq"}
]

for prod_data in products_data:
    try:
        category = Category.objects.get(name=prod_data["category"])
        product, created = Product.objects.get_or_create(
            name=prod_data["name"],
            category=category,
            defaults={
                'description': prod_data["description"],
                'price': Decimal(str(prod_data["price"])),
                'is_active': True,
                'is_available': True
            }
        )
        status = "✅ Yaratildi" if created else "ℹ️ Mavjud"
        print(f"{status}: {product.name} - {product.price:,} so'm")
    except Exception as e:
        print(f"❌ Xatolik {prod_data['name']}: {e}")

# 3. Yotoqxonalar yaratish
dormitories_data = [
    {"name": "1-yotoqxona", "address": "Universitet ko'chasi 1"},
    {"name": "2-yotoqxona", "address": "Universitet ko'chasi 2"},
    {"name": "3-yotoqxona", "address": "Universitet ko'chasi 3"},
    {"name": "4-yotoqxona", "address": "Universitet ko'chasi 4"},
]

for dorm_data in dormitories_data:
    dormitory, created = Dormitory.objects.get_or_create(
        name=dorm_data["name"],
        defaults={
            'address': dorm_data["address"],
            'is_active': True
        }
    )
    status = "✅ Yaratildi" if created else "ℹ️ Mavjud"
    print(f"{status}: {dormitory.name}")

print("\n🎉 Test ma'lumotlari muvaffaqiyatli yaratildi!")
print(f"\n📊 Statistika:")
print(f"📂 Kategoriyalar: {Category.objects.count()}")
print(f"🍕 Mahsulotlar: {Product.objects.count()}")
print(f"🏠 Yotoqxonalar: {Dormitory.objects.count()}")

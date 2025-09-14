from django.core.management.base import BaseCommand
from bot.models import Dormitory, Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test ma\'lumotlari yaratish'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Test ma\'lumotlarini yaratish boshlandi...')
        
        # Test yotoqxonalari yaratish
        dormitories_data = [
            {
                'name': '1-bino A blok',
                'address': 'Universitetskaya ko\'chasi, 1-bino A blok',
                'delivery_fee': Decimal('3000'),
                'delivery_time': 20,
                'contact_person': 'Administator',
                'contact_phone': '+998901234567',
                'working_hours_start': '08:00',
                'working_hours_end': '22:00',
                'is_24_hours': False,
                'is_active': True
            },
            {
                'name': '1-bino B blok',
                'address': 'Universitetskaya ko\'chasi, 1-bino B blok',
                'delivery_fee': Decimal('2500'),
                'delivery_time': 15,
                'contact_person': 'Administator',
                'contact_phone': '+998901234568',
                'working_hours_start': '07:00',
                'working_hours_end': '23:00',
                'is_24_hours': False,
                'is_active': True
            },
            {
                'name': '2-bino',
                'address': 'Universitetskaya ko\'chasi, 2-bino',
                'delivery_fee': Decimal('5000'),
                'delivery_time': 30,
                'contact_person': 'Administator',
                'contact_phone': '+998901234569',
                'is_24_hours': True,
                'is_active': True
            },
            {
                'name': '3-bino C blok',
                'address': 'Universitetskaya ko\'chasi, 3-bino C blok',
                'delivery_fee': Decimal('0'),  # Bepul yetkazish
                'delivery_time': 25,
                'contact_person': 'Administator',
                'contact_phone': '+998901234570',
                'working_hours_start': '09:00',
                'working_hours_end': '21:00',
                'is_24_hours': False,
                'is_active': True
            }
        ]

        for dorm_data in dormitories_data:
            dorm, created = Dormitory.objects.get_or_create(
                name=dorm_data['name'],
                defaults=dorm_data
            )
            status = 'yaratildi' if created else 'mavjud'
            self.stdout.write(f'🏢 Yotoqxona: {dorm.name} - {status}')

        # Test kategoriyalar yaratish
        categories_data = [
            {'name': '🍕 Pitsa', 'is_active': True},
            {'name': '🍔 Burger', 'is_active': True},
            {'name': '🍜 Sho\'rva', 'is_active': True},
            {'name': '🥤 Ichimliklar', 'is_active': True},
            {'name': '🍰 Shirinliklar', 'is_active': True},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            status = 'yaratildi' if created else 'mavjud'
            self.stdout.write(f'📂 Kategoriya: {category.name} - {status}')

        # Test mahsulotlar yaratish
        products_data = [
            # Pitsa
            {'name': 'Margarita pitsa', 'category': '🍕 Pitsa', 'price': Decimal('25000'), 'description': 'Klassik margarita pitsa pomidor va mozzarella bilan'},
            {'name': 'Pepperoni pitsa', 'category': '🍕 Pitsa', 'price': Decimal('30000'), 'description': 'Pepperoni go\'shti va pishloq bilan'},
            {'name': 'Qo\'ziqorin pitsa', 'category': '🍕 Pitsa', 'price': Decimal('28000'), 'description': 'Yangi qo\'ziqorinlar va pishloq bilan'},
            
            # Burger
            {'name': 'Klassik burger', 'category': '🍔 Burger', 'price': Decimal('18000'), 'description': 'Mol go\'shti, sabzavot va sous bilan'},
            {'name': 'Chizburger', 'category': '🍔 Burger', 'price': Decimal('20000'), 'description': 'Mol go\'shti va pishloq bilan'},
            {'name': 'Tovuq burger', 'category': '🍔 Burger', 'price': Decimal('17000'), 'description': 'Tovuq go\'shti va sabzavot bilan'},
            
            # Sho'rva
            {'name': 'Lag\'mon', 'category': '🍜 Sho\'rva', 'price': Decimal('15000'), 'description': 'An\'anaviy lag\'mon go\'sht va sabzavot bilan'},
            {'name': 'Mastava', 'category': '🍜 Sho\'rva', 'price': Decimal('12000'), 'description': 'Guruch va sabzavot sho\'rvasi'},
            {'name': 'Borsh', 'category': '🍜 Sho\'rva', 'price': Decimal('14000'), 'description': 'Qizil borsh smetana bilan'},
            
            # Ichimliklar
            {'name': 'Coca Cola', 'category': '🥤 Ichimliklar', 'price': Decimal('5000'), 'description': '0.5L gazli ichimlik'},
            {'name': 'Apelsin sharbati', 'category': '🥤 Ichimliklar', 'price': Decimal('6000'), 'description': 'Tabiiy apelsin sharbati'},
            {'name': 'Choy', 'category': '🥤 Ichimliklar', 'price': Decimal('3000'), 'description': 'Qora yoki ko\'k choy'},
            
            # Shirinliklar
            {'name': 'Tiramisu', 'category': '🍰 Shirinliklar', 'price': Decimal('12000'), 'description': 'Klassik italyan deserti'},
            {'name': 'Shokoladli tort', 'category': '🍰 Shirinliklar', 'price': Decimal('10000'), 'description': 'Shokolad bilan tort'},
            {'name': 'Muzqaymoq', 'category': '🍰 Shirinliklar', 'price': Decimal('8000'), 'description': 'Turli xil ta\'mlar'},
        ]

        for prod_data in products_data:
            try:
                category = Category.objects.get(name=prod_data['category'])
                product, created = Product.objects.get_or_create(
                    name=prod_data['name'],
                    defaults={
                        'category': category,
                        'price': prod_data['price'],
                        'description': prod_data['description'],
                        'is_available': True
                    }
                )
                status = 'yaratildi' if created else 'mavjud'
                self.stdout.write(f'🍕 Mahsulot: {product.name} - {status}')
            except Category.DoesNotExist:
                self.stdout.write(f'❌ Kategoriya topilmadi: {prod_data["category"]}')

        # Statistika
        self.stdout.write('\n📊 Statistika:')
        self.stdout.write(f'🏢 Jami yotoqxonalar: {Dormitory.objects.count()}')
        self.stdout.write(f'📂 Jami kategoriyalar: {Category.objects.count()}')
        self.stdout.write(f'🍕 Jami mahsulotlar: {Product.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test ma\'lumotlari muvaffaqiyatli yaratildi!'))
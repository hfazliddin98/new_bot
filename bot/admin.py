from django.contrib import admin
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, Dormitory

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_display_name', 'username', 'phone_number', 'get_dormitory_display', 'room_number', 'age', 'is_registered', 'is_active', 'created_at')
    list_filter = ('is_registered', 'is_active', 'dormitory', 'age', 'created_at', 'registration_date')
    search_fields = ('username', 'first_name', 'last_name', 'full_name', 'user_id', 'phone_number', 'room_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'registration_date')
    fieldsets = (
        ('Telegram ma\'lumotlari', {
            'fields': ('user_id', 'username', 'first_name', 'last_name', 'full_name')
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('phone_number', 'age', 'is_active')
        }),
        ('Yashash joyi', {
            'fields': ('dormitory', 'room_number')
        }),
        ('Ro\'yxatdan o\'tish', {
            'fields': ('is_registered', 'registration_date'),
            'classes': ('collapse',)
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Ism'
    
    def get_dormitory_display(self, obj):
        return obj.dormitory.name if obj.dormitory else '-'
    get_dormitory_display.short_description = 'Yotoqxona'

@admin.register(Dormitory)
class DormitoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'address_short', 'delivery_fee', 'delivery_time', 'get_working_hours_display', 'contact_person', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_24_hours', 'delivery_fee', 'created_at')
    search_fields = ('name', 'address', 'contact_person', 'contact_phone')
    ordering = ('name',)
    list_editable = ('is_active', 'delivery_fee')
    date_hierarchy = 'created_at'
    actions = ['activate_dormitories', 'deactivate_dormitories', 'copy_delivery_settings']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'address', 'is_active'),
            'description': 'Yotoqxonaning asosiy ma\'lumotlari'
        }),
        ('Yetkazib berish sozlamalari', {
            'fields': ('delivery_fee', 'delivery_time'),
            'description': 'Yetkazib berish haqi va vaqti'
        }),
        ('Ish vaqti', {
            'fields': ('is_24_hours', 'working_hours_start', 'working_hours_end'),
            'description': 'Yetkazib berish ish vaqtlari'
        }),
        ('Kontakt ma\'lumotlari', {
            'fields': ('contact_person', 'contact_phone'),
            'description': 'Mas\'ul shaxs va telefon raqam'
        }),
        ('Koordinatalar', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
            'description': 'GPS koordinatalar (ixtiyoriy)'
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('notes',),
            'classes': ('collapse',),
            'description': 'Qo\'shimcha izohlar va ma\'lumotlar'
        })
    )
    
    def address_short(self, obj):
        """Qisqartirilgan manzil"""
        return obj.address[:50] + "..." if len(obj.address) > 50 else obj.address
    address_short.short_description = 'Manzil'
    
    def get_working_hours_display(self, obj):
        return obj.get_working_hours_display()
    get_working_hours_display.short_description = 'Ish vaqti'
    
    def activate_dormitories(self, request, queryset):
        """Yotoqxonalarni faollashtirish"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ta yotoqxona faollashtirildi.')
    activate_dormitories.short_description = 'Tanlangan yotoqxonalarni faollashtirish'
    
    def deactivate_dormitories(self, request, queryset):
        """Yotoqxonalarni faolsizlashtirish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ta yotoqxona faolsizlashtirildi.')
    deactivate_dormitories.short_description = 'Tanlangan yotoqxonalarni faolsizlashtirish'
    
    def copy_delivery_settings(self, request, queryset):
        """Yetkazib berish sozlamalarini nusxalash"""
        if queryset.count() > 1:
            first_dorm = queryset.first()
            updated = queryset.exclude(id=first_dorm.id).update(
                delivery_fee=first_dorm.delivery_fee,
                delivery_time=first_dorm.delivery_time,
                working_hours_start=first_dorm.working_hours_start,
                working_hours_end=first_dorm.working_hours_end,
                is_24_hours=first_dorm.is_24_hours
            )
            self.message_user(request, f'{updated} ta yotoqxonaga "{first_dorm.name}" sozlamalari nusxalandi.')
        else:
            self.message_user(request, 'Kamida 2 ta yotoqxona tanlang.', level='error')
    copy_delivery_settings.short_description = 'Birinchi tanlangan yotoqxona sozlamalarini boshqalariga nusxalash'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'get_total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__first_name', 'product__name')
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dormitory', 'status', 'get_delivery_time_display', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'dormitory', 'created_at')
    search_fields = ('user__first_name', 'delivery_address', 'phone_number', 'room_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Buyurtma ma\'lumotlari', {
            'fields': ('user', 'status', 'payment_method', 'total_amount')
        }),
        ('Yetkazib berish', {
            'fields': ('dormitory', 'delivery_address', 'room_number', 'phone_number', 'delivery_time')
        }),
        ('Qo\'shimcha', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_delivery_time_display(self, obj):
        if obj.delivery_time:
            return obj.delivery_time.strftime('%H:%M')
        return obj.get_delivery_time_display()
    get_delivery_time_display.short_description = 'Yetkazib berish vaqti'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total_price')
    list_filter = ('order__created_at',)
    search_fields = ('product__name', 'order__id')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'message_text_short', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('message_text', 'telegram_user__username')
    ordering = ('-created_at',)
    
    def message_text_short(self, obj):
        return obj.message_text[:50] + "..." if len(obj.message_text) > 50 else obj.message_text
    message_text_short.short_description = 'Xabar matni'

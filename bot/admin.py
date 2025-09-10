from django.contrib import admin
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem, DeliveryZone, Dormitory

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'get_display_name', 'username', 'phone_number', 'get_dormitory_display', 'room_number', 'age', 'is_registered', 'is_active', 'created_at')
    list_filter = ('is_registered', 'is_active', 'dormitory__zone', 'dormitory', 'age', 'created_at', 'registration_date')
    search_fields = ('username', 'first_name', 'last_name', 'full_name', 'user_id', 'phone_number', 'room_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'registration_date')
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Ism'
    
    def get_dormitory_display(self, obj):
        return obj.dormitory.name if obj.dormitory else '-'
    get_dormitory_display.short_description = 'Yotoqxona'

@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_fee', 'delivery_time', 'get_working_hours_display', 'is_working_now', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_24_hours', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def is_working_now(self, obj):
        return "✅ Ha" if obj.is_working_now() else "❌ Yo'q"
    is_working_now.short_description = 'Hozir ishlaydi'

@admin.register(Dormitory)
class DormitoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'contact_person', 'contact_phone', 'is_active', 'created_at')
    list_filter = ('zone', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'contact_person')
    ordering = ('zone', 'name')

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
    list_display = ('id', 'user', 'dormitory', 'delivery_zone', 'status', 'get_delivery_time_display', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'dormitory', 'delivery_zone', 'created_at')
    search_fields = ('user__first_name', 'delivery_address', 'phone_number', 'room_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
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

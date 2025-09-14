from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with role-based fields
    """
    
    # Fields to display in admin list
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active_worker', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active_worker', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    # Fieldsets for editing user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role va Qo\'shimcha Ma\'lumotlar', {
            'fields': ('role', 'phone_number', 'address', 'is_active_worker')
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields for adding new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role va Qo\'shimcha Ma\'lumotlar', {
            'fields': ('role', 'phone_number', 'address', 'is_active_worker')
        }),
    )
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_name(self, obj):
        """Get user's full name for admin display"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'To\'liq ismi'
    
    actions = ['create_kitchen_staff', 'create_courier_staff', 'assign_kitchen_role', 'assign_courier_role']
    
    def create_kitchen_staff(self, request, queryset):
        """Tanlangan userlar uchun KitchenStaff yaratish"""
        from kitchen.models import KitchenStaff
        created_count = 0
        
        for user in queryset.filter(role='kitchen'):
            staff, created = KitchenStaff.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': user.get_full_name() or user.username,
                    'phone_number': user.phone_number or '',
                    'position': 'Oshpaz'
                }
            )
            if created:
                created_count += 1
        
        self.message_user(request, f"{created_count} ta oshxona xodimi yaratildi.")
    create_kitchen_staff.short_description = "Tanlangan userlar uchun oshxona xodimi yaratish"
    
    def create_courier_staff(self, request, queryset):
        """Tanlangan userlar uchun CourierStaff yaratish"""
        from courier.models import CourierStaff
        created_count = 0
        
        for user in queryset.filter(role='courier'):
            staff, created = CourierStaff.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': user.get_full_name() or user.username,
                    'phone_number': user.phone_number or '',
                    'vehicle_type': 'Piyoda'
                }
            )
            if created:
                created_count += 1
        
        self.message_user(request, f"{created_count} ta kuryer yaratildi.")
    create_courier_staff.short_description = "Tanlangan userlar uchun kuryer yaratish"
    
    def assign_kitchen_role(self, request, queryset):
        """Tanlangan userlarni kitchen role'ga o'rnatish va KitchenStaff yaratish"""
        from kitchen.models import KitchenStaff
        updated_count = 0
        created_count = 0
        
        for user in queryset:
            # Role'ni kitchen'ga o'rnatish
            user.role = 'kitchen'
            user.save()
            updated_count += 1
            
            # KitchenStaff yaratish
            staff, created = KitchenStaff.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': user.get_full_name() or user.username,
                    'phone_number': user.phone_number or '',
                    'position': 'Oshpaz'
                }
            )
            if created:
                created_count += 1
        
        self.message_user(request, 
            f"{updated_count} ta user oshpaz role'ga o'rnatildi. "
            f"{created_count} ta oshxona xodimi yaratildi."
        )
    assign_kitchen_role.short_description = "Tanlangan userlarni oshpaz qilish"
    
    def assign_courier_role(self, request, queryset):
        """Tanlangan userlarni courier role'ga o'rnatish va CourierStaff yaratish"""
        from courier.models import CourierStaff
        updated_count = 0
        created_count = 0
        
        for user in queryset:
            # Role'ni courier'ga o'rnatish
            user.role = 'courier'
            user.save()
            updated_count += 1
            
            # CourierStaff yaratish
            staff, created = CourierStaff.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': user.get_full_name() or user.username,
                    'phone_number': user.phone_number or '',
                    'vehicle_type': 'Piyoda'
                }
            )
            if created:
                created_count += 1
        
        self.message_user(request, 
            f"{updated_count} ta user kuryer role'ga o'rnatildi. "
            f"{created_count} ta kuryer yaratildi."
        )
    assign_courier_role.short_description = "Tanlangan userlarni kuryer qilish"

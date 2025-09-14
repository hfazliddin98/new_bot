from django.contrib import admin
from .models import KitchenStaff, OrderProgress
from users.forms import CreateKitchenStaffForm

@admin.register(KitchenStaff)
class KitchenStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'position', 'phone_number', 'is_active', 'created_at')
    list_filter = ('position', 'is_active', 'created_at')
    search_fields = ('full_name', 'user__username', 'phone_number')
    ordering = ('full_name',)
    
    # Yangi oshpaz qo'shish uchun form
    add_form = CreateKitchenStaffForm
    
    def get_form(self, request, obj=None, **kwargs):
        """Yangi qo'shishda custom form ishlatish"""
        if obj is None:  # Yangi obyekt yaratilayotgan bo'lsa
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)
    
    def get_fieldsets(self, request, obj=None):
        """Yangi qo'shishda boshqa fieldset ishlatish"""
        if obj is None:  # Yangi obyekt yaratilayotgan bo'lsa
            return (
                ('Foydalanuvchi Ma\'lumotlari', {
                    'fields': ('username', 'password', 'first_name', 'last_name', 'email')
                }),
                ('Oshpaz Ma\'lumotlari', {
                    'fields': ('full_name', 'phone_number', 'position')
                }),
            )
        else:  # Mavjud obyektni tahrirlash
            return (
                ('Asosiy Ma\'lumotlar', {
                    'fields': ('user', 'full_name', 'position')
                }),
                ('Aloqa Ma\'lumotlari', {
                    'fields': ('phone_number',)
                }),
                ('Holat', {
                    'fields': ('is_active',)
                }),
            )
    
    def save_model(self, request, obj, form, change):
        # User'ni kitchen role'ga o'rnatish
        if obj.user:
            obj.user.role = 'kitchen'
            obj.user.save()
        super().save_model(request, obj, form, change)

@admin.register(OrderProgress)
class OrderProgressAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'kitchen_staff', 'preparation_time', 'started_at', 'completed_at')
    list_filter = ('status', 'kitchen_staff', 'order__created_at')
    search_fields = ('order__id', 'order__user__full_name', 'notes')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)

from django.contrib import admin
from .models import CourierStaff, Delivery
from users.forms import CreateCourierStaffForm

@admin.register(CourierStaff)
class CourierStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'vehicle_type', 'phone_number', 'is_active', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'is_active', 'is_available', 'created_at')
    search_fields = ('full_name', 'user__username', 'phone_number')
    ordering = ('full_name',)
    
    # Yangi kuryer qo'shish uchun form
    add_form = CreateCourierStaffForm
    
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
                ('Kuryer Ma\'lumotlari', {
                    'fields': ('full_name', 'phone_number', 'vehicle_type')
                }),
            )
        else:  # Mavjud obyektni tahrirlash
            return (
                ('Asosiy Ma\'lumotlar', {
                    'fields': ('user', 'full_name', 'vehicle_type')
                }),
                ('Aloqa Ma\'lumotlari', {
                    'fields': ('phone_number',)
                }),

                ('Holat', {
                    'fields': ('is_active', 'is_available')
                }),
            )
    
    def save_model(self, request, obj, form, change):
        # User'ni courier role'ga o'rnatish
        if obj.user:
            obj.user.role = 'courier'
            obj.user.save()
        super().save_model(request, obj, form, change)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'status', 'picked_up_at', 'delivered_at', 'rating')
    list_filter = ('status', 'courier', 'order__created_at', 'rating')
    search_fields = ('order__id', 'order__user__full_name', 'courier__full_name', 'delivery_notes')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)

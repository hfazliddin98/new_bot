from django.contrib import admin
from .models import CourierStaff, Delivery

@admin.register(CourierStaff)
class CourierStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'vehicle_type', 'phone_number', 'is_active', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'is_active', 'is_available', 'delivery_zones', 'created_at')
    search_fields = ('full_name', 'user__username', 'phone_number')
    ordering = ('full_name',)
    filter_horizontal = ('delivery_zones',)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'courier', 'status', 'picked_up_at', 'delivered_at', 'rating')
    list_filter = ('status', 'courier', 'order__created_at', 'rating')
    search_fields = ('order__id', 'order__user__full_name', 'courier__full_name', 'delivery_notes')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)

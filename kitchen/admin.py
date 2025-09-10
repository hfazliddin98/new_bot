from django.contrib import admin
from .models import KitchenStaff, OrderProgress

@admin.register(KitchenStaff)
class KitchenStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'position', 'phone_number', 'is_active', 'created_at')
    list_filter = ('position', 'is_active', 'created_at')
    search_fields = ('full_name', 'user__username', 'phone_number')
    ordering = ('full_name',)

@admin.register(OrderProgress)
class OrderProgressAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'kitchen_staff', 'preparation_time', 'started_at', 'completed_at')
    list_filter = ('status', 'kitchen_staff', 'order__created_at')
    search_fields = ('order__id', 'order__user__full_name', 'notes')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)

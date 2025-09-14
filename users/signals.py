from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from kitchen.models import KitchenStaff
from courier.models import CourierStaff

User = get_user_model()


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """
    User yaratilganda yoki role o'zgarganda tegishli Staff profile yaratish
    """
    if instance.role == 'kitchen':
        # KitchenStaff yaratish yoki yangilash
        kitchen_staff, kitchen_created = KitchenStaff.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
                'phone_number': instance.phone_number or '',
                'position': 'Oshpaz'
            }
        )
        
        # Agar user yangi emas va KitchenStaff yangi yaratilmagan bo'lsa, ma'lumotlarni yangilash
        if not created and not kitchen_created:
            kitchen_staff.full_name = instance.get_full_name() or instance.username
            kitchen_staff.phone_number = instance.phone_number or ''
            kitchen_staff.save()
            
    elif instance.role == 'courier':
        # CourierStaff yaratish yoki yangilash
        courier_staff, courier_created = CourierStaff.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
                'phone_number': instance.phone_number or '',
                'vehicle_type': 'Piyoda'
            }
        )
        
        # Agar user yangi emas va CourierStaff yangi yaratilmagan bo'lsa, ma'lumotlarni yangilash
        if not created and not courier_created:
            courier_staff.full_name = instance.get_full_name() or instance.username
            courier_staff.phone_number = instance.phone_number or ''
            courier_staff.save()


@receiver(post_save, sender=User)
def update_staff_profile(sender, instance, **kwargs):
    """
    User ma'lumotlari o'zgarganda tegishli Staff profilelarni yangilash
    """
    # KitchenStaff yangilash
    try:
        kitchen_staff = KitchenStaff.objects.get(user=instance)
        kitchen_staff.full_name = instance.get_full_name() or instance.username
        kitchen_staff.phone_number = instance.phone_number or ''
        kitchen_staff.save()
    except KitchenStaff.DoesNotExist:
        pass
    
    # CourierStaff yangilash
    try:
        courier_staff = CourierStaff.objects.get(user=instance)
        courier_staff.full_name = instance.get_full_name() or instance.username
        courier_staff.phone_number = instance.phone_number or ''
        courier_staff.save()
    except CourierStaff.DoesNotExist:
        pass
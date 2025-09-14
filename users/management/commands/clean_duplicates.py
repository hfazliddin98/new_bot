from django.core.management.base import BaseCommand
from kitchen.models import KitchenStaff
from courier.models import CourierStaff
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Duplicate staff entries ni tozalash'

    def handle(self, *args, **options):
        # KitchenStaff duplicates ni tozalash
        kitchen_duplicates = 0
        for user in User.objects.filter(role='kitchen'):
            kitchen_staffs = KitchenStaff.objects.filter(user=user)
            if kitchen_staffs.count() > 1:
                # Eng oxirgisidan boshqa hammasini o'chirish
                latest = kitchen_staffs.last()
                duplicates_to_delete = kitchen_staffs.exclude(id=latest.id)
                count = duplicates_to_delete.count()
                duplicates_to_delete.delete()
                kitchen_duplicates += count
                self.stdout.write(f"User {user.username} uchun {count} ta duplicate KitchenStaff o'chirildi")

        # CourierStaff duplicates ni tozalash
        courier_duplicates = 0
        for user in User.objects.filter(role='courier'):
            courier_staffs = CourierStaff.objects.filter(user=user)
            if courier_staffs.count() > 1:
                # Eng oxirgisidan boshqa hammasini o'chirish
                latest = courier_staffs.last()
                duplicates_to_delete = courier_staffs.exclude(id=latest.id)
                count = duplicates_to_delete.count()
                duplicates_to_delete.delete()
                courier_duplicates += count
                self.stdout.write(f"User {user.username} uchun {count} ta duplicate CourierStaff o'chirildi")

        self.stdout.write(
            self.style.SUCCESS(
                f'Tozalash yakunlandi: {kitchen_duplicates} KitchenStaff, {courier_duplicates} CourierStaff duplicates o\'chirildi'
            )
        )
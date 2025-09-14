from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db import models
from users.decorators import admin_required
from .forms import CreateKitchenStaffForm, CreateCourierStaffForm, EditKitchenStaffForm, EditCourierStaffForm, UniversalStaffForm
from kitchen.models import KitchenStaff
from courier.models import CourierStaff
from django.contrib.auth import get_user_model

User = get_user_model()


@admin_required
def admin_dashboard(request):
    """Admin dashboard sahifasi"""
    from bot.models import Dormitory
    context = {
        'total_users': User.objects.distinct().count(),
        'kitchen_staff_count': KitchenStaff.objects.distinct().count(),
        'courier_staff_count': CourierStaff.objects.distinct().count(),
        'admin_count': User.objects.filter(role='admin').distinct().count(),
        'dormitories_count': Dormitory.objects.distinct().count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def add_kitchen_staff(request):
    """Yangi oshpaz qo'shish sahifasi"""
    if request.method == 'POST':
        form = CreateKitchenStaffForm(request.POST)
        if form.is_valid():
            try:
                kitchen_staff = form.save()
                messages.success(request, f"Oshpaz {kitchen_staff.full_name} muvaffaqiyatli qo'shildi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    else:
        form = CreateKitchenStaffForm()
    
    return render(request, 'admin_panel/add_kitchen_staff.html', {'form': form})


@admin_required
def add_courier_staff(request):
    """Yangi kuryer qo'shish sahifasi"""
    if request.method == 'POST':
        form = CreateCourierStaffForm(request.POST)
        if form.is_valid():
            try:
                courier_staff = form.save()
                messages.success(request, f"Kuryer {courier_staff.full_name} muvaffaqiyatli qo'shildi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    else:
        form = CreateCourierStaffForm()
    
    return render(request, 'admin_panel/add_courier_staff.html', {'form': form})


@admin_required
def staff_list(request):
    """Barcha xodimlar ro'yxati"""
    # Oxirgi yaratilgan entries ni olish (duplicate larni yo'q qilish uchun)
    kitchen_staff = KitchenStaff.objects.select_related('user').order_by('-id')
    courier_staff = CourierStaff.objects.select_related('user').order_by('-id')
    
    # Manual duplicate removal - faqat unique user_id lar
    seen_kitchen_users = set()
    unique_kitchen_staff = []
    for staff in kitchen_staff:
        if staff.user_id not in seen_kitchen_users:
            unique_kitchen_staff.append(staff)
            seen_kitchen_users.add(staff.user_id)
    
    seen_courier_users = set()
    unique_courier_staff = []
    for staff in courier_staff:
        if staff.user_id not in seen_courier_users:
            unique_courier_staff.append(staff)
            seen_courier_users.add(staff.user_id)
    
    context = {
        'kitchen_staff': unique_kitchen_staff,
        'courier_staff': unique_courier_staff,
    }
    return render(request, 'admin_panel/staff_list.html', context)


@admin_required
@admin_required
def edit_kitchen_staff(request, staff_id):
    """Oshpaz tahrirlash"""
    try:
        kitchen_staff = KitchenStaff.objects.get(id=staff_id)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Oshpaz topilmadi!")
        return redirect('admin_panel:staff_list')
    except KitchenStaff.MultipleObjectsReturned:
        # Agar bir nechta obyekt bo'lsa, eng oxirgisini olish
        kitchen_staff = KitchenStaff.objects.filter(id=staff_id).last()
        messages.warning(request, "Duplicate entries aniqlandi, oxirgisi tanlandi.")
    
    if request.method == 'POST':
        form = EditKitchenStaffForm(request.POST, instance=kitchen_staff)
        if form.is_valid():
            try:
                kitchen_staff = form.save()
                # Agar parol o'zgartirilgan bo'lsa, session hash-ni yangilash
                if form.cleaned_data.get('password'):
                    update_session_auth_hash(request, kitchen_staff.user)
                messages.success(request, f"Oshpaz {kitchen_staff.full_name} ma'lumotlari yangilandi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    else:
        form = EditKitchenStaffForm(instance=kitchen_staff)
    
    return render(request, 'admin_panel/edit_kitchen_staff.html', {
        'form': form,
        'staff': kitchen_staff,
        'title': 'Oshpaz tahrirlash'
    })


@admin_required  
def edit_courier_staff(request, staff_id):
    """Kuryer tahrirlash"""
    try:
        courier_staff = CourierStaff.objects.get(id=staff_id)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Kuryer topilmadi!")
        return redirect('admin_panel:staff_list')
    except CourierStaff.MultipleObjectsReturned:
        # Agar bir nechta obyekt bo'lsa, eng oxirgisini olish
        courier_staff = CourierStaff.objects.filter(id=staff_id).last()
        messages.warning(request, "Duplicate entries aniqlandi, oxirgisi tanlandi.")
    
    if request.method == 'POST':
        form = EditCourierStaffForm(request.POST, instance=courier_staff)
        if form.is_valid():
            try:
                courier_staff = form.save()
                # Agar parol o'zgartirilgan bo'lsa, session hash-ni yangilash
                if form.cleaned_data.get('password'):
                    update_session_auth_hash(request, courier_staff.user)
                messages.success(request, f"Kuryer {courier_staff.full_name} ma'lumotlari yangilandi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    else:
        form = EditCourierStaffForm(instance=courier_staff)
    
    return render(request, 'admin_panel/edit_courier_staff.html', {
        'form': form,
        'staff': courier_staff,
        'title': 'Kuryer tahrirlash'
    })


@admin_required
def delete_kitchen_staff(request, staff_id):
    """Oshpazni o'chirish"""
    try:
        kitchen_staff = KitchenStaff.objects.get(id=staff_id)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Oshpaz topilmadi!")
        return redirect('admin_panel:staff_list')
    except KitchenStaff.MultipleObjectsReturned:
        kitchen_staff = KitchenStaff.objects.filter(id=staff_id).last()
    
    if request.method == 'POST':
        user = kitchen_staff.user
        full_name = kitchen_staff.full_name
        
        # KitchenStaff va User ni o'chirish
        kitchen_staff.delete()
        user.delete()
        
        messages.success(request, f"Oshpaz {full_name} muvaffaqiyatli o'chirildi!")
        return redirect('admin_panel:staff_list')
    
    return render(request, 'admin_panel/confirm_delete.html', {
        'staff': kitchen_staff,
        'staff_type': 'oshpaz',
        'title': 'Oshpazni o\'chirish'
    })


@admin_required
def delete_courier_staff(request, staff_id):
    """Kuryerni o'chirish"""
    try:
        courier_staff = CourierStaff.objects.get(id=staff_id)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Kuryer topilmadi!")
        return redirect('admin_panel:staff_list')
    except CourierStaff.MultipleObjectsReturned:
        courier_staff = CourierStaff.objects.filter(id=staff_id).last()
    
    if request.method == 'POST':
        user = courier_staff.user
        full_name = courier_staff.full_name
        
        # CourierStaff va User ni o'chirish
        courier_staff.delete()
        user.delete()
        
        messages.success(request, f"Kuryer {full_name} muvaffaqiyatli o'chirildi!")
        return redirect('admin_panel:staff_list')
    
    return render(request, 'admin_panel/confirm_delete.html', {
        'staff': courier_staff,
        'staff_type': 'kuryer',
        'title': 'Kuryerni o\'chirish'
    })


@admin_required
def add_staff(request):
    """Umumiy xodim qo'shish"""
    if request.method == 'POST':
        form = UniversalStaffForm(request.POST)
        if form.is_valid():
            try:
                staff = form.save()
                role = form.cleaned_data['role']
                if role == 'kitchen':
                    messages.success(request, f"Oshpaz {staff.full_name} muvaffaqiyatli qo'shildi!")
                else:
                    messages.success(request, f"Kuryer {staff.full_name} muvaffaqiyatli qo'shildi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik: {str(e)}")
    else:
        form = UniversalStaffForm()
    
    return render(request, 'admin_panel/add_staff.html', {
        'form': form,
        'title': 'Xodim qo\'shish'
    })


@admin_required
def edit_staff(request, staff_type, staff_id):
    """Umumiy xodim tahrirlash"""
    staff = None
    
    try:
        if staff_type == 'kitchen':
            try:
                staff = KitchenStaff.objects.get(id=staff_id)
            except KitchenStaff.MultipleObjectsReturned:
                # Agar bir nechta bo'lsa, oxirgisini olish
                staff = KitchenStaff.objects.filter(id=staff_id).last()
                messages.warning(request, "Bir nechta bir xil xodim topildi, oxirgisi tanlandi.")
            except KitchenStaff.DoesNotExist:
                messages.error(request, "Oshpaz topilmadi!")
                return redirect('admin_panel:staff_list')
        elif staff_type == 'courier':
            try:
                staff = CourierStaff.objects.get(id=staff_id)
            except CourierStaff.MultipleObjectsReturned:
                # Agar bir nechta bo'lsa, oxirgisini olish
                staff = CourierStaff.objects.filter(id=staff_id).last()
                messages.warning(request, "Bir nechta bir xil xodim topildi, oxirgisi tanlandi.")
            except CourierStaff.DoesNotExist:
                messages.error(request, "Kuryer topilmadi!")
                return redirect('admin_panel:staff_list')
        else:
            messages.error(request, "Noto'g'ri xodim turi!")
            return redirect('admin_panel:staff_list')
    except Exception as e:
        messages.error(request, f"Xatolik yuz berdi: {str(e)}")
        return redirect('admin_panel:staff_list')
    
    if request.method == 'POST':
        form = UniversalStaffForm(request.POST, instance=staff)
        if form.is_valid():
            try:
                updated_staff = form.save()
                # Parol o'zgartirilgan bo'lsa session ni yangilash
                if form.cleaned_data.get('password1'):
                    update_session_auth_hash(request, updated_staff.user)
                
                messages.success(request, f"Xodim {updated_staff.full_name} muvaffaqiyatli yangilandi!")
                return redirect('admin_panel:staff_list')
            except Exception as e:
                messages.error(request, f"Xatolik: {str(e)}")
    else:
        form = UniversalStaffForm(instance=staff)
    
    return render(request, 'admin_panel/edit_staff.html', {
        'form': form,
        'staff': staff,
        'staff_type': staff_type,
        'title': f"Xodimni tahrirlash - {staff.full_name}"
    })


@admin_required
def dormitories_list(request):
    """Yotoqxonalar ro'yxati"""
    from bot.models import Dormitory
    dormitories = Dormitory.objects.all().order_by('name')
    return render(request, 'admin_panel/dormitories_list.html', {
        'dormitories': dormitories,
        'title': 'Yotoqxonalar ro\'yxati'
    })


@admin_required
def add_dormitory(request):
    """Yangi yotoqxona qo'shish"""
    from bot.models import Dormitory
    from decimal import Decimal
    
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        contact_person = request.POST.get('contact_person', '')
        contact_phone = request.POST.get('contact_phone', '')
        delivery_fee = request.POST.get('delivery_fee', '0')
        delivery_time = request.POST.get('delivery_time', '30')
        working_hours_start = request.POST.get('working_hours_start', '09:00')
        working_hours_end = request.POST.get('working_hours_end', '23:00')
        is_24_hours = request.POST.get('is_24_hours') == 'on'
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        notes = request.POST.get('notes', '')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            dormitory = Dormitory.objects.create(
                name=name,
                address=address,
                contact_person=contact_person,
                contact_phone=contact_phone,
                delivery_fee=Decimal(delivery_fee) if delivery_fee else Decimal('0'),
                delivery_time=int(delivery_time) if delivery_time else 30,
                working_hours_start=working_hours_start,
                working_hours_end=working_hours_end,
                is_24_hours=is_24_hours,
                latitude=Decimal(latitude) if latitude else None,
                longitude=Decimal(longitude) if longitude else None,
                notes=notes,
                is_active=is_active
            )
            messages.success(request, f"Yotoqxona '{dormitory.name}' muvaffaqiyatli qo'shildi!")
            return redirect('admin_panel:dormitories_list')
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return render(request, 'admin_panel/add_dormitory.html', {
        'title': 'Yangi yotoqxona qo\'shish'
    })


@admin_required
def edit_dormitory(request, dormitory_id):
    """Yotoqxona tahrirlash"""
    from bot.models import Dormitory
    from decimal import Decimal
    
    try:
        dormitory = Dormitory.objects.get(id=dormitory_id)
    except Dormitory.DoesNotExist:
        messages.error(request, "Yotoqxona topilmadi!")
        return redirect('admin_panel:dormitories_list')
    
    if request.method == 'POST':
        dormitory.name = request.POST.get('name')
        dormitory.address = request.POST.get('address')
        dormitory.contact_person = request.POST.get('contact_person', '')
        dormitory.contact_phone = request.POST.get('contact_phone', '')
        delivery_fee = request.POST.get('delivery_fee', '0')
        delivery_time = request.POST.get('delivery_time', '30')
        working_hours_start = request.POST.get('working_hours_start', '09:00')
        working_hours_end = request.POST.get('working_hours_end', '23:00')
        is_24_hours = request.POST.get('is_24_hours') == 'on'
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        dormitory.notes = request.POST.get('notes', '')
        dormitory.is_active = request.POST.get('is_active') == 'on'
        
        try:
            dormitory.delivery_fee = Decimal(delivery_fee) if delivery_fee else Decimal('0')
            dormitory.delivery_time = int(delivery_time) if delivery_time else 30
            dormitory.working_hours_start = working_hours_start
            dormitory.working_hours_end = working_hours_end
            dormitory.is_24_hours = is_24_hours
            dormitory.latitude = Decimal(latitude) if latitude else None
            dormitory.longitude = Decimal(longitude) if longitude else None
            dormitory.save()
            messages.success(request, f"Yotoqxona '{dormitory.name}' muvaffaqiyatli yangilandi!")
            return redirect('admin_panel:dormitories_list')
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return render(request, 'admin_panel/edit_dormitory.html', {
        'dormitory': dormitory,
        'title': f'Yotoqxona tahrirlash - {dormitory.name}'
    })


@admin_required
def delete_dormitory(request, dormitory_id):
    """Yotoqxona o'chirish"""
    from bot.models import Dormitory
    
    try:
        dormitory = Dormitory.objects.get(id=dormitory_id)
    except Dormitory.DoesNotExist:
        messages.error(request, "Yotoqxona topilmadi!")
        return redirect('admin_panel:dormitories_list')
    
    if request.method == 'POST':
        name = dormitory.name
        dormitory.delete()
        messages.success(request, f"Yotoqxona '{name}' muvaffaqiyatli o'chirildi!")
        return redirect('admin_panel:dormitories_list')
    
    return render(request, 'admin_panel/confirm_delete.html', {
        'item': dormitory,
        'item_type': 'yotoqxona',
        'title': f'Yotoqxona o\'chirish - {dormitory.name}'
    })

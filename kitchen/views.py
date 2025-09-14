from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib import messages
from datetime import datetime, timedelta
import json

from bot.models import Order, OrderItem, Category, Product
from .models import KitchenStaff, OrderProgress
from users.decorators import kitchen_required

@kitchen_required
def dashboard(request):
    """Oshxona dashboard"""
    try:
        # Foydalanuvchi oshxona xodimimi?
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect(request.user.get_dashboard_url())
    
    # Mavjud ready buyurtmalar uchun Delivery obyektlarini yaratish
    from courier.models import Delivery
    ready_orders_without_delivery = Order.objects.filter(
        orderprogress__status='ready',
        delivery__isnull=True
    )
    
    for order in ready_orders_without_delivery:
        Delivery.objects.get_or_create(
            order=order,
            defaults={
                'status': 'ready',
                'delivery_address': f"{order.dormitory.name}, {order.room_number}-xona" if order.dormitory and order.room_number else order.address or "Manzil ko'rsatilmagan"
            }
        )
    
    # Statistika
    today = timezone.now().date()
    
    stats = {
        'new_orders': Order.objects.filter(
            created_at__date=today,
            orderprogress__isnull=True
        ).count(),
        'preparing_orders': OrderProgress.objects.filter(
            status='preparing',
            order__created_at__date=today
        ).count(),
        'ready_orders': OrderProgress.objects.filter(
            status='ready',
            order__created_at__date=today
        ).count(),
        'today_total': Order.objects.filter(created_at__date=today).count(),
    }
    
    # Mahsulotlar statistikasi
    categories_count = Category.objects.filter(is_active=True).count()
    products_count = Product.objects.filter(is_available=True).count()
    
    # So'nggi buyurtmalar
    recent_orders = Order.objects.filter(
        created_at__date=today
    ).select_related('user', 'dormitory', 'orderprogress').prefetch_related('items__product').order_by('-created_at')[:10]
    
    context = {
        'kitchen_staff': kitchen_staff,
        'stats': stats,
        'recent_orders': recent_orders,
        'categories_count': categories_count,
        'products_count': products_count,
    }
    
    return render(request, 'kitchen/dashboard.html', context)

@kitchen_required
def orders_list(request):
    """Barcha buyurtmalar ro'yxati"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    orders = Order.objects.select_related('user', 'dormitory').prefetch_related('items__product', 'orderprogress').order_by('-created_at')
    
    # Filter
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'new':
            orders = orders.filter(orderprogress__isnull=True)
        else:
            orders = orders.filter(orderprogress__status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    
    return render(request, 'kitchen/orders.html', context)

@kitchen_required
def order_detail(request, order_id):
    """Buyurtma tafsilotlari"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Order progress yaratish yoki olish
    progress, created = OrderProgress.objects.get_or_create(
        order=order,
        defaults={
            'kitchen_staff': kitchen_staff,
            'status': 'received'
        }
    )
    
    context = {
        'order': order,
        'progress': progress,
        'order_items': order.items.all(),
    }
    
    return render(request, 'kitchen/order_detail.html', context)

@kitchen_required
def start_order(request, order_id):
    """Buyurtmani tayyorlashni boshlash"""
    if request.method == 'POST':
        try:
            kitchen_staff = KitchenStaff.objects.get(user=request.user)
            order = get_object_or_404(Order, id=order_id)
            
            progress, created = OrderProgress.objects.get_or_create(
                order=order,
                defaults={
                    'kitchen_staff': kitchen_staff,
                    'status': 'preparing',
                    'started_at': timezone.now()
                }
            )
            
            if not created and progress.status == 'received':
                progress.status = 'preparing'
                progress.kitchen_staff = kitchen_staff
                progress.started_at = timezone.now()
                progress.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@kitchen_required
def order_detail(request, order_id):
    """Buyurtma tafsilotlari"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product').all()
    
    try:
        progress = order.orderprogress
    except OrderProgress.DoesNotExist:
        progress = None
    
    context = {
        'order': order,
        'order_items': order_items,
        'progress': progress,
        'kitchen_staff': kitchen_staff,
    }
    
    return render(request, 'kitchen/order_detail.html', context)

@kitchen_required
def complete_order(request, order_id):
    """Buyurtmani tayyor deb belgilash"""
    if request.method == 'POST':
        try:
            kitchen_staff = KitchenStaff.objects.get(user=request.user)
            order = get_object_or_404(Order, id=order_id)
            
            progress = get_object_or_404(OrderProgress, order=order)
            progress.status = 'ready'
            progress.completed_at = timezone.now()
            progress.save()
            
            # Order holatini yangilash
            order.status = 'ready'
            order.save()
            
            # Kuryer uchun Delivery obyektini yaratish
            from courier.models import Delivery
            delivery, created = Delivery.objects.get_or_create(
                order=order,
                defaults={
                    'status': 'ready',
                    'delivery_address': f"{order.dormitory.name}, {order.room_number}-xona" if order.dormitory and order.room_number else order.address or "Manzil ko'rsatilmagan"
                }
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@kitchen_required
def preparing_orders(request):
    """Tayyorlanayotgan buyurtmalar"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    orders = Order.objects.filter(
        orderprogress__status='preparing'
    ).select_related('user', 'dormitory').prefetch_related('items__product', 'orderprogress').order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Tayyorlanayotgan buyurtmalar',
    }
    
    return render(request, 'kitchen/preparing.html', context)

@kitchen_required
def ready_orders(request):
    """Tayyor buyurtmalar"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    orders = Order.objects.filter(
        orderprogress__status='ready'
    ).select_related('user', 'dormitory').prefetch_related('items__product', 'orderprogress', 'delivery').order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Tayyor buyurtmalar',
    }
    
    return render(request, 'kitchen/ready.html', context)

@kitchen_required
def create_delivery(request, order_id):
    """Buyurtma uchun yetkazib berish yaratish"""
    if request.method == 'POST':
        try:
            kitchen_staff = KitchenStaff.objects.get(user=request.user)
            order = get_object_or_404(Order, id=order_id)
            
            # Buyurtma tayyor holatidami?
            if not hasattr(order, 'orderprogress') or order.orderprogress.status != 'ready':
                return JsonResponse({'success': False, 'message': 'Buyurtma tayyor emas'})
            
            # Delivery allaqachon mavjudmi?
            if hasattr(order, 'delivery'):
                return JsonResponse({'success': False, 'message': 'Yetkazib berish allaqachon yaratilgan'})
            
            # Delivery yaratish
            from courier.models import Delivery
            delivery = Delivery.objects.create(
                order=order,
                status='ready'
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

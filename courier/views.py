from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.contrib import messages
from datetime import datetime, timedelta

from bot.models import Order
from kitchen.models import OrderProgress
from .models import CourierStaff, Delivery
from users.decorators import courier_required

@courier_required
def dashboard(request):
    """Kuryer dashboard"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect(request.user.get_dashboard_url())
    
    # Statistika
    today = timezone.now().date()
    
    # Tayyor buyurtmalarni Delivery obyektlarini yaratish
    ready_orders_query = Order.objects.filter(
        orderprogress__status='ready',
        delivery__isnull=True
    )
    
    for order in ready_orders_query:
        # Agar delivery obyekt mavjud bo'lmasa, yaratamiz
        if not hasattr(order, 'delivery'):
            Delivery.objects.get_or_create(
                order=order,
                defaults={'status': 'ready'}
            )
    
    # Kuryer statistikasi
    stats = {
        'ready_orders': Delivery.objects.filter(
            status='ready',
            courier__isnull=True
        ).count(),
        'on_way_orders': Delivery.objects.filter(
            courier=courier,
            status__in=['picked_up', 'on_way']
        ).count(),
        'delivered_today': Delivery.objects.filter(
            courier=courier,
            status='delivered',
            delivered_at__date=today
        ).count(),
        'total_earnings': Delivery.objects.filter(
            courier=courier,
            status='delivered'
        ).aggregate(total=Sum('order__delivery_fee'))['total'] or 0,
    }
    
    # Faol yetkazishlar
    active_deliveries = Delivery.objects.filter(
        courier=courier,
        status__in=['assigned', 'picked_up', 'on_way']
    ).select_related('order__user', 'order__dormitory').order_by('-updated_at')
    
    # Tayyor buyurtmalar
    ready_orders = Delivery.objects.filter(
        status='ready',
        courier__isnull=True
    ).select_related('order__user', 'order__dormitory').order_by('-updated_at')[:5]
    
    context = {
        'courier': courier,
        'stats': stats,
        'active_deliveries': active_deliveries,
        'ready_orders': ready_orders,
    }
    
    return render(request, 'courier/dashboard.html', context)

@courier_required
def toggle_availability(request):
    """Kuryer mavjudligini o'zgartirish"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            courier.is_available = not courier.is_available
            courier.save()
            
            return JsonResponse({'success': True, 'is_available': courier.is_available})
            
        except CourierStaff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kuryer topilmadi'})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})



@courier_required
def deliveries_list(request):
    """Yetkazib berishlar ro'yxati"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect(request.user.get_dashboard_url())
    
    # Tayyor buyurtmalarni Delivery obyektlarini yaratish
    ready_orders = Order.objects.filter(
        orderprogress__status='ready',
        delivery__isnull=True
    )
    
    for order in ready_orders:
        # Agar delivery obyekt mavjud bo'lmasa, yaratamiz
        if not hasattr(order, 'delivery'):
            Delivery.objects.get_or_create(
                order=order,
                defaults={'status': 'ready'}
            )
    
    # Barcha yetkazib berishlar
    deliveries = Delivery.objects.filter(
        Q(courier=courier) |  # Kuryer buyurtmalari
        Q(status='ready', courier__isnull=True)  # Tayyor buyurtmalar
    ).select_related('order__user', 'order__dormitory', 'courier', 'order__orderprogress').order_by('-updated_at')
    
    # Filter
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'ready':
            deliveries = deliveries.filter(status='ready', courier__isnull=True)
        elif status_filter == 'assigned':
            deliveries = deliveries.filter(status='assigned', courier=courier)
        else:
            deliveries = deliveries.filter(status=status_filter)
    
    context = {
        'deliveries': deliveries,
        'status_filter': status_filter,
    }
    
    return render(request, 'courier/deliveries.html', context)

@courier_required
def take_order(request, delivery_id):
    """Yetkazib berishni olish"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id)
            
            # Kuryer mavjudmi?
            if not courier.is_available:
                return JsonResponse({'success': False, 'message': 'Siz hozir mavjud emassiz'})
            
            # Yetkazib berish tayyor holatidami?
            if delivery.status != 'ready':
                return JsonResponse({'success': False, 'message': 'Bu yetkazib berish tayyor emas'})
            
            # Allaqachon olinganmi?
            if delivery.courier:
                return JsonResponse({'success': False, 'message': 'Bu yetkazib berish allaqachon olingan'})
            
            # Kuryer tayinlash
            delivery.courier = courier
            delivery.status = 'assigned'
            delivery.assigned_at = timezone.now()
            delivery.save()
            
            # OrderProgress holatini yangilash
            if hasattr(delivery.order, 'orderprogress'):
                delivery.order.orderprogress.status = 'picked_up'
                delivery.order.orderprogress.save()
            
            return JsonResponse({'success': True})
            
        except CourierStaff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kuryer topilmadi'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@courier_required
def pickup_order(request, delivery_id):
    """Buyurtmani olib ketish"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, courier=courier)
            
            if delivery.status != 'assigned':
                return JsonResponse({'success': False, 'message': 'Bu buyurtma tayinlanmagan'})
            
            delivery.status = 'picked_up'
            delivery.picked_up_at = timezone.now()
            delivery.save()
            
            # OrderProgress holatini yangilash
            if hasattr(delivery.order, 'orderprogress'):
                delivery.order.orderprogress.status = 'picked_up'
                delivery.order.orderprogress.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@courier_required
def start_delivery(request, delivery_id):
    """Yetkazib berishni boshlash"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, courier=courier)
            
            delivery.status = 'on_way'
            delivery.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@courier_required
def complete_delivery(request, delivery_id):
    """Yetkazib berishni yakunlash"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, courier=courier)
            
            if delivery.status != 'on_way':
                return JsonResponse({'success': False, 'message': 'Bu buyurtma yo\'lda emas'})
            
            delivery.status = 'delivered'
            delivery.delivered_at = timezone.now()
            delivery.save()
            
            # Order holatini yangilash
            delivery.order.status = 'delivered'
            delivery.order.save()
            
            # OrderProgress holatini yangilash
            if hasattr(delivery.order, 'orderprogress'):
                delivery.order.orderprogress.status = 'delivered'
                delivery.order.orderprogress.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@courier_required
def delivery_history(request):
    """Yetkazib berish tarixi"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect(request.user.get_dashboard_url())
    
    # Filter
    period_filter = request.GET.get('period')
    deliveries = Delivery.objects.filter(courier=courier)
    
    today = timezone.now().date()
    
    if period_filter == 'today':
        deliveries = deliveries.filter(delivered_at__date=today)
    elif period_filter == 'week':
        week_start = today - timedelta(days=today.weekday())
        deliveries = deliveries.filter(delivered_at__date__gte=week_start)
    elif period_filter == 'month':
        deliveries = deliveries.filter(
            delivered_at__year=today.year,
            delivered_at__month=today.month
        )
    
    deliveries = deliveries.select_related('order__user', 'order__dormitory').order_by('-delivered_at')
    
    # Statistics
    today_count = Delivery.objects.filter(
        courier=courier, 
        delivered_at__date=today
    ).count()
    
    week_start = today - timedelta(days=today.weekday())
    week_count = Delivery.objects.filter(
        courier=courier,
        delivered_at__date__gte=week_start
    ).count()
    
    month_count = Delivery.objects.filter(
        courier=courier,
        delivered_at__year=today.year,
        delivered_at__month=today.month
    ).count()
    
    total_count = Delivery.objects.filter(courier=courier).count()
    
    context = {
        'deliveries': deliveries,
        'period_filter': period_filter,
        'today_count': today_count,
        'week_count': week_count,
        'month_count': month_count,
        'total_count': total_count,
    }
    
    return render(request, 'courier/history.html', context)

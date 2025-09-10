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

@login_required
def dashboard(request):
    """Kuryer dashboard"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect('admin:index')
    
    # Statistika
    today = timezone.now().date()
    
    stats = {
        'ready_orders': Order.objects.filter(
            orderprogress__status='ready',
            delivery__isnull=True
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
    
    # Tayyor buyurtmalar (kuryer zonasida)
    courier_zones = courier.delivery_zones.all()
    ready_orders = Order.objects.filter(
        orderprogress__status='ready',
        delivery__isnull=True,
        delivery_zone__in=courier_zones
    ).select_related('user', 'dormitory').order_by('-created_at')[:5]
    
    context = {
        'courier': courier,
        'stats': stats,
        'active_deliveries': active_deliveries,
        'ready_orders': ready_orders,
    }
    
    return render(request, 'courier/dashboard.html', context)

@login_required
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

@login_required
def take_order(request, order_id):
    """Buyurtmani olish"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            order = get_object_or_404(Order, id=order_id)
            
            # Kuryer mavjudmi?
            if not courier.is_available:
                return JsonResponse({'success': False, 'message': 'Siz hozir mavjud emassiz'})
            
            # Buyurtma tayyor holatidami?
            if not hasattr(order, 'orderprogress') or order.orderprogress.status != 'ready':
                return JsonResponse({'success': False, 'message': 'Buyurtma tayyor emas'})
            
            # Delivery yaratish
            delivery, created = Delivery.objects.get_or_create(
                order=order,
                defaults={
                    'courier': courier,
                    'status': 'assigned'
                }
            )
            
            if not created:
                return JsonResponse({'success': False, 'message': 'Bu buyurtma allaqachon olingan'})
            
            # Order progress yangilash
            order.orderprogress.status = 'picked_up'
            order.orderprogress.save()
            
            return JsonResponse({'success': True})
            
        except CourierStaff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kuryer topilmadi'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
def deliveries_list(request):
    """Yetkazib berishlar ro'yxati"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect('admin:index')
    
    # Barcha yetkazib berishlar (kuryer zonasida)
    courier_zones = courier.delivery_zones.all()
    deliveries = Delivery.objects.filter(
        Q(courier=courier) |
        Q(order__delivery_zone__in=courier_zones, status='ready')
    ).select_related('order__user', 'order__dormitory', 'courier').order_by('-updated_at')
    
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

@login_required
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
            
            return JsonResponse({'success': True})
            
        except CourierStaff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kuryer topilmadi'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
def pickup_order(request, delivery_id):
    """Buyurtmani olib ketish"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, courier=courier)
            
            delivery.status = 'picked_up'
            delivery.picked_up_at = timezone.now()
            delivery.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
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

@login_required
def complete_delivery(request, delivery_id):
    """Yetkazib berishni yakunlash"""
    if request.method == 'POST':
        try:
            courier = CourierStaff.objects.get(user=request.user)
            delivery = get_object_or_404(Delivery, id=delivery_id, courier=courier)
            
            delivery.status = 'delivered'
            delivery.delivered_at = timezone.now()
            delivery.save()
            
            # Order holatini yangilash
            delivery.order.status = 'delivered'
            delivery.order.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
def delivery_history(request):
    """Yetkazib berish tarixi"""
    try:
        courier = CourierStaff.objects.get(user=request.user)
    except CourierStaff.DoesNotExist:
        messages.error(request, "Siz kuryer emassiz!")
        return redirect('admin:index')
    
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

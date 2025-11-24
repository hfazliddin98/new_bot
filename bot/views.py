from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import logging
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem
from users.decorators import admin_required

logger = logging.getLogger(__name__)

# Webhook olib tashlandi - faqat polling rejimi ishlatiladi

def set_webhook(request):
    """Webhook o'rnatish uchun view"""
    webhook_url = "https://yourdomain.com/bot/webhook/"  # Bu yerga o'z domeningizni yozing
    try:
        result = bot.set_webhook(url=webhook_url)
        if result:
            return JsonResponse({"status": "success", "message": "Webhook o'rnatildi"})
        else:
            return JsonResponse({"status": "error", "message": "Webhook o'rnatilmadi"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@admin_required
def bot_stats(request):
    """Bot statistikasi"""
    total_users = TelegramUser.objects.count()
    active_users = TelegramUser.objects.filter(is_active=True).count()
    total_messages = Message.objects.count()
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    
    # So'nggi buyurtmalar
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_messages': total_messages,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_categories': total_categories,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'bot/stats.html', context)

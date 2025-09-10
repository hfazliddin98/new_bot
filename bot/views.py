from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import telebot
from .models import TelegramUser, Message, Category, Product, Cart, Order, OrderItem
from .bot_handlers import handle_telegram_update

# Bot instanceni yaratish
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

@csrf_exempt
def telegram_webhook(request):
    """Telegram webhook uchun view"""
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            handle_telegram_update(json_data)
            return HttpResponse("OK")
        except Exception as e:
            print(f"Webhook xatosi: {e}")
            return HttpResponse("Error", status=500)
    return HttpResponse("Method not allowed", status=405)

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

from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('set_webhook/', views.set_webhook, name='set_webhook'),
    path('stats/', views.bot_stats, name='bot_stats'),
]

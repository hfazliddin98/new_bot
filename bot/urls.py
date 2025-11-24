from django.urls import path
from . import views

urlpatterns = [
    # Webhook olib tashlandi - faqat polling
    path('stats/', views.bot_stats, name='bot_stats'),
]

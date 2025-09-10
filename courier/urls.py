from django.urls import path
from . import views

app_name = 'courier'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('deliveries/', views.deliveries_list, name='deliveries'),
    path('history/', views.delivery_history, name='history'),
    path('take-order/<int:delivery_id>/', views.take_order, name='take_order'),
    path('pickup-order/<int:delivery_id>/', views.pickup_order, name='pickup_order'),
    path('start-delivery/<int:delivery_id>/', views.start_delivery, name='start_delivery'),
    path('complete-delivery/<int:delivery_id>/', views.complete_delivery, name='complete_delivery'),
]

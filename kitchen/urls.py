from django.urls import path
from . import views
from . import product_views

app_name = 'kitchen'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.orders_list, name='orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('start-order/<int:order_id>/', views.start_order, name='start_order'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('preparing/', views.preparing_orders, name='preparing'),
    path('ready/', views.ready_orders, name='ready'),
    path('create-delivery/<int:order_id>/', views.create_delivery, name='create_delivery'),
    
    # Mahsulot boshqaruvi
    path('products/', product_views.manage_products, name='manage_products'),
    path('products/add/', product_views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', product_views.edit_product, name='edit_product'),
    path('products/toggle/<int:product_id>/', product_views.toggle_product_availability, name='toggle_product'),
    
    # Kategoriya boshqaruvi
    path('categories/', product_views.manage_categories, name='manage_categories'),
    path('categories/add/', product_views.add_category, name='add_category'),
    
    # Jonli buyurtmalar
    path('live-orders/', product_views.live_orders, name='live_orders'),
]

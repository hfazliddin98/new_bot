from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    # Eski URLlar (backward compatibility uchun)
    path('add-kitchen-staff/', views.add_kitchen_staff, name='add_kitchen_staff'),
    path('add-courier-staff/', views.add_courier_staff, name='add_courier_staff'),
    path('edit-kitchen-staff/<int:staff_id>/', views.edit_kitchen_staff, name='edit_kitchen_staff'),
    path('edit-courier-staff/<int:staff_id>/', views.edit_courier_staff, name='edit_courier_staff'),
    path('delete-kitchen-staff/<int:staff_id>/', views.delete_kitchen_staff, name='delete_kitchen_staff'),
    path('delete-courier-staff/<int:staff_id>/', views.delete_courier_staff, name='delete_courier_staff'),
    
    # Yangi umumiy URLlar
    path('add-staff/', views.add_staff, name='add_staff'),
    path('edit-staff/<str:staff_type>/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    
    # Boshqa sahifalar
    path('staff-list/', views.staff_list, name='staff_list'),
    
    # Yotoqxonalar
    path('dormitories/', views.dormitories_list, name='dormitories_list'),
    path('add-dormitory/', views.add_dormitory, name='add_dormitory'),
    path('edit-dormitory/<int:dormitory_id>/', views.edit_dormitory, name='edit_dormitory'),
    path('delete-dormitory/<int:dormitory_id>/', views.delete_dormitory, name='delete_dormitory'),
]
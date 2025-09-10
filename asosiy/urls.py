from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

def dashboard_redirect(request):
    """Login qilgandan so'ng tegishli dashboardga yo'naltirish"""
    if request.user.is_authenticated:
        # Oshxona xodimi?
        try:
            from kitchen.models import KitchenStaff
            KitchenStaff.objects.get(user=request.user)
            return redirect('kitchen:dashboard')
        except:
            pass
        
        # Kuryer?
        try:
            from courier.models import CourierStaff
            CourierStaff.objects.get(user=request.user)
            return redirect('courier:dashboard')
        except:
            pass
        
        # Admin
        return redirect('admin:index')
    
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/', include('bot.urls')),
    path('kitchen/', include('kitchen.urls')),
    path('courier/', include('courier.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard_redirect, name='dashboard_redirect'),
]

# Media fayllar uchun URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

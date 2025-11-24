from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from users import views as user_views

def dashboard_redirect(request):
    """Login qilgandan so'ng tegishli dashboardga yo'naltirish"""
    if request.user.is_authenticated:
        # User'ning default dashboard URL'ini olish
        dashboard_url = request.user.get_dashboard_url()
        return redirect(dashboard_url)
    
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('users.urls')),
    path('bot/', include('bot.urls')),
    path('kitchen/', include('kitchen.urls')),
    path('courier/', include('courier.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', user_views.user_profile, name='user_profile'),
    path('settings/', user_views.user_settings, name='user_settings'),
    path('', dashboard_redirect, name='dashboard_redirect'),
]

# Media fayllar uchun URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleBasedAccessMiddleware:
    """
    Role-based access control middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URL patterns for different roles
        self.kitchen_urls = [
            '/kitchen/',
            '/kitchen/dashboard/',
            '/kitchen/orders/',
            '/kitchen/preparing/',
            '/kitchen/ready/',
            '/kitchen/categories/',
            '/kitchen/products/',
        ]
        
        self.courier_urls = [
            '/courier/',
            '/courier/dashboard/',
            '/courier/deliveries/',
            '/courier/history/',
        ]
        
        self.admin_urls = [
            '/admin-panel/',
            '/bot/stats/',
        ]
        
        # URLs that don't require role checking
        self.public_urls = [
            '/admin/',
            '/accounts/',
            '/login/',
            '/logout/',
            '/static/',
            '/media/',
            '/',
        ]

    def __call__(self, request):
        # Skip middleware for public URLs
        if any(request.path.startswith(url) for url in self.public_urls):
            response = self.get_response(request)
            return response
        
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check kitchen access
        if any(request.path.startswith(url) for url in self.kitchen_urls):
            if not request.user.can_access_kitchen():
                return HttpResponseForbidden(
                    "Sizda oshxona paneliga kirish huquqi yo'q. "
                    "Agar bu xato bo'lsa, administrator bilan bog'laning."
                )
        
        # Check courier access
        elif any(request.path.startswith(url) for url in self.courier_urls):
            if not request.user.can_access_courier():
                # Foydalanuvchi mos sahifasiga yo'naltirish
                if request.user.role == 'kitchen':
                    return redirect('/kitchen/')
                elif request.user.role == 'admin':
                    return redirect('/admin-panel/')
                else:
                    return redirect('login')
        
        # Check admin access
        elif any(request.path.startswith(url) for url in self.admin_urls):
            if not request.user.is_admin_user():
                # Foydalanuvchi mos sahifasiga yo'naltirish
                if request.user.role == 'kitchen':
                    return redirect('/kitchen/')
                elif request.user.role == 'courier':
                    return redirect('/courier/')
                else:
                    return redirect('login')
        
        response = self.get_response(request)
        return response


class LoginRedirectMiddleware:
    """
    Redirect users to appropriate dashboard after login based on their role
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if user just logged in and is on root URL
        if (request.user.is_authenticated and 
            request.path == '/' and 
            request.method == 'GET'):
            
            # Redirect to user's default dashboard
            dashboard_url = request.user.get_dashboard_url()
            return redirect(dashboard_url)
        
        return response
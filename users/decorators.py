from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def kitchen_required(view_func):
    """
    Decorator to require kitchen access for views
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_access_kitchen():
            # Foydalanuvchi mos sahifasiga yo'naltirish
            if request.user.role == 'courier':
                return redirect('courier:dashboard')
            elif request.user.role == 'admin':
                return redirect('admin_panel:dashboard')
            else:
                return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def courier_required(view_func):
    """
    Decorator to require courier access for views
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.can_access_courier():
            # Foydalanuvchi mos sahifasiga yo'naltirish
            if request.user.role == 'kitchen':
                return redirect('kitchen:dashboard')
            elif request.user.role == 'admin':
                return redirect('admin_panel:dashboard')
            else:
                return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator to require admin access for views
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_admin_user():
            # Foydalanuvchi mos sahifasiga yo'naltirish
            if request.user.role == 'kitchen':
                return redirect('kitchen:dashboard')
            elif request.user.role == 'courier':
                return redirect('courier:dashboard')
            else:
                return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
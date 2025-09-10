from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from bot.models import Category, Product
from .models import KitchenStaff

@login_required
def manage_products(request):
    """Mahsulotlarni boshqarish"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    # Kategoriyalar va mahsulotlar
    categories = Category.objects.filter(is_active=True).order_by('name')
    products = Product.objects.select_related('category').order_by('category__name', 'name')
    
    context = {
        'categories': categories,
        'products': products,
        'page_title': 'Mahsulotlarni boshqarish',
    }
    
    return render(request, 'kitchen/products.html', context)

@login_required
def add_product(request):
    """Yangi mahsulot qo'shish"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_id = request.POST.get('category')
            
            if not all([name, description, price, category_id]):
                messages.error(request, "Barcha maydonlarni to'ldiring!")
                return redirect('kitchen:manage_products')
            
            category = get_object_or_404(Category, id=category_id)
            
            # Mahsulot yaratish
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                is_available=True
            )
            
            messages.success(request, f"'{product.name}' mahsuloti muvaffaqiyatli qo'shildi!")
            return redirect('kitchen:manage_products')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            return redirect('kitchen:manage_products')
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    context = {
        'categories': categories,
        'page_title': 'Yangi mahsulot qo\'shish',
    }
    
    return render(request, 'kitchen/add_product.html', context)

@login_required
def edit_product(request, product_id):
    """Mahsulotni tahrirlash"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.price = request.POST.get('price', product.price)
            
            category_id = request.POST.get('category')
            if category_id:
                product.category = get_object_or_404(Category, id=category_id)
            
            is_available = request.POST.get('is_available') == 'on'
            product.is_available = is_available
            
            product.save()
            
            messages.success(request, f"'{product.name}' mahsuloti yangilandi!")
            return redirect('kitchen:manage_products')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    context = {
        'product': product,
        'categories': categories,
        'page_title': f'{product.name} tahrirlash',
    }
    
    return render(request, 'kitchen/edit_product.html', context)

@login_required
def toggle_product_availability(request, product_id):
    """Mahsulot mavjudligini o'zgartirish"""
    if request.method == 'POST':
        try:
            kitchen_staff = KitchenStaff.objects.get(user=request.user)
            product = get_object_or_404(Product, id=product_id)
            
            product.is_available = not product.is_available
            product.save()
            
            status = "mavjud" if product.is_available else "mavjud emas"
            return JsonResponse({
                'success': True, 
                'message': f"'{product.name}' {status} deb belgilandi!",
                'is_available': product.is_available
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
def manage_categories(request):
    """Kategoriyalarni boshqarish"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    categories = Category.objects.all().order_by('name')
    
    # Har bir kategoriyada nechta mahsulot borligini hisoblash
    for category in categories:
        category.product_count = Product.objects.filter(category=category).count()
    
    context = {
        'categories': categories,
        'page_title': 'Kategoriyalarni boshqarish',
    }
    
    return render(request, 'kitchen/categories.html', context)

@login_required
def add_category(request):
    """Yangi kategoriya qo'shish"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            if not name:
                messages.error(request, "Kategoriya nomi majburiy!")
                return redirect('kitchen:manage_categories')
            
            # Kategoriya yaratish
            category = Category.objects.create(
                name=name,
                description=description,
                is_active=True
            )
            
            messages.success(request, f"'{category.name}' kategoriyasi qo'shildi!")
            return redirect('kitchen:manage_categories')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            return redirect('kitchen:manage_categories')
    
    context = {
        'page_title': 'Yangi kategoriya qo\'shish',
    }
    
    return render(request, 'kitchen/add_category.html', context)

@login_required
def live_orders(request):
    """Jonli buyurtmalar monitoringi"""
    try:
        kitchen_staff = KitchenStaff.objects.get(user=request.user)
    except KitchenStaff.DoesNotExist:
        messages.error(request, "Siz oshxona xodimi emassiz!")
        return redirect('admin:index')
    
    from django.utils import timezone
    # Bugungi barcha buyurtmalar
    today = timezone.now().date()
    
    from bot.models import Order
    orders = Order.objects.filter(
        created_at__date=today
    ).select_related('user', 'dormitory', 'orderprogress').prefetch_related(
        'items__product'
    ).order_by('-created_at')
    
    context = {
        'orders': orders,
        'page_title': 'Jonli buyurtmalar',
    }
    
    return render(request, 'kitchen/live_orders.html', context)

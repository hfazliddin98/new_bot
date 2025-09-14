from django import forms
from django.contrib.auth import get_user_model
from kitchen.models import KitchenStaff
from courier.models import CourierStaff

User = get_user_model()


class CreateKitchenStaffForm(forms.ModelForm):
    """Oshpaz yaratish uchun form"""
    
    username = forms.CharField(
        max_length=150,
        label="Foydalanuvchi nomi",
        help_text="Kirishda foydalaniladigan nom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Parol",
        help_text="Kamida 8 ta belgi"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Parolni tasdiqlash",
        help_text="Yuqoridagi parolni takrorlang"
    )
    first_name = forms.CharField(
        max_length=30,
        label="Ism",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Familya",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = KitchenStaff
        fields = ['phone_number']
        labels = {
            'phone_number': 'Telefon raqam',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+998901234567',
                'pattern': r'\+998[0-9]{9}',
                'title': 'Telefon raqamni +998XXXXXXXXX formatida kiriting'
            }),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if not phone.startswith('+998'):
            phone = '+998' + phone.lstrip('+').lstrip('998')
        
        # Telefon raqam formatini tekshirish
        import re
        if not re.match(r'^\+998[0-9]{9}$', phone):
            raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
        
        return phone
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2

    def save(self, commit=True):
        # User yaratish
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
            email='',
            role='kitchen'
        )
        
        # KitchenStaff yaratish
        kitchen_staff = super().save(commit=False)
        kitchen_staff.user = user
        kitchen_staff.position = 'Oshpaz'  # Avtomatik lavozim
        kitchen_staff.full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        if commit:
            kitchen_staff.save()
        
        return kitchen_staff


class CreateCourierStaffForm(forms.ModelForm):
    """Kuryer yaratish uchun form"""
    
    username = forms.CharField(
        max_length=150,
        label="Foydalanuvchi nomi",
        help_text="Kirishda foydalaniladigan nom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Parol",
        help_text="Kamida 8 ta belgi"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Parolni tasdiqlash",
        help_text="Yuqoridagi parolni takrorlang"
    )
    first_name = forms.CharField(
        max_length=30,
        label="Ism",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Familya",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = CourierStaff
        fields = ['phone_number', 'delivery_zones']
        labels = {
            'phone_number': 'Telefon raqam',
            'delivery_zones': 'Yetkazib berish zonalari'
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+998901234567',
                'pattern': r'\+998[0-9]{9}',
                'title': 'Telefon raqamni +998XXXXXXXXX formatida kiriting'
            }),
            'delivery_zones': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if not phone.startswith('+998'):
            phone = '+998' + phone.lstrip('+').lstrip('998')
        
        # Telefon raqam formatini tekshirish
        import re
        if not re.match(r'^\+998[0-9]{9}$', phone):
            raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
        
        return phone
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2

    def save(self, commit=True):
        # User yaratish
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
            email='',
            role='courier'
        )
        
        # CourierStaff yaratish
        courier_staff = super().save(commit=False)
        courier_staff.user = user
        courier_staff.full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        if commit:
            courier_staff.save()
        
        return courier_staff
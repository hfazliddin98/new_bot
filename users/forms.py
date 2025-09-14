from django import forms
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        label="Parol",
        help_text="Kamida 8 ta belgi"
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
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
                'title': '+998XXXXXXXXX formatida kiriting'
            }),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            # +998 bilan boshlanishini tekshirish
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
            # Raqamlar sonini tekshirish
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 12:  # 998 + 9 raqam = 12
                raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
            return phone
        return phone
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu foydalanuvchi nomi allaqachon mavjud")
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        """Atomik operatsiya bilan User va KitchenStaff yaratish"""
        try:
            # User yaratish
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data.get('first_name', ''),
                last_name=self.cleaned_data.get('last_name', ''),
                email='',
                role='kitchen'
            )
            # Plain parolni ham saqlash
            user.plain_password = self.cleaned_data['password1']
            user.save()
            
            # KitchenStaff yaratish
            kitchen_staff = KitchenStaff(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                position='Oshpaz',
                full_name=f"{user.first_name} {user.last_name}".strip() or user.username
            )
            
            if commit:
                kitchen_staff.save()
            
            return kitchen_staff
            
        except IntegrityError as e:
            raise forms.ValidationError(f"Ma'lumotlar bazasi xatoligi: {str(e)}")
        except Exception as e:
            raise forms.ValidationError(f"Kutilmagan xatolik: {str(e)}")


class CreateCourierStaffForm(forms.ModelForm):
    """Kuryer yaratish uchun form"""
    
    username = forms.CharField(
        max_length=150,
        label="Foydalanuvchi nomi",
        help_text="Kirishda foydalaniladigan nom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        label="Parol",
        help_text="Kamida 8 ta belgi"
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
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
        fields = ['phone_number']
        labels = {
            'phone_number': 'Telefon raqam',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+998901234567',
                'pattern': r'\+998[0-9]{9}',
                'title': '+998XXXXXXXXX formatida kiriting'
            }),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            # +998 bilan boshlanishini tekshirish
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
            # Raqamlar sonini tekshirish
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 12:  # 998 + 9 raqam = 12
                raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
            return phone
        return phone
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu foydalanuvchi nomi allaqachon mavjud")
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2

    @transaction.atomic
    def save(self, commit=True):
        """Atomik operatsiya bilan User va CourierStaff yaratish"""
        try:
            # User yaratish
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data.get('first_name', ''),
                last_name=self.cleaned_data.get('last_name', ''),
                email='',
                role='courier'
            )
            # Plain parolni ham saqlash
            user.plain_password = self.cleaned_data['password1']
            user.save()
            
            # CourierStaff yaratish
            courier_staff = CourierStaff(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                full_name=f"{user.first_name} {user.last_name}".strip() or user.username
            )
            
            if commit:
                courier_staff.save()

            
            return courier_staff
            
        except IntegrityError as e:
            raise forms.ValidationError(f"Ma'lumotlar bazasi xatoligi: {str(e)}")
        except Exception as e:
            raise forms.ValidationError(f"Kutilmagan xatolik: {str(e)}")


class EditKitchenStaffForm(forms.ModelForm):
    """Oshpaz tahrirlash uchun form"""
    
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
    is_active = forms.BooleanField(
        label="Faol",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    password = forms.CharField(
        label="Parol",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        help_text="Yangi parol kiritish uchun"
    )
    password_confirm = forms.CharField(
        label="Parolni tasdiqlash",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        help_text="Yuqoridagi parolni takrorlang"
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
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        if instance and instance.user:
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['is_active'].initial = instance.user.is_active
            # Telefon raqamni ko'rsatish (to'liq +998 bilan)
            if instance.phone_number:
                self.fields['phone_number'].initial = instance.phone_number
            # Joriy parolni ko'rsatish (agar plain_password mavjud bo'lsa)
            if hasattr(instance.user, 'plain_password') and instance.user.plain_password:
                self.fields['password'].initial = instance.user.plain_password
                self.fields['password_confirm'].initial = instance.user.plain_password
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        # Agar parol kiritilgan bo'lsa, tasdiqlash ham bo'lishi kerak
        if password and not password_confirm:
            raise forms.ValidationError("Parolni tasdiqlash majburiy")
        
        # Parollar mos kelishi kerak
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Parollar mos kelmaydi")
        
        return password_confirm
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            # +998 bilan boshlanishini tekshirish
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
            # Raqamlar sonini tekshirish
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 12:  # 998 + 9 raqam = 12
                raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
            return phone
        return phone
    
    @transaction.atomic
    def save(self, commit=True):
        """Atomik operatsiya bilan User va KitchenStaff yangilash"""
        kitchen_staff = super().save(commit=False)
        
        # User ma'lumotlarini yangilash
        user = kitchen_staff.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_active = self.cleaned_data.get('is_active', False)
        
        # Parol o'zgartirilgan bo'lsa
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)
            user.plain_password = new_password  # Plain parolni ham saqlash
        
        user.save()
        
        # KitchenStaff ma'lumotlarini yangilash
        kitchen_staff.position = 'Oshpaz'  # Avtomatik lavozim
        kitchen_staff.full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Telefon raqamni yangilash
        if 'phone_number' in self.cleaned_data:
            kitchen_staff.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            kitchen_staff.save()
        
        return kitchen_staff


class EditCourierStaffForm(forms.ModelForm):
    """Kuryer tahrirlash uchun form"""
    
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
    is_active = forms.BooleanField(
        label="Faol",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    vehicle_type = forms.ChoiceField(
        label="Transport turi",
        choices=[
            ('motorcycle', 'Mototsikl'),
            ('bicycle', 'Velosiped'),
            ('car', 'Avtomobil'),
            ('on_foot', 'Piyoda'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Parol",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        help_text="Yangi parol kiritish uchun"
    )
    password_confirm = forms.CharField(
        label="Parolni tasdiqlash",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        help_text="Yuqoridagi parolni takrorlang"
    )
    
    class Meta:
        model = CourierStaff
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
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        if instance and instance.user:
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['is_active'].initial = instance.user.is_active
            # Telefon raqamni ko'rsatish (to'liq +998 bilan)
            if instance.phone_number:
                self.fields['phone_number'].initial = instance.phone_number
            self.fields['vehicle_type'].initial = instance.vehicle_type
            # Joriy parolni ko'rsatish (agar plain_password mavjud bo'lsa)
            if hasattr(instance.user, 'plain_password') and instance.user.plain_password:
                self.fields['password'].initial = instance.user.plain_password
                self.fields['password_confirm'].initial = instance.user.plain_password
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        # Agar parol kiritilgan bo'lsa, tasdiqlash ham bo'lishi kerak
        if password and not password_confirm:
            raise forms.ValidationError("Parolni tasdiqlash majburiy")
        
        # Parollar mos kelishi kerak
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Parollar mos kelmaydi")
        
        return password_confirm
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            # +998 bilan boshlanishini tekshirish
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
            # Raqamlar sonini tekshirish
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 12:  # 998 + 9 raqam = 12
                raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
            return phone
        return phone
    
    @transaction.atomic
    def save(self, commit=True):
        """Atomik operatsiya bilan User va CourierStaff yangilash"""
        courier_staff = super().save(commit=False)
        
        # User ma'lumotlarini yangilash
        user = courier_staff.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_active = self.cleaned_data.get('is_active', False)
        
        # Parol o'zgartirilgan bo'lsa
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)
            user.plain_password = new_password  # Plain parolni ham saqlash
        
        user.save()
        
        # CourierStaff ma'lumotlarini yangilash
        courier_staff.vehicle_type = self.cleaned_data.get('vehicle_type', '')
        courier_staff.full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Telefon raqamni yangilash
        if 'phone_number' in self.cleaned_data:
            courier_staff.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            courier_staff.save()
        
        return courier_staff


class UniversalStaffForm(forms.Form):
    """Umumiy xodim yaratish/tahrirlash formi"""
    
    # Role tanlash
    role = forms.ChoiceField(
        choices=[
            ('kitchen', 'Oshpaz'),
            ('courier', 'Kuryer'),
        ],
        label="Xodim turi",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # User ma'lumotlari
    username = forms.CharField(
        max_length=150,
        label="Foydalanuvchi nomi",
        widget=forms.TextInput(attrs={'class': 'form-control'})
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
    phone_number = forms.CharField(
        max_length=20,
        label="Telefon raqam",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998901234567',
            'pattern': r'\+998[0-9]{9}',
            'title': '+998XXXXXXXXX formatida kiriting'
        })
    )
    password1 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        label="Parol",
        help_text="Kamida 8 ta belgi"
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'password'
        }),
        label="Parolni tasdiqlash",
        help_text="Yuqoridagi parolni takrorlang"
    )
    is_active = forms.BooleanField(
        label="Faol",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Kuryer uchun qo'shimcha fieldlar
    vehicle_type = forms.ChoiceField(
        choices=[
            ('motorcycle', 'Mototsikl'),
            ('bicycle', 'Velosiped'),
            ('car', 'Avtomobil'),
            ('on_foot', 'Piyoda'),
        ],
        label="Transport turi",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        # Agar tahrirlash rejimida bo'lsa, ma'lumotlarni to'ldirish
        if self.instance:
            if hasattr(self.instance, 'user'):
                user = self.instance.user
                self.fields['username'].initial = user.username
                self.fields['first_name'].initial = user.first_name
                self.fields['last_name'].initial = user.last_name
                self.fields['is_active'].initial = user.is_active
                self.fields['phone_number'].initial = self.instance.phone_number
                
                if hasattr(user, 'plain_password') and user.plain_password:
                    self.fields['password1'].initial = user.plain_password
                    self.fields['password2'].initial = user.plain_password
                
                # Role ni aniqlash
                if hasattr(self.instance, 'position'):  # KitchenStaff
                    self.fields['role'].initial = 'kitchen'
                elif hasattr(self.instance, 'vehicle_type'):  # CourierStaff
                    self.fields['role'].initial = 'courier'
                    self.fields['vehicle_type'].initial = self.instance.vehicle_type
                    
            # Tahrirlash rejimida username ni o'zgartirib bo'lmaydi
            self.fields['username'].widget.attrs['readonly'] = True
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Yangi yaratishda faqat username unique tekshiruvi
        if not self.instance and User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu foydalanuvchi nomi allaqachon mavjud")
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqam +998 bilan boshlanishi kerak")
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 12:  # 998 + 9 raqam = 12
                raise forms.ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
            return phone
        return phone
    
    @transaction.atomic
    def save(self):
        """Xodimni saqlash"""
        role = self.cleaned_data['role']
        
        if self.instance:
            # Tahrirlash rejimi
            return self._update_staff()
        else:
            # Yangi yaratish rejimi
            return self._create_staff()
    
    def _create_staff(self):
        """Yangi xodim yaratish"""
        role = self.cleaned_data['role']
        
        try:
            # User yaratish
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data.get('first_name', ''),
                last_name=self.cleaned_data.get('last_name', ''),
                email='',
                role=role,
                is_active=self.cleaned_data.get('is_active', True)
            )
            user.plain_password = self.cleaned_data['password1']
            user.save()
            
            # Role ga qarab staff yaratish
            if role == 'kitchen':
                staff = KitchenStaff.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    position='Oshpaz',
                    full_name=f"{user.first_name} {user.last_name}".strip() or user.username
                )
            else:  # courier
                staff = CourierStaff.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    vehicle_type=self.cleaned_data.get('vehicle_type', 'on_foot'),
                    full_name=f"{user.first_name} {user.last_name}".strip() or user.username
                )
            
            return staff
            
        except Exception as e:
            raise forms.ValidationError(f"Xatolik yuz berdi: {str(e)}")
    
    def _update_staff(self):
        """Xodim ma'lumotlarini yangilash"""
        staff = self.instance
        user = staff.user
        
        # User ma'lumotlarini yangilash
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_active = self.cleaned_data.get('is_active', True)
        
        # Parol o'zgartirilgan bo'lsa
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
            user.plain_password = self.cleaned_data['password1']
        
        user.save()
        
        # Staff ma'lumotlarini yangilash
        staff.phone_number = self.cleaned_data['phone_number']
        staff.full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Kuryer uchun qo'shimcha ma'lumotlar
        if hasattr(staff, 'vehicle_type'):
            staff.vehicle_type = self.cleaned_data.get('vehicle_type', 'on_foot')
        
        staff.save()
        
        return staff
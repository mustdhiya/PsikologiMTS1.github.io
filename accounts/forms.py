from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from students.models import Student

class StudentLoginForm(forms.Form):
    """Login form for students using NISN"""
    nisn = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-field',
            'placeholder': 'Masukkan NISN (10 digit)',
            'pattern': '[0-9]{10}',
            'title': 'NISN harus 10 digit angka',
            'autofocus': True,
            'autocomplete': 'username'
        }),
        label='NISN'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 pl-12 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-field',
            'placeholder': 'Masukkan Password',
            'autocomplete': 'current-password'
        }),
        label='Password'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
        }),
        label='Ingat saya'
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean_nisn(self):
        nisn = self.cleaned_data.get('nisn', '').strip()
        
        if not nisn:
            raise forms.ValidationError('NISN tidak boleh kosong')
        
        if not nisn.isdigit():
            raise forms.ValidationError('NISN harus berupa angka')
        
        if len(nisn) != 10:
            raise forms.ValidationError('NISN harus 10 digit')
        
        return nisn
    
    def clean(self):
        nisn = self.cleaned_data.get('nisn')
        password = self.cleaned_data.get('password')
        
        if nisn and password:
            # Check if student exists
            try:
                student = Student.objects.get(nisn=nisn)
                
                if student.is_locked:
                    raise forms.ValidationError(
                        'Akun Anda telah dikunci karena terlalu banyak percobaan login yang gagal. '
                        'Silakan hubungi guru atau admin sekolah.'
                    )
                
            except Student.DoesNotExist:
                raise forms.ValidationError(
                    'NISN tidak ditemukan dalam sistem. '
                    'Pastikan Anda sudah terdaftar sebagai siswa.'
                )
            
            # Authenticate user
            self.user_cache = authenticate(
                self.request,
                username=nisn,
                password=password
            )
            
            if self.user_cache is None:
                # Check if it's a password issue or account issue
                try:
                    student = Student.objects.get(nisn=nisn)
                    remaining_attempts = 5 - student.login_attempts
                    
                    if remaining_attempts > 0:
                        raise forms.ValidationError(
                            f'Password salah. Sisa percobaan: {remaining_attempts}. '
                            f'Jika lupa password, hubungi guru atau gunakan password awal yang diberikan.'
                        )
                    else:
                        raise forms.ValidationError(
                            'Akun dikunci karena terlalu banyak percobaan yang gagal. '
                            'Hubungi guru atau admin sekolah.'
                        )
                except Student.DoesNotExist:
                    raise forms.ValidationError('NISN tidak valid.')
        
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache


class AdminLoginForm(AuthenticationForm):
    """Enhanced admin login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'Username Admin',
            'autofocus': True
        }),
        label='Username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'Password Admin'
        }),
        label='Password'
    )

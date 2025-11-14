from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import StudentLoginForm
from students.models import Student
import logging

logger = logging.getLogger(__name__)

# ==================== CUSTOM MIXINS ====================
class StudentRequiredMixin(LoginRequiredMixin):
    """Mixin untuk memastikan hanya siswa yang dapat akses"""
    login_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        
        # Jika admin/staff, redirect ke admin panel
        if request.user.is_staff or request.user.is_superuser:
            messages.warning(request, 'Akses sebagai admin. Mengarahkan ke admin panel.')
            return redirect('core:dashboard')
        
        # Pastikan user adalah siswa
        try:
            Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            messages.error(request, 'Akun Anda bukan siswa terdaftar.')
            logout(request)
            return redirect(self.login_url)
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin untuk memastikan hanya admin/staff yang dapat akses"""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'Anda tidak memiliki akses untuk halaman ini.')
        return redirect('accounts:login')


# ==================== STUDENT LOGIN ====================
@method_decorator([never_cache, csrf_protect], name='dispatch')
class StudentLoginView(TemplateView):
    """Login view untuk siswa menggunakan NISN"""
    template_name = 'accounts/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('core:dashboard')
            else:
                return redirect('students:certificate_page')  # ← PENTING!
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentLoginForm()
        context['login_type'] = 'student'
        return context
    
    def post(self, request, *args, **kwargs):
        form = StudentLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            # Cegah admin login di student login
            if user.is_staff or user.is_superuser:
                messages.error(request, 'Gunakan admin login untuk masuk sebagai administrator.')
                logger.warning(f'Admin {user.username} attempted student login')
                return render(request, self.template_name, {
                    'form': form,
                    'login_type': 'student',
                    'error': 'Akun admin harus menggunakan admin login'
                })
            
            login(request, user)
            
            # Set session expiry
            remember_me = form.cleaned_data.get('remember_me', False)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            
            # Get student info
            try:
                student = Student.objects.get(user=user)
                messages.success(
                    request,
                    f'Selamat datang, {student.name}! Anda berhasil login ke sistem RMIB.'
                )
                logger.info(f'Student login: {student.name} (NISN: {student.nisn})')
                
                # ✓ REDIRECT KE CERTIFICATE PAGE
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': str(reverse_lazy('students:certificate_page'))
                    })
                
                return redirect('students:certificate_page')  # ← PENTING!
                
            except Student.DoesNotExist:
                messages.error(request, 'Akun Anda tidak terhubung dengan data siswa.')
                logger.error(f'Login tanpa student record: {user.username}')
                logout(request)
                return redirect('accounts:login')
        
        # Form tidak valid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        
        return render(request, self.template_name, {
            'form': form,
            'login_type': 'student'
        })

# ==================== ADMIN LOGIN ====================
@method_decorator([never_cache, csrf_protect], name='dispatch')
class AdminLoginView(TemplateView):
    """Login view terpisah untuk admin"""
    template_name = 'accounts/admin_login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('core:dashboard')
            else:
                return redirect('students:certificate_page')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AuthenticationForm()
        context['login_type'] = 'admin'
        return context
    
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(
                    request,
                    f'Selamat datang, {user.get_full_name() or user.username}!'
                )
                logger.info(f'Admin login: {user.username}')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Akun ini bukan administrator.')
                logger.warning(f'Non-admin attempted admin login: {user.username}')
        else:
            messages.error(request, 'Username atau password salah.')
        
        return render(request, self.template_name, {
            'form': form,
            'login_type': 'admin'
        })


# ==================== LOGOUT ====================
def student_logout(request):
    """Logout untuk semua user"""
    user_info = "User"
    
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            user_info = student.name
            logger.info(f'Student logout: {student.name} (NISN: {student.nisn})')
        except Student.DoesNotExist:
            user_info = request.user.username
            logger.info(f'User logout: {user_info}')
    
    logout(request)
    messages.success(request, f'Sampai jumpa, {user_info}! Anda telah logout dari sistem.')
    return redirect('accounts:login')


# ==================== STUDENT PROFILE ====================
@login_required
def student_profile_view(request):
    """Profil untuk siswa"""
    try:
        student = Student.objects.get(user=request.user)
        return render(request, 'accounts/student_profile.html', {
            'student': student,
            'user_type': 'student'
        })
    except Student.DoesNotExist:
        messages.error(request, 'Data siswa tidak ditemukan.')
        return redirect('accounts:login')


# ==================== DASHBOARD REDIRECT ====================
class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """Redirect ke dashboard yang sesuai berdasarkan tipe user"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Admin/Staff → Admin Panel
        if user.is_staff or user.is_superuser:
            return redirect('core:dashboard')
        
        # Student → Certificate Page
        try:
            Student.objects.get(user=user)
            return redirect('students:certificate_page')
        except Student.DoesNotExist:
            messages.error(request, 'Akun Anda bukan siswa terdaftar.')
            logout(request)
            return redirect('accounts:login')


# ==================== PASSWORD RESET (ADMIN ONLY) ====================
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def reset_student_password(request, student_id):
    """Reset password siswa (admin only)"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            new_password = student.reset_password()
            messages.success(
                request,
                f'Password {student.name} berhasil direset: {new_password}'
            )
            logger.info(f'Password reset by {request.user.username} for: {student.name}')
        except Exception as e:
            messages.error(request, f'Gagal mereset password: {str(e)}')
            logger.error(f'Password reset error for {student.name}: {str(e)}')
    
    return redirect('students:detail', pk=student.pk)


# ==================== UTILITY VIEWS ====================
@login_required
def test_auth_view(request):
    """Test view untuk cek status autentikasi"""
    try:
        student = Student.objects.get(user=request.user)
        return JsonResponse({
            'authenticated': True,
            'user_type': 'student',
            'student_name': student.name,
            'nisn': student.nisn,
            'class': student.student_class,
            'test_status': student.test_status
        })
    except Student.DoesNotExist:
        return JsonResponse({
            'authenticated': True,
            'user_type': 'staff',
            'username': request.user.username,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser
        })


# ==================== ERROR HANDLERS ====================
def permission_denied_view(request, exception=None):
    """Custom 403 error handler"""
    messages.error(request, 'Anda tidak memiliki akses untuk halaman ini.')
    return render(request, 'accounts/403.html', status=403)


def page_not_found_view(request, exception=None):
    """Custom 404 error handler"""
    return render(request, 'accounts/404.html', status=404)


def server_error_view(request):
    """Custom 500 error handler"""
    return render(request, 'accounts/500.html', status=500)

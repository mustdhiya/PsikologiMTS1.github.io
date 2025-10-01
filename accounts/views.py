from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
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

# Setup logging
logger = logging.getLogger(__name__)

@method_decorator([never_cache, csrf_protect], name='dispatch')
class StudentLoginView(TemplateView):
    """Main login view for students using NISN"""
    template_name = 'accounts/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
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
            login(request, user)
            
            # Set session expiry based on remember me
            remember_me = form.cleaned_data.get('remember_me')
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            # Get student info for welcome message
            try:
                student = Student.objects.get(user=user)
                messages.success(
                    request, 
                    f'Selamat datang, {student.name}! Anda berhasil login ke sistem RMIB.'
                )
                
                # Log successful login
                logger.info(f'Student login successful: {student.name} (NISN: {student.nisn})')
                
            except Student.DoesNotExist:
                messages.success(request, f'Selamat datang! Anda berhasil login.')
                logger.warning(f'User login without student record: {user.username}')
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'redirect_url': reverse_lazy('core:dashboard')
                })
            
            return redirect('core:dashboard')
        
        # If form is not valid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        
        return render(request, self.template_name, {'form': form, 'login_type': 'student'})


@method_decorator([never_cache, csrf_protect], name='dispatch')
class AdminLoginView(TemplateView):
    """Separate admin login view"""
    template_name = 'accounts/admin_login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin:index')
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
            
            # Check if user is staff/admin
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
                
                # Log admin login
                logger.info(f'Admin login successful: {user.username}')
                
                return redirect('admin:index')
            else:
                messages.error(request, 'Akun ini tidak memiliki akses administrator.')
                logger.warning(f'Non-admin attempted admin login: {user.username}')
        
        return render(request, self.template_name, {'form': form, 'login_type': 'admin'})


def student_logout(request):
    """Logout view for students"""
    user_name = None
    
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            user_name = student.name
            logger.info(f'Student logout: {student.name} (NISN: {student.nisn})')
        except Student.DoesNotExist:
            user_name = request.user.get_full_name() or request.user.username
            logger.info(f'User logout: {user_name}')
    
    logout(request)
    
    if user_name:
        messages.success(request, f'Sampai jumpa, {user_name}! Anda telah logout dari sistem.')
    else:
        messages.success(request, 'Anda telah logout dari sistem.')
    
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Profile view for authenticated users"""
    try:
        student = Student.objects.get(user=request.user)
        context = {
            'student': student,
            'user_type': 'student'
        }
        template = 'accounts/student_profile.html'
    except Student.DoesNotExist:
        context = {
            'user': request.user,
            'user_type': 'staff'
        }
        template = 'accounts/staff_profile.html'
    
    return render(request, template, context)


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """Redirect to appropriate dashboard based on user type"""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user is admin/staff
        if user.is_staff or user.is_superuser:
            return redirect('admin:index')
        
        # Check if user is a student
        try:
            student = Student.objects.get(user=user)
            return redirect('core:dashboard')
        except Student.DoesNotExist:
            # If user exists but no student record, redirect to profile
            messages.warning(
                request, 
                'Akun Anda tidak terhubung dengan data siswa. Silakan hubungi administrator.'
            )
            return redirect('accounts:profile')


def is_admin_or_staff(user):
    """Check if user is admin or staff"""
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin_or_staff)
def reset_student_password(request, student_id):
    """Reset password for a specific student (admin only)"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            new_password = student.reset_password()
            messages.success(
                request, 
                f'Password untuk {student.name} telah direset. Password baru: {new_password}'
            )
            logger.info(f'Password reset by {request.user.username} for student: {student.name}')
        except Exception as e:
            messages.error(request, f'Gagal mereset password: {str(e)}')
            logger.error(f'Password reset failed for {student.name}: {str(e)}')
    
    return redirect('admin:students_student_changelist')


# Utility views for testing
@login_required
def test_auth_view(request):
    """Test view to check authentication status"""
    try:
        student = Student.objects.get(user=request.user)
        data = {
            'authenticated': True,
            'user_type': 'student',
            'student_name': student.name,
            'nisn': student.nisn,
            'class': student.student_class,
            'test_status': student.test_status
        }
    except Student.DoesNotExist:
        data = {
            'authenticated': True,
            'user_type': 'staff',
            'username': request.user.username,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser
        }
    
    return JsonResponse(data)


# Error handlers
def permission_denied_view(request, exception=None):
    """Custom 403 error handler"""
    return render(request, 'accounts/403.html', status=403)

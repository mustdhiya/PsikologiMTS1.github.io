from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class StudentAccessMiddleware:
    """
    Middleware untuk membatasi akses student hanya ke dashboard & certificate
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip jika user belum login
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip jika user adalah staff/admin
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)
        
        # Daftar URL yang BOLEH diakses student
        allowed_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/students/dashboard/',
            '/students/certificate/',
            '/students/profile/',
            '/static/',
            '/media/',
        ]
        
        # Check if path is allowed
        current_path = request.path
        is_allowed = any(current_path.startswith(path) for path in allowed_paths)
        
        # Jika bukan path yang diizinkan, redirect ke dashboard
        if not is_allowed:
            messages.warning(request, 'Anda hanya dapat mengakses dashboard dan sertifikat.')
            return redirect('students:student_dashboard')
        
        return self.get_response(request)

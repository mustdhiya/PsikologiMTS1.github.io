from django.urls import path
from . import views
from django.shortcuts import redirect


app_name = 'accounts'

urlpatterns = [
    # Student login (main login page)
    path('login/', views.StudentLoginView.as_view(), name='login'),
    
    # Admin login (separate if needed)
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    
    # Logout
    path('logout/', views.student_logout, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Dashboard redirect
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    
    # Password reset (for admin use)
    path('reset-password/<int:student_id>/', views.reset_student_password, name='reset_password'),
]

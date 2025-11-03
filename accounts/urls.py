from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Student Login
    path('login/', views.StudentLoginView.as_view(), name='login'),
    
    # Admin Login
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    
    # Logout
    path('logout/', views.student_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.DashboardRedirectView.as_view(), name='dashboard'),
    
    # Profile
    path('profile/', views.student_profile_view, name='profile'),
    
    # Password Reset (Admin)
    path('student/<int:student_id>/reset-password/', 
         views.reset_student_password, 
         name='reset_student_password'),
    
    # Test
    path('test-auth/', views.test_auth_view, name='test_auth'),
]

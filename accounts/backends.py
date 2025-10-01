from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from students.models import Student
from django.utils import timezone
from datetime import timedelta

class StudentNISNBackend(BaseBackend):
    """Custom authentication backend for NISN-based login"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find student by NISN
            student = Student.objects.get(nisn=username)
            
            # Check if account is locked
            if student.is_locked:
                # Auto-unlock after 30 minutes
                if student.last_login_attempt and \
                   timezone.now() - student.last_login_attempt > timedelta(minutes=30):
                    student.unlock_account()
                else:
                    return None
            
            # Create user account if doesn't exist
            if not student.user:
                user, generated_password = student.create_user_account()
            else:
                user = student.user
                generated_password = student.generated_password
            
            # Check password
            if user.check_password(password) or password == generated_password:
                # Reset failed attempts on successful login
                student.login_attempts = 0
                student.last_login_attempt = timezone.now()
                student.save()
                
                return user
            else:
                # Increment failed attempts
                student.increment_login_attempt()
                return None
                
        except Student.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel

class UserProfile(BaseModel):
    """Extended user profile"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('teacher', 'Guru BK'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

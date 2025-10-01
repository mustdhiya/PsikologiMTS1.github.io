from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BaseModel(models.Model):
    """Base model dengan timestamp"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class School(models.Model):
    """Model untuk data sekolah"""
    name = models.CharField(max_length=200, default="MTs Al-Hikmah")
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    principal = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

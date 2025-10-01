from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel

User = get_user_model()

class Teacher(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return self.user.get_full_name()

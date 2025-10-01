from django.db import models
from students.models import Student
from testsystem.models import RMIBScore
from core.models import BaseModel

class Certificate(BaseModel):
    """Model untuk sertifikat RMIB"""
    TEMPLATE_CHOICES = [
        ('standard', 'Template Standard'),
        ('premium', 'Template Premium'),
        ('minimal', 'Template Minimal'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rmib_score = models.ForeignKey(RMIBScore, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='standard')
    issued_date = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True)
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = f"RMIB-{self.student.nisn}-{self.issued_date.year}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.name}"

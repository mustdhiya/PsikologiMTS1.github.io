from django.db import models
from students.models import Student
from core.models import BaseModel

class ClassReport(BaseModel):
    """Laporan per kelas"""
    class_name = models.CharField(max_length=10)
    total_students = models.IntegerField(default=0)
    completed_tests = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    report_date = models.DateField()
    pdf_file = models.FileField(upload_to='class_reports/', blank=True)
    
    def __str__(self):
        return f"Laporan Kelas {self.class_name} - {self.report_date}"

class SystemReport(BaseModel):
    """Laporan sistem keseluruhan"""
    REPORT_TYPES = [
        ('monthly', 'Laporan Bulanan'),
        ('semester', 'Laporan Semester'),
        ('yearly', 'Laporan Tahunan'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    total_students = models.IntegerField(default=0)
    completed_tests = models.IntegerField(default=0)
    pdf_file = models.FileField(upload_to='system_reports/', blank=True)
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.period_start} to {self.period_end}"

from django.db import models
from students.models import Student
from core.models import BaseModel

class RMIBCategory(BaseModel):
    """Kategori RMIB dengan deskripsi lengkap"""
    code = models.CharField(max_length=10, unique=True)  # OUT, ME, COMP, dll
    name = models.CharField(max_length=100)  # Nama kategori
    description = models.TextField()  # Deskripsi lengkap
    career_fields = models.TextField()  # Field karir yang cocok
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class RMIBScore(BaseModel):
    """Hasil tes RMIB siswa"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='rmib_score')
    
    # 12 Kategori RMIB
    outdoor = models.IntegerField(default=0, verbose_name="Outdoor (OUT)")
    mechanical = models.IntegerField(default=0, verbose_name="Mechanical (ME)")
    computational = models.IntegerField(default=0, verbose_name="Computational (COMP)")
    scientific = models.IntegerField(default=0, verbose_name="Scientific (SCI)")
    personal = models.IntegerField(default=0, verbose_name="Personal (PERS)")
    aesthetic = models.IntegerField(default=0, verbose_name="Aesthetic (AEST)")
    literary = models.IntegerField(default=0, verbose_name="Literary (LIT)")
    musical = models.IntegerField(default=0, verbose_name="Musical (MUS)")
    social_service = models.IntegerField(default=0, verbose_name="Social Service (SS)")
    clerical = models.IntegerField(default=0, verbose_name="Clerical (CLER)")
    practical = models.IntegerField(default=0, verbose_name="Practical (PRAC)")
    medical = models.IntegerField(default=0, verbose_name="Medical (MED)")
    
    # Metadata
    test_duration = models.DurationField(null=True, blank=True)
    total_questions = models.IntegerField(default=150)
    completed_questions = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    def get_highest_scores(self, top_n=3):
        """Mendapatkan skor tertinggi"""
        scores = {
            'Outdoor': self.outdoor,
            'Mechanical': self.mechanical,
            'Computational': self.computational,
            'Scientific': self.scientific,
            'Personal': self.personal,
            'Aesthetic': self.aesthetic,
            'Literary': self.literary,
            'Musical': self.musical,
            'Social Service': self.social_service,
            'Clerical': self.clerical,
            'Practical': self.practical,
            'Medical': self.medical,
        }
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def __str__(self):
        return f"RMIB Score - {self.student.name}"

class TestSession(BaseModel):
    """Session tes untuk tracking progress"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    current_question = models.IntegerField(default=1)
    is_paused = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Session {self.student.name} - {self.start_time.date()}"

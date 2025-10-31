from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import BaseModel
import secrets
import string


class Student(BaseModel):
    """Model utama untuk data siswa"""
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Belum Tes'),
        ('in_progress', 'Sedang Tes'),
        ('completed', 'Selesai'),
    ]
    
    # Data Pribadi
    name = models.CharField(max_length=200)
    nisn = models.CharField(max_length=10, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=100, blank=True)
    
    # Data Akademik
    student_class = models.CharField(max_length=10)
    entry_year = models.IntegerField(default=2025)
    
    # Status Tes
    test_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    test_date = models.DateTimeField(null=True, blank=True)
    
    # Contact Info
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    
    # Authentication fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    generated_password = models.CharField(max_length=20, blank=True)
    password_changed = models.BooleanField(default=False)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    
    def generate_password(self):
        """Generate automatic password for student"""
        if not self.generated_password:
            name_part = ''.join(c for c in self.name.split()[0][:3] if c.isalpha()).upper()
            year_part = str(self.birth_date.year)[-2:] if self.birth_date else '00'
            random_part = ''.join(secrets.choice(string.digits) for _ in range(2))
            
            self.generated_password = f"{name_part}{year_part}{random_part}"
            self.save()
        
        return self.generated_password
    
    def create_user_account(self):
        """Create Django User account for student"""
        if not self.user:
            password = self.generate_password()
            
            user = User.objects.create_user(
                username=self.nisn,
                email=f"{self.nisn}@student.mts1samarinda.id",
                first_name=self.name.split()[0],
                last_name=' '.join(self.name.split()[1:]) if len(self.name.split()) > 1 else '',
                password=password
            )
            
            self.user = user
            self.save()
            
            return user, password
        
        return self.user, self.generated_password
    
    def reset_password(self):
        """Reset student password to generated one"""
        if self.user:
            self.generated_password = ''
            new_password = self.generate_password()
            
            self.user.set_password(new_password)
            self.user.save()
            
            self.password_changed = False
            self.login_attempts = 0
            self.is_locked = False
            self.save()
            
            return new_password
        return None
    
    def increment_login_attempt(self):
        """Increment failed login attempts"""
        self.login_attempts += 1
        self.last_login_attempt = timezone.now()
        
        if self.login_attempts >= 5:
            self.is_locked = True
        
        self.save()
    
    def unlock_account(self):
        """Unlock student account"""
        self.is_locked = False
        self.login_attempts = 0
        self.save()

    def get_display_name(self):
        """Get student display name"""
        return self.name
    
    def get_class_display(self):
        """Get formatted class display"""
        return f"Kelas {self.student_class}"
    
    def is_test_completed(self):
        """Check if student has completed the test"""
        return self.test_status == 'completed'
    
    def can_take_test(self):
        """Check if student can take the test"""
        return self.test_status in ['pending', 'in_progress']
    
    class Meta:
        ordering = ['student_class', 'name']
        indexes = [
            models.Index(fields=['nisn']),
            models.Index(fields=['student_class']),
            models.Index(fields=['test_status']),
        ]
        verbose_name = 'Siswa'
        verbose_name_plural = 'Siswa'
    
    def __str__(self):
        return f"{self.name} ({self.student_class})"


class Prestasi(BaseModel):
    """Model untuk prestasi siswa"""
    JENIS_CHOICES = [
        ('akademik', 'Prestasi Akademik'),
        ('olahraga', 'Prestasi Olahraga'),
        ('seni', 'Prestasi Seni'),
        ('organisasi', 'Prestasi Organisasi'),
        ('teknologi', 'Prestasi Teknologi'),
        ('keagamaan', 'Prestasi Keagamaan'),
    ]
    
    TINGKAT_CHOICES = [
        ('sekolah', 'Tingkat Sekolah'),
        ('kecamatan', 'Tingkat Kecamatan'),
        ('kabupaten', 'Tingkat Kabupaten'),
        ('provinsi', 'Tingkat Provinsi'),
        ('nasional', 'Tingkat Nasional'),
        ('internasional', 'Tingkat Internasional'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='prestasi')
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)
    nama = models.CharField(max_length=200)
    tingkat = models.CharField(max_length=20, choices=TINGKAT_CHOICES)
    peringkat = models.CharField(max_length=20)
    tahun = models.IntegerField()
    keterangan = models.TextField(blank=True)
    sertifikat = models.FileField(upload_to='sertifikat_prestasi/', blank=True)
    bonus_score = models.IntegerField(default=0)
    
    def get_tingkat_display_color(self):
        """Get color class for tingkat display"""
        colors = {
            'sekolah': 'text-blue-600',
            'kecamatan': 'text-green-600', 
            'kabupaten': 'text-yellow-600',
            'provinsi': 'text-orange-600',
            'nasional': 'text-red-600',
            'internasional': 'text-purple-600',
        }
        return colors.get(self.tingkat, 'text-gray-600')
    
    def get_jenis_icon(self):
        """Get icon for jenis prestasi"""
        icons = {
            'akademik': 'fas fa-graduation-cap',
            'olahraga': 'fas fa-running',
            'seni': 'fas fa-paint-brush',
            'organisasi': 'fas fa-users',
            'teknologi': 'fas fa-laptop-code',
            'keagamaan': 'fas fa-pray',
        }
        return icons.get(self.jenis, 'fas fa-trophy')
    
    class Meta:
        ordering = ['-tahun', 'tingkat', 'nama']
        verbose_name = 'Prestasi'
        verbose_name_plural = 'Prestasi'
    
    def __str__(self):
        return f"{self.student.name} - {self.nama}"


class RMIBResult(BaseModel):
    """Model untuk menyimpan hasil tes RMIB"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='rmib_result')
    
    # Level storage: {category_key: level_value}
    levels = models.JSONField(default=dict, help_text="Levels untuk setiap kategori (1-12)")
    
    # Scores
    category_scores = models.JSONField(default=dict, help_text="Score per kategori (level × 5)")
    total_score = models.IntegerField(default=0, help_text="Total score dari semua kategori")
    
    # Top interests
    primary_interest = models.CharField(max_length=20, blank=True)
    primary_level = models.IntegerField(default=0)
    
    secondary_interest = models.CharField(max_length=20, blank=True)
    secondary_level = models.IntegerField(default=0)
    
    tertiary_interest = models.CharField(max_length=20, blank=True)
    tertiary_level = models.IntegerField(default=0)
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'Sedang Dikerjakan'),
            ('completed', 'Selesai'),
            ('edited', 'Diedit')  # ← NEW: Track if edited
        ],
        default='in_progress'
    )
    
    submitted_at = models.DateTimeField(help_text="Waktu tes diselesaikan")
    edited_at = models.DateTimeField(null=True, blank=True, help_text="Waktu terakhir diedit")
    
    def calculate_scores(self):
        """Calculate scores dari levels"""
        self.category_scores = {}
        self.total_score = 0
        
        for category, level in self.levels.items():
            score = level * 5
            self.category_scores[category] = score
            self.total_score += score
        
        # Find top 3 interests
        sorted_levels = sorted(self.levels.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_levels) > 0:
            self.primary_interest = sorted_levels[0][0]
            self.primary_level = sorted_levels[0][1]
        
        if len(sorted_levels) > 1:
            self.secondary_interest = sorted_levels[1][0]
            self.secondary_level = sorted_levels[1][1]
        
        if len(sorted_levels) > 2:
            self.tertiary_interest = sorted_levels[2][0]
            self.tertiary_level = sorted_levels[2][1]
    
    def get_ranking_summary(self):
        """Get all categories sorted by level"""
        return sorted(self.levels.items(), key=lambda x: x[1], reverse=True)
    
    def mark_as_edited(self):
        """Mark this result as edited"""
        self.status = 'edited'
        self.edited_at = timezone.now()
        self.save()
    
    def reset_for_editing(self):
        """Reset status to in_progress for editing"""
        self.status = 'in_progress'
        self.save()
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Hasil RMIB'
        verbose_name_plural = 'Hasil RMIB'
    
    def __str__(self):
        return f"RMIB Result - {self.student.name} ({self.status})"

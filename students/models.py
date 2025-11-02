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


class AchievementType(models.Model):
    CATEGORY_CHOICES = [
        ('academic', '🎓 Akademik'),
        ('non_academic', '🎨 Non-Akademik'),
        ('other', 'Lainnya')
    ]
    
    RMIB_CHOICES = [
        ('outdoor', 'Outdoor'),
        ('mechanical', 'Mechanical'),
        ('computational', 'Computational'),
        ('scientific', 'Scientific'),
        ('personal_contact', 'Personal Contact'),
        ('aesthetic', 'Aesthetic'),
        ('literary', 'Literary'),
        ('musical', 'Musical'),
        ('social_service', 'Social Service'),
        ('clerical', 'Clerical'),
        ('practical', 'Practical'),
        ('medical', 'Medical'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Auto-generate
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    
    # RMIB Mapping
    rmib_primary = models.CharField(
        max_length=50, 
        choices=RMIB_CHOICES, 
        blank=True, 
        null=True,
        help_text='Kategori RMIB utama'
    )
    rmib_secondary = models.CharField(
        max_length=50, 
        choices=RMIB_CHOICES, 
        blank=True,  # CHANGE NULL TO BLANK ONLY
        null=True,
        help_text='Kategori RMIB sekunder'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Achievement Types'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate code if empty
        if not self.code:
            # Create code from name: Matematika -> MAT
            words = self.name.split()
            code = ''.join([word[0].upper() for word in words])[:10]
            counter = 1
            original_code = code
            while AchievementType.objects.filter(code=code).exclude(pk=self.pk).exists():
                code = f"{original_code}{counter}"
                counter += 1
            self.code = code
        
        super().save(*args, **kwargs)


class StudentAchievement(BaseModel):
    """Prestasi siswa (formerly Prestasi)"""
    LEVEL_CHOICES = [
        ('sekolah', 'Sekolah'),
        ('kecamatan', 'Kecamatan'),
        ('kabupaten', 'Kabupaten/Kota'),
        ('provinsi', 'Provinsi'),
        ('nasional', 'Nasional'),
        ('internasional', 'Internasional'),
    ]
    
    RANK_CHOICES = [
        ('juara_1', 'Juara 1'),
        ('juara_2', 'Juara 2'),
        ('juara_3', 'Juara 3'),
        ('harapan', 'Juara Harapan/Finalis'),
    ]
    
    # Poin matrix
    POINTS_MATRIX = {
        'internasional': {'juara_1': 100, 'juara_2': 90, 'juara_3': 80, 'harapan': 70},
        'nasional': {'juara_1': 80, 'juara_2': 70, 'juara_3': 60, 'harapan': 50},
        'provinsi': {'juara_1': 60, 'juara_2': 50, 'juara_3': 40, 'harapan': 30},
        'kabupaten': {'juara_1': 40, 'juara_2': 35, 'juara_3': 30, 'harapan': 20},
        'kecamatan': {'juara_1': 20, 'juara_2': 15, 'juara_3': 10, 'harapan': 5},
        'sekolah': {'juara_1': 10, 'juara_2': 8, 'juara_3': 6, 'harapan': 4},
    }
    
    # Relations
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.ForeignKey(AchievementType, on_delete=models.PROTECT, related_name='student_achievements')
    
    # Achievement details
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    year = models.IntegerField(help_text="Tahun prestasi diraih")
    
    # Auto-calculated
    points = models.IntegerField(default=0, help_text="Poin prestasi berdasarkan level & rank")
    
    # RMIB contribution (auto-calculated)
    rmib_contributions = models.JSONField(
        default=dict, 
        help_text="Kontribusi ke kategori RMIB, misal: {'scientific': 80, 'computational': 40}"
    )
    
    # Evidence
    certificate = models.FileField(upload_to='achievements/%Y/', blank=True, help_text="Upload sertifikat/bukti")
    notes = models.TextField(blank=True, help_text="Catatan tambahan")
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text="Sudah diverifikasi oleh guru/admin")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def calculate_points(self):
        """Calculate points based on level and rank"""
        self.points = self.POINTS_MATRIX.get(self.level, {}).get(self.rank, 0)
        return self.points
    
    def calculate_rmib_contributions(self):
        """Calculate RMIB category contributions"""
        self.rmib_contributions = {}
        
        # Primary category gets full points
        if self.achievement_type.rmib_primary:
            self.rmib_contributions[self.achievement_type.rmib_primary] = self.points
        
        # Secondary categories get 50% of points
        if self.achievement_type.rmib_secondary and self.achievement_type.rmib_secondary != '-':
            secondary_cats = [c.strip() for c in self.achievement_type.rmib_secondary.split(',')]
            secondary_points = self.points // 2
            
            for cat in secondary_cats:
                if cat and cat != '-':
                    self.rmib_contributions[cat] = secondary_points
        
        return self.rmib_contributions
    
    def save(self, *args, **kwargs):
        """Auto-calculate points and RMIB contributions before saving"""
        self.calculate_points()
        self.calculate_rmib_contributions()
        super().save(*args, **kwargs)
    
    def verify(self, user):
        """Verify this achievement"""
        self.is_verified = True
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()
    
    def get_level_color(self):
        """Get color for level badge"""
        colors = {
            'sekolah': 'blue',
            'kecamatan': 'green',
            'kabupaten': 'yellow',
            'provinsi': 'orange',
            'nasional': 'red',
            'internasional': 'purple',
        }
        return colors.get(self.level, 'gray')
    
    def get_rank_badge_class(self):
        """Get badge class for rank"""
        classes = {
            'juara_1': 'bg-gradient-to-r from-yellow-400 to-yellow-600',  # Gold
            'juara_2': 'bg-gradient-to-r from-gray-300 to-gray-500',       # Silver
            'juara_3': 'bg-gradient-to-r from-orange-400 to-orange-600',   # Bronze
            'harapan': 'bg-gradient-to-r from-blue-400 to-blue-600',       # Blue
        }
        return classes.get(self.rank, 'bg-gray-400')
    
    class Meta:
        ordering = ['-year', '-points', 'achievement_type__name']
        verbose_name = 'Prestasi Siswa'
        verbose_name_plural = 'Prestasi Siswa'
        indexes = [
            models.Index(fields=['student', '-year']),
            models.Index(fields=['achievement_type', 'level']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.student.name} - {self.achievement_type.name} ({self.get_level_display()})"

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

    def get_achievement_contributions(self):
        """Get total RMIB contributions from student achievements"""
        contributions = {}
        
        for achievement in self.student.achievements.filter(is_verified=True):
            for category, points in achievement.rmib_contributions.items():
                contributions[category] = contributions.get(category, 0) + points
        
        return contributions
    
    def get_total_rmib_scores(self):
        """Get combined RMIB scores (test + achievements)"""
        test_scores = self.category_scores.copy()
        achievement_scores = self.get_achievement_contributions()
        
        combined_scores = {}
        all_categories = set(list(test_scores.keys()) + list(achievement_scores.keys()))
        
        for category in all_categories:
            combined_scores[category] = {
                'test_score': test_scores.get(category, 0),
                'achievement_score': achievement_scores.get(category, 0),
                'total_score': test_scores.get(category, 0) + achievement_scores.get(category, 0)
            }
        
        return combined_scores
    
    def get_final_ranking(self):
        """Get final RMIB ranking (test + achievements)"""
        combined = self.get_total_rmib_scores()
        return sorted(combined.items(), key=lambda x: x[1]['total_score'], reverse=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Hasil RMIB'
        verbose_name_plural = 'Hasil RMIB'
    
    def __str__(self):
        return f"RMIB Result - {self.student.name} ({self.status})"

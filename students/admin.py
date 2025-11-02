from django.contrib import admin
from django.utils.html import format_html
from .models import Student, AchievementType, StudentAchievement, RMIBResult


# ==================== ACHIEVEMENT TYPE ADMIN ====================

@admin.register(AchievementType)
class AchievementTypeAdmin(admin.ModelAdmin):
    """Admin untuk Master Jenis Prestasi"""
    list_display = ['code', 'name', 'category_display', 'rmib_primary', 'is_active']
    list_filter = ['category', 'is_active', 'rmib_primary']
    search_fields = ['code', 'name', 'sub_category']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identitas', {
            'fields': ('code', 'name', 'category', 'sub_category')
        }),
        ('RMIB Mapping', {
            'fields': ('rmib_primary', 'rmib_secondary')
        }),
        ('Detail', {
            'fields': ('example_competitions', 'description', 'available_levels')
        }),
        ('Display', {
            'fields': ('icon', 'color', 'is_active')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_display(self, obj):
        """Display kategori dengan badge"""
        colors = {
            'akademik': '#3b82f6',
            'non_akademik': '#8b5cf6',
        }
        color = colors.get(obj.category, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = "Kategori"


# ==================== STUDENT ACHIEVEMENT INLINE ====================

class StudentAchievementInline(admin.TabularInline):
    """Inline admin untuk StudentAchievement"""
    model = StudentAchievement
    extra = 1
    fields = ['achievement_type', 'level', 'rank', 'year', 'points', 'is_verified']
    readonly_fields = ['points']


# ==================== STUDENT ADMIN ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin untuk Student"""
    list_display = ['name', 'nisn', 'student_class', 'gender', 'test_status', 'test_date']
    list_filter = ['student_class', 'test_status', 'gender', 'entry_year']
    search_fields = ['name', 'nisn', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'generated_password']
    
    fieldsets = (
        ('Data Pribadi', {
            'fields': ('name', 'nisn', 'gender', 'birth_date', 'birth_place')
        }),
        ('Data Akademik', {
            'fields': ('student_class', 'entry_year', 'test_status', 'test_date')
        }),
        ('Kontak', {
            'fields': ('phone', 'address', 'parent_phone')
        }),
        ('Autentikasi', {
            'fields': ('user', 'generated_password', 'password_changed', 'is_locked', 'login_attempts'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [StudentAchievementInline]
    
    actions = ['reset_password', 'unlock_account']
    
    def reset_password(self, request, queryset):
        """Reset password untuk selected students"""
        for student in queryset:
            if student.user:
                new_password = student.reset_password()
                self.message_user(
                    request, 
                    f'Password {student.name} direset ke: {new_password}'
                )
    reset_password.short_description = "Reset password dipilih siswa"
    
    def unlock_account(self, request, queryset):
        """Unlock account untuk selected students"""
        for student in queryset:
            student.unlock_account()
        self.message_user(request, f'{queryset.count()} akun berhasil dibuka')
    unlock_account.short_description = "Buka akun terkunci"


# ==================== STUDENT ACHIEVEMENT ADMIN ====================

@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    """Admin untuk Prestasi Siswa"""
    list_display = [
        'student_name',
        'achievement_name',
        'level_badge',
        'rank_display',
        'year',
        'points',
        'is_verified_display'
    ]
    list_filter = ['level', 'rank', 'year', 'is_verified', 'achievement_type__category']
    search_fields = ['student__name', 'achievement_type__name', 'student__nisn']
    readonly_fields = [
        'created_at',
        'updated_at',
        'points',
        'rmib_contributions_display',
        'verified_at'
    ]
    
    fieldsets = (
        ('Data Siswa & Prestasi', {
            'fields': ('student', 'achievement_type')
        }),
        ('Prestasi', {
            'fields': ('level', 'rank', 'year', 'points', 'certificate', 'notes')
        }),
        ('RMIB Contributions', {
            'fields': ('rmib_contributions_display',),
            'description': 'Kontribusi otomatis ke kategori RMIB'
        }),
        ('Verifikasi', {
            'fields': ('is_verified', 'verified_by', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_achievements', 'unverify_achievements']
    
    def student_name(self, obj):
        """Display nama siswa"""
        return f"{obj.student.name} ({obj.student.nisn})"
    student_name.short_description = "Siswa"
    
    def achievement_name(self, obj):
        """Display nama prestasi"""
        return f"{obj.achievement_type.name}"
    achievement_name.short_description = "Prestasi"
    
    def level_badge(self, obj):
        """Display level dengan badge"""
        colors = {
            'sekolah': '#3b82f6',
            'kecamatan': '#10b981',
            'kabupaten': '#f59e0b',
            'provinsi': '#f97316',
            'nasional': '#ef4444',
            'internasional': '#8b5cf6',
        }
        color = colors.get(obj.level, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.get_level_display()
        )
    level_badge.short_description = "Tingkat"
    
    def rank_display(self, obj):
        """Display rank dengan warna"""
        classes = {
            'juara_1': 'from-yellow-400 to-yellow-600',
            'juara_2': 'from-gray-300 to-gray-500',
            'juara_3': 'from-orange-400 to-orange-600',
            'harapan': 'from-blue-400 to-blue-600',
        }
        class_name = classes.get(obj.rank, 'from-gray-400 to-gray-600')
        colors_map = {
            'juara_1': '#FBBF24',
            'juara_2': '#A0AEC0',
            'juara_3': '#FB923C',
            'harapan': '#60A5FA',
        }
        bg = colors_map.get(obj.rank, '#999')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            bg,
            obj.get_rank_display()
        )
    rank_display.short_description = "Peringkat"
    
    def is_verified_display(self, obj):
        """Display status verifikasi"""
        if obj.is_verified:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #ef4444;">Pending</span>'
        )
    is_verified_display.short_description = "Status"
    
    def rmib_contributions_display(self, obj):
        """Display RMIB contributions"""
        if not obj.rmib_contributions:
            return '<em>Belum dihitung</em>'
        
        html = '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        html += '<tr style="background-color: #f3f4f6;"><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Kategori RMIB</th><th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Poin</th></tr>'
        
        for category, points in sorted(obj.rmib_contributions.items()):
            category_name = category.replace('_', ' ').title()
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{category_name}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{points}</strong></td></tr>'
        
        html += '</table>'
        return format_html(html)
    rmib_contributions_display.short_description = "Kontribusi RMIB"
    
    def verify_achievements(self, request, queryset):
        """Verify selected achievements"""
        count = 0
        for achievement in queryset:
            if not achievement.is_verified:
                achievement.verify(request.user)
                count += 1
        self.message_user(request, f'{count} prestasi berhasil diverifikasi')
    verify_achievements.short_description = "Verifikasi prestasi yang dipilih"
    
    def unverify_achievements(self, request, queryset):
        """Unverify selected achievements"""
        queryset.update(is_verified=False, verified_by=None, verified_at=None)
        self.message_user(request, f'{queryset.count()} prestasi status verifikasi dihapus')
    unverify_achievements.short_description = "Batalkan verifikasi prestasi yang dipilih"


# ==================== RMIB RESULT ADMIN ====================

@admin.register(RMIBResult)
class RMIBResultAdmin(admin.ModelAdmin):
    """Admin untuk RMIB Result"""
    list_display = [
        'student_name',
        'total_score',
        'primary_interest_display',
        'status_display',
        'submitted_date'
    ]
    list_filter = ['submitted_at', 'primary_interest', 'status']
    search_fields = ['student__name', 'student__nisn', 'primary_interest']
    readonly_fields = [
        'created_at',
        'updated_at',
        'submitted_at',
        'edited_at',
        'total_score',
        'category_scores_display',
        'levels_display',
        'top_interests_display',
        'achievement_contributions_display'
    ]
    
    fieldsets = (
        ('Data Siswa', {
            'fields': ('student', 'status')
        }),
        ('Level Input', {
            'fields': ('levels_display',),
            'description': 'Level yang dipilih siswa untuk setiap kategori (1-12)'
        }),
        ('Skor dari Tes', {
            'fields': ('total_score', 'category_scores_display'),
            'description': 'Skor otomatis terhitung dari levels'
        }),
        ('Kontribusi Prestasi', {
            'fields': ('achievement_contributions_display',),
            'description': 'Skor tambahan dari prestasi yang terverifikasi'
        }),
        ('Minat Utama', {
            'fields': ('primary_interest', 'primary_level')
        }),
        ('Minat Kedua', {
            'fields': ('secondary_interest', 'secondary_level'),
            'classes': ('collapse',)
        }),
        ('Minat Ketiga', {
            'fields': ('tertiary_interest', 'tertiary_level'),
            'classes': ('collapse',)
        }),
        ('Ringkasan Minat', {
            'fields': ('top_interests_display',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('submitted_at', 'edited_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_name(self, obj):
        """Display student name"""
        return f"{obj.student.name} ({obj.student.nisn})"
    student_name.short_description = "Siswa"
    
    def status_display(self, obj):
        """Display status dengan badge"""
        colors = {
            'in_progress': '#3b82f6',
            'completed': '#10b981',
            'edited': '#f59e0b',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"
    
    def primary_interest_display(self, obj):
        """Display primary interest dengan warna"""
        if obj.primary_interest:
            colors = {
                'outdoor': '#10b981',
                'mechanical': '#3b82f6',
                'computational': '#8b5cf6',
                'scientific': '#6366f1',
                'personal_contact': '#ec4899',
                'aesthetic': '#f97316',
                'literary': '#14b8a6',
                'musical': '#ef4444',
                'social_service': '#f59e0b',
                'clerical': '#6b7280',
                'practical': '#eab308',
                'medical': '#dc2626',
            }
            color = colors.get(obj.primary_interest, '#666')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
                color,
                obj.primary_interest.replace('_', ' ').title()
            )
        return '-'
    primary_interest_display.short_description = "Minat Utama"
    
    def submitted_date(self, obj):
        """Display submitted date"""
        return obj.submitted_at.strftime('%d %b %Y %H:%M') if obj.submitted_at else '-'
    submitted_date.short_description = "Tanggal Kirim"
    
    def levels_display(self, obj):
        """Display levels sebagai formatted text"""
        if not obj.levels:
            return '<em>Belum ada data</em>'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f3f4f6;"><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Kategori</th><th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Level</th></tr>'
        
        for category, level in sorted(obj.levels.items()):
            category_name = category.replace('_', ' ').title()
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{category_name}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{level}</strong></td></tr>'
        
        html += '</table>'
        return format_html(html)
    levels_display.short_description = "Level per Kategori"
    
    def category_scores_display(self, obj):
        """Display category scores sebagai formatted table"""
        if not obj.category_scores:
            return '<em>Belum dihitung</em>'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f3f4f6;"><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Kategori</th><th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Score</th></tr>'
        
        for category, score in sorted(obj.category_scores.items(), key=lambda x: x[1], reverse=True):
            category_name = category.replace('_', ' ').title()
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{category_name}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong>{score}</strong></td></tr>'
        
        html += '</table>'
        return format_html(html)
    category_scores_display.short_description = "Score Tes per Kategori"
    
    def achievement_contributions_display(self, obj):
        """Display achievement contributions"""
        contributions = obj.get_achievement_contributions()
        
        if not contributions:
            return '<em>Belum ada prestasi terverifikasi</em>'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f3f4f6;"><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Kategori</th><th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Kontribusi</th></tr>'
        
        for category, score in sorted(contributions.items(), key=lambda x: x[1], reverse=True):
            category_name = category.replace('_', ' ').title()
            html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;">{category_name}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: center;"><strong style="color: #10b981;">+{score}</strong></td></tr>'
        
        html += '</table>'
        return format_html(html)
    achievement_contributions_display.short_description = "Kontribusi dari Prestasi"
    
    def top_interests_display(self, obj):
        """Display top 3 interests"""
        if not obj.levels or len(obj.levels) == 0:
            return '<em>Belum ada data</em>'
        
        ranking = obj.get_ranking_summary()
        
        html = '<ol>'
        for i, (category, level) in enumerate(ranking[:3], 1):
            category_name = category.replace('_', ' ').title()
            score = level * 5
            html += f'<li><strong>{category_name}</strong> - Level {level} ({score} poin)</li>'
        html += '</ol>'
        
        return format_html(html)
    top_interests_display.short_description = "Top 3 Minat Tertinggi"
    
    def has_add_permission(self, request):
        """Prevent manual addition - only auto-created"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for data cleanup"""
        return request.user.is_superuser

from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Prestasi, RMIBResult
import json


class PrestasiInline(admin.TabularInline):
    """Inline admin untuk Prestasi"""
    model = Prestasi
    extra = 1
    fields = ['jenis', 'nama', 'tingkat', 'peringkat', 'tahun', 'bonus_score']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin untuk Student"""
    list_display = ['name', 'nisn', 'student_class', 'gender', 'test_status', 'test_date']
    list_filter = ['student_class', 'test_status', 'gender', 'entry_year']
    search_fields = ['name', 'nisn', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
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
    
    inlines = [PrestasiInline]
    
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


@admin.register(Prestasi)
class PrestasiAdmin(admin.ModelAdmin):
    """Admin untuk Prestasi"""
    list_display = ['student', 'nama', 'jenis', 'tingkat', 'peringkat', 'tahun', 'bonus_score']
    list_filter = ['jenis', 'tingkat', 'tahun']
    search_fields = ['student__name', 'nama']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Data Prestasi', {
            'fields': ('student', 'nama', 'jenis', 'tingkat', 'peringkat', 'tahun')
        }),
        ('Detail', {
            'fields': ('keterangan', 'sertifikat', 'bonus_score')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RMIBResult)
class RMIBResultAdmin(admin.ModelAdmin):
    """Admin untuk RMIB Result - Level-Based"""
    list_display = [
        'student_name',
        'total_score',
        'primary_interest_display',
        'primary_level',
        'submitted_date'
    ]
    list_filter = ['submitted_at', 'primary_interest']
    search_fields = ['student__name', 'student__nisn', 'primary_interest']
    readonly_fields = [
        'created_at',
        'updated_at',
        'submitted_at',
        'total_score',
        'category_scores_display',
        'levels_display',
        'top_interests_display'
    ]
    
    fieldsets = (
        ('Data Siswa', {
            'fields': ('student',)
        }),
        ('Level Input', {
            'fields': ('levels_display',),
            'description': 'Level yang dipilih siswa untuk setiap kategori (1-12)'
        }),
        ('Skor Terhitung', {
            'fields': ('total_score', 'category_scores_display'),
            'description': 'Skor otomatis terhitung dari levels'
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
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_name(self, obj):
        """Display student name"""
        return f"{obj.student.name} ({obj.student.nisn})"
    student_name.short_description = "Siswa"
    
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
    category_scores_display.short_description = "Score per Kategori"
    
    def top_interests_display(self, obj):
        """Display top 3 interests"""
        if not obj.levels or len(obj.levels) == 0:
            return '<em>Belum ada data</em>'
        
        top_3 = obj.get_top_3_interests()
        
        html = '<ol>'
        for i, interest in enumerate(top_3, 1):
            category_name = interest['category'].replace('_', ' ').title()
            level = interest['level']
            score = interest['score']
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

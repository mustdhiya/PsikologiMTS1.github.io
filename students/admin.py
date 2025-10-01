from django.contrib import admin
from .models import Student, Prestasi, RMIBResult

@admin.register(RMIBResult)
class RMIBResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'primary_interest', 'secondary_interest', 'tertiary_interest', 'submitted_at')
    list_filter = ('primary_interest', 'submitted_at')
    search_fields = ('student__name', 'student__nisn')
    readonly_fields = ('submitted_at', 'rankings', 'original_scores', 'final_scores', 'top_interests')
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Test Results', {
            'fields': ('rankings', 'original_scores', 'final_scores', 'top_interests', 'submitted_at')
        }),
        ('Interest Analysis', {
            'fields': ('primary_interest', 'secondary_interest', 'tertiary_interest')
        }),
        ('Recommendations', {
            'fields': ('career_recommendations', 'study_recommendations')
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'nisn', 'student_class', 'test_status', 'created_at']
    list_filter = ['student_class', 'test_status', 'gender', 'entry_year']
    search_fields = ['name', 'nisn']
    list_editable = ['test_status']
    ordering = ['student_class', 'name']
    
    fieldsets = (
        ('Data Pribadi', {
            'fields': ('name', 'nisn', 'gender', 'birth_date', 'birth_place')
        }),
        ('Data Akademik', {
            'fields': ('student_class', 'entry_year')
        }),
        ('Status Tes', {
            'fields': ('test_status', 'test_date')
        }),
        ('Kontak', {
            'fields': ('phone', 'address', 'parent_phone'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Prestasi)
class PrestasiAdmin(admin.ModelAdmin):
    list_display = ['student', 'nama', 'jenis', 'tingkat', 'peringkat', 'tahun']
    list_filter = ['jenis', 'tingkat', 'tahun']
    search_fields = ['student__name', 'nama']
    raw_id_fields = ['student']

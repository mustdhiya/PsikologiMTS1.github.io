from django.contrib import admin
from .models import RMIBCategory, RMIBScore, TestSession

@admin.register(RMIBCategory)
class RMIBCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description']
    search_fields = ['code', 'name']

@admin.register(RMIBScore)
class RMIBScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['student__name', 'student__nisn']
    raw_id_fields = ['student']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Student Info', {
            'fields': ('student', 'is_completed')
        }),
        ('RMIB Scores', {
            'fields': (
                ('outdoor', 'mechanical', 'computational', 'scientific'),
                ('personal', 'aesthetic', 'literary', 'musical'),
                ('social_service', 'clerical', 'practical', 'medical')
            )
        }),
        ('Test Metadata', {
            'fields': ('test_duration', 'total_questions', 'completed_questions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'start_time', 'current_question', 'is_completed']
    list_filter = ['is_completed', 'is_paused', 'start_time']
    search_fields = ['student__name']
    raw_id_fields = ['student']

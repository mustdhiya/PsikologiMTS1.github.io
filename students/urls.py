from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # ==================== MAIN STUDENT VIEWS ====================
    path('', views.StudentListView.as_view(), name='list'),
    path('create/', views.StudentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.StudentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='delete'),
    
    # ==================== AJAX ENDPOINTS ====================
    path('<int:pk>/delete-ajax/', views.delete_student_ajax, name='delete_ajax'),
    path('bulk-delete/', views.bulk_delete_students, name='bulk_delete'),
    path('<int:pk>/reset-password/', views.reset_student_password, name='reset_password'),
    path('<int:pk>/unlock-account/', views.unlock_student_account, name='unlock_account'),
    
    # ==================== IMPORT & EXPORT ====================
    path('batch-import/', views.BatchImportView.as_view(), name='batch_import'),
    path('export-csv/', views.export_students_csv, name='export_csv'),
    path('download-template/', views.download_csv_template, name='download_template'),
    
    # ==================== RMIB ENDPOINTS ====================
    path('<int:student_pk>/rmib/test/', views.rmib_test_interface, name='rmib_test'),
    path('<int:student_pk>/rmib/start/', views.start_rmib_test, name='rmib_start'),
    path('<int:student_pk>/rmib/save/', views.save_rmib_progress, name='rmib_save'),
    path('<int:student_pk>/rmib/load/', views.load_rmib_progress, name='rmib_load'),
    path('<int:student_pk>/rmib/submit/', views.submit_rmib_test, name='rmib_submit'),
    path('<int:student_pk>/rmib/result/', views.rmib_result_view, name='rmib_result'),
    path('<int:student_pk>/rmib/edit-confirmation/', views.rmib_edit_confirmation, name='rmib_edit_confirmation'),
    path('<int:student_pk>/rmib/restart/', views.rmib_restart_test, name='rmib_restart'),
    path('<int:student_pk>/rmib/submit-edited/', views.submit_rmib_test_edited, name='rmib_submit_edited'),
    path('<int:student_pk>/rmib/cancel-edit/', views.rmib_cancel_edit, name='rmib_cancel_edit'),
    
    # ==================== RMIB BATCH IMPORT ====================
    path('rmib-batch-import/', views.RMIBBatchImportView.as_view(), name='rmib_batch_import'),
    path('rmib-template-download/', views.download_rmib_template, name='download_rmib_template'),

    # ==================== API ENDPOINTS ====================
    path('api/achievement-types/', views.api_achievement_types, name='api_achievement_types'),
    path('api/rmib/autosave/<int:student_id>/', views.rmib_autosave_api, name='rmib_autosave_api'),

    # ==================== LEGACY COMPATIBILITY ====================
    path('add/', views.StudentCreateView.as_view()),
    path('import/', views.BatchImportView.as_view()),

    # ==================== CERTIFICATE PAGES ====================
    path('certificate/', views.student_certificate_page, name='certificate_page'),
    path('certificate/detail/', views.view_certificate, name='view_certificate'),
    path('certificate/summary/', views.view_summary, name='view_summary'),
    path('certificate/parent-report/', views.view_parent_report, name='view_parent_report'),

    
    # Certificate detail views
    path('certificate/view/<int:request_id>/', views.view_certificate, name='view_certificate'),    
    # Certificate actions
    path('certificate/request/<str:template_type>/', views.request_certificate, name='request_certificate'),
    path('certificate/download/<int:request_id>/', views.download_certificate_pdf, name='download_certificate'),
    path('certificate/cancel/<int:request_id>/', views.cancel_certificate_request, name='cancel_certificate'),
    path('certificate/status/<int:request_id>/', views.get_certificate_status, name='certificate_status'),
]

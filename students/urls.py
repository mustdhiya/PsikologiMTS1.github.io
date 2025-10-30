from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Main student views
    path('', views.StudentListView.as_view(), name='list'),
    path('create/', views.StudentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='delete'),
    
    # Import and export
    path('batch-import/', views.BatchImportView.as_view(), name='batch_import'),
    path('batch-import/', views.BatchImportView.as_view(), name='import_batch'),
    path('export-csv/', views.export_students_csv, name='export_csv'),
    path('download-template/', views.download_csv_template, name='download_template'),
    
    # AJAX endpoints
    path('<int:pk>/reset-password/', views.reset_student_password, name='reset_password'),
    path('<int:pk>/unlock-account/', views.unlock_student_account, name='unlock_account'),
    path('<int:pk>/delete-ajax/', views.delete_student_ajax, name='delete_ajax'),
    
    # Bulk operations
    path('bulk-delete/', views.bulk_delete_students, name='bulk_delete'),
    
    # RMIB URLs
    path('<int:student_pk>/rmib/', views.rmib_test_interface, name='rmib_test'),
    path('<int:student_pk>/rmib/start/', views.start_rmib_test, name='rmib_start'),
    path('<int:student_pk>/rmib/save/', views.save_rmib_progress, name='rmib_save'),
    path('<int:student_pk>/rmib/submit/', views.submit_rmib_test, name='rmib_submit'),
    path('<int:student_pk>/rmib/load/', views.load_rmib_progress, name='rmib_load'),
    path('<int:student_pk>/rmib/result/', views.rmib_result_view, name='rmib_result'),
    path('<int:student_pk>/rmib/export-pdf/', views.export_rmib_pdf, name='rmib_export_pdf'),  # ← TAMBAHKAN INI
    
    # Legacy compatibility
    path('add/', views.StudentCreateView.as_view()),
    path('import/', views.BatchImportView.as_view()),
]

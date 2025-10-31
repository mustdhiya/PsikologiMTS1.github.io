from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
import logging
import re
import json

from .models import Student
from .forms import StudentForm
from .models import Student, Prestasi
from .forms import StudentForm, PrestasiForm, StudentBatchImportForm

# Setup logging
logger = logging.getLogger(__name__)

class IsStaffMixin(UserPassesTestMixin):
    """Mixin to check if user is staff or admin"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class StudentListView(LoginRequiredMixin, ListView):
    """Enhanced student list view with advanced filtering and search"""
    model = Student
    template_name = 'students/list.html'
    context_object_name = 'students'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Student.objects.select_related('user').prefetch_related('prestasi').order_by('student_class', 'name')
        
        # Search functionality
        search = self.request.GET.get('search', '').strip()
        if search:
            search_terms = search.split()
            for term in search_terms:
                queryset = queryset.filter(
                    Q(name__icontains=term) | 
                    Q(nisn__icontains=term) |
                    Q(student_class__icontains=term) |
                    Q(birth_place__icontains=term)
                )
        
        # Filter by class
        class_filter = self.request.GET.get('class', '').strip()
        if class_filter:
            queryset = queryset.filter(student_class=class_filter)
            
        # Filter by status
        status_filter = self.request.GET.get('status', '').strip()
        if status_filter:
            queryset = queryset.filter(test_status=status_filter)
        
        # Filter by gender
        gender_filter = self.request.GET.get('gender', '').strip()
        if gender_filter:
            queryset = queryset.filter(gender=gender_filter)
        
        # Filter by entry year
        year_filter = self.request.GET.get('year', '').strip()
        if year_filter and year_filter.isdigit():
            queryset = queryset.filter(entry_year=int(year_filter))
        
        # Sorting
        sort = self.request.GET.get('sort', '').strip()
        if sort == 'name':
            queryset = queryset.order_by('name')
        elif sort == 'nisn':
            queryset = queryset.order_by('nisn')
        elif sort == 'class':
            queryset = queryset.order_by('student_class', 'name')
        elif sort == 'status':
            queryset = queryset.order_by('test_status', 'name')
        elif sort == 'date':
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Preserve search parameters
        context.update({
            'search': self.request.GET.get('search', ''),
            'class_filter': self.request.GET.get('class', ''),
            'status_filter': self.request.GET.get('status', ''),
            'gender_filter': self.request.GET.get('gender', ''),
            'year_filter': self.request.GET.get('year', ''),
            'sort': self.request.GET.get('sort', ''),
        })
        
        # Get filter options
        students = Student.objects.all()
        context.update({
            'available_classes': students.values_list('student_class', flat=True).distinct().order_by('student_class'),
            'available_years': students.values_list('entry_year', flat=True).distinct().order_by('-entry_year'),
            'status_choices': Student.STATUS_CHOICES,
            'gender_choices': Student.GENDER_CHOICES,
        })
        
        # Statistics
        context.update({
            'total_students': students.count(),
            'completed_tests': students.filter(test_status='completed').count(),
            'pending_tests': students.filter(test_status='pending').count(),
            'in_progress_tests': students.filter(test_status='in_progress').count(),
        })
        
        return context
class StudentDeleteView(LoginRequiredMixin, IsStaffMixin, DeleteView):
    """Enhanced student delete view with safety checks"""
    model = Student
    template_name = 'students/delete_confirm.html'
    context_object_name = 'student'
    success_url = reverse_lazy('students:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        context.update({
            'page_title': f'Hapus Siswa - {student.name}',
            'breadcrumb_title': 'Hapus Siswa',
            'has_user_account': bool(student.user),
            'has_prestasi': hasattr(student, 'prestasi') and student.prestasi.exists(),
            'prestasi_count': student.prestasi.count() if hasattr(student, 'prestasi') else 0,
            'has_test_results': student.test_status == 'completed',
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.name
        student_nisn = student.nisn
        
        try:
            with transaction.atomic():
                # Delete related user account if exists
                if student.user:
                    user = student.user
                    user.delete()
                    logger.info(f"User account deleted for student: {student_name}")
                
                # Delete student (this will cascade to related objects)
                student.delete()
                
                messages.success(
                    request, 
                    f'Siswa {student_name} (NISN: {student_nisn}) berhasil dihapus dari sistem!'
                )
                logger.info(f"Student deleted: {student_name} (NISN: {student_nisn}) by {request.user.username}")
                
        except Exception as e:
            logger.error(f"Error deleting student {student_name}: {str(e)}")
            messages.error(request, f'Terjadi kesalahan saat menghapus siswa: {str(e)}')
            return redirect('students:detail', pk=student.pk)
        
        return redirect(self.success_url)

@require_POST
@login_required
def bulk_delete_students(request):
    """Bulk delete multiple students - WORKING SOLUTION"""
    print("Bulk delete called")  # Debug
    
    if not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk menghapus data')
        return redirect('students:list')
    
    try:
        student_ids = request.POST.getlist('student_ids')
        print(f"Student IDs to delete: {student_ids}")  # Debug
        
        if not student_ids:
            messages.error(request, 'Tidak ada siswa yang dipilih untuk dihapus')
            return redirect('students:list')
        
        try:
            student_ids = [int(sid) for sid in student_ids if sid.isdigit()]
        except ValueError:
            messages.error(request, 'ID siswa tidak valid')
            return redirect('students:list')
        
        if not student_ids:
            messages.error(request, 'ID siswa tidak valid')
            return redirect('students:list')
        
        students = Student.objects.filter(id__in=student_ids)
        total_count = students.count()
        
        if total_count == 0:
            messages.error(request, 'Siswa yang dipilih tidak ditemukan')
            return redirect('students:list')
        
        # Get student data for logging
        student_data = list(students.values('id', 'name', 'nisn', 'user_id'))
        student_names = [s['name'] for s in student_data]
        print(f"Deleting students: {student_names}")  # Debug
        
        # FIXED: Delete without atomic transaction to avoid cascade issues
        deleted_count = 0
        deleted_names = []
        failed_names = []
        
        for student_info in student_data:
            try:
                student = Student.objects.get(id=student_info['id'])
                student_name = student.name
                
                # METHOD 1: Change relationship before delete
                user_to_delete = None
                if student.user:
                    user_to_delete = student.user
                    # Break the relationship first
                    student.user = None
                    student.save()
                    print(f"Cleared user relationship for: {student_name}")
                
                # Delete student first (this will not cascade to user anymore)
                student.delete()
                print(f"Student deleted: {student_name}")
                
                # Now safely delete the user
                if user_to_delete:
                    try:
                        # Delete user without CASCADE issues
                        user_to_delete.delete()
                        print(f"User deleted for: {student_name}")
                    except Exception as user_error:
                        print(f"Warning - user delete failed for {student_name}: {user_error}")
                
                deleted_count += 1
                deleted_names.append(student_name)
                
            except Student.DoesNotExist:
                print(f"Student {student_info['id']} not found")
                continue
            except Exception as student_error:
                print(f"Error deleting student {student_info.get('name', student_info['id'])}: {student_error}")
                failed_names.append(student_info.get('name', f"ID:{student_info['id']}"))
                continue
        
        # Provide comprehensive feedback
        if deleted_count > 0:
            messages.success(
                request, 
                f'✅ {deleted_count} siswa berhasil dihapus dari sistem!'
            )
            logger.info(f"Bulk delete success: {deleted_count}/{total_count} students deleted by {request.user.username}")
        
        if failed_names:
            messages.warning(
                request,
                f'⚠️ {len(failed_names)} siswa gagal dihapus: {", ".join(failed_names[:5])}'
            )
        
        print(f"Final result: {deleted_count}/{total_count} students deleted")
        return redirect('students:list')
        
    except Exception as e:
        logger.error(f"Bulk delete error: {str(e)}")
        print(f"Bulk delete error: {str(e)}")  # Debug
        messages.error(request, f'Terjadi kesalahan saat menghapus siswa: {str(e)}')
        return redirect('students:list')

@require_POST
@login_required
def delete_student_ajax(request, pk):
    """AJAX endpoint for deleting student - WORKING SOLUTION"""
    print(f"AJAX delete called for student ID: {pk}")  # Debug
    
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        student = get_object_or_404(Student, pk=pk)
        student_name = student.name
        student_nisn = student.nisn
        
        print(f"Attempting to delete student: {student_name}")  # Debug
        
        # FIXED: Break user relationship first to avoid cascade issues
        user_to_delete = None
        if student.user:
            user_to_delete = student.user
            # Break the relationship
            student.user = None
            student.save()
            print(f"Cleared user relationship for: {student_name}")
        
        # Delete student (no more cascade issues)
        student.delete()
        print(f"Student deleted: {student_name}")
        
        # Delete user separately if exists
        if user_to_delete:
            try:
                user_to_delete.delete()
                print(f"User account deleted for: {student_name}")
            except Exception as user_error:
                print(f"Warning - user delete failed: {user_error}")
        
        logger.info(f"Student deleted via AJAX: {student_name} (NISN: {student_nisn}) by {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Siswa {student_name} berhasil dihapus!',
            'redirect_url': str(reverse('students:list'))
        })
        
    except Exception as e:
        logger.error(f"AJAX delete error: {str(e)}")
        print(f"Delete error: {str(e)}")  # Debug
        return JsonResponse({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }, status=500)


class StudentCreateView(LoginRequiredMixin, IsStaffMixin, CreateView):
    """Enhanced student creation view with validation"""
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    success_url = reverse_lazy('students:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Tambah Siswa Baru',
            'form_action': 'Tambah',
            'breadcrumb_title': 'Tambah Siswa',
        })
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                student = form.save()
                
                user, password = student.create_user_account()
                
                messages.success(
                    self.request, 
                    f'Siswa {student.name} berhasil ditambahkan! '
                    f'NISN: {student.nisn}, Password: {password}'
                )
                
                # Log the creation
                logger.info(f"Student created: {student.name} (NISN: {student.nisn}) by {self.request.user.username}")
                
                return super().form_valid(form)
                
        except IntegrityError:
            messages.error(self.request, 'NISN sudah ada dalam sistem!')
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            messages.error(self.request, 'Terjadi kesalahan saat menyimpan data siswa')
            return self.form_invalid(form)

class StudentDetailView(LoginRequiredMixin, DetailView):
    """Enhanced student detail view"""
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'
    
    def get_queryset(self):
        return Student.objects.select_related('user').prefetch_related('prestasi')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        context.update({
            'prestasi_list': student.prestasi.all().order_by('-tahun', 'tingkat'),
            'has_user_account': bool(student.user),
            'account_status': 'Aktif' if student.user else 'Tidak Ada',
            'login_attempts': student.login_attempts,
            'is_locked': student.is_locked,
            'last_login': student.user.last_login if student.user else None,
        })
        
        # Test status info
        if student.test_status == 'completed' and student.test_date:
            context['test_completed_date'] = student.test_date
        
        return context

class StudentUpdateView(LoginRequiredMixin, IsStaffMixin, UpdateView):
    """Enhanced student update view"""
    model = Student
    form_class = StudentForm
    template_name = 'students/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'Edit Data - {self.object.name}',
            'form_action': 'Update',
            'breadcrumb_title': 'Edit Siswa',
        })
        return context
    
    def get_success_url(self):
        return reverse_lazy('students:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                old_nisn = Student.objects.get(pk=self.object.pk).nisn
                new_nisn = form.cleaned_data['nisn']
                
                student = form.save()
                
                # Update user account if NISN changed
                if old_nisn != new_nisn and student.user:
                    student.user.username = new_nisn
                    student.user.email = f"{new_nisn}@student.mts1samarinda.id"
                    student.user.save()
                
                # Update name in user account
                if student.user:
                    name_parts = student.name.split()
                    student.user.first_name = name_parts[0]
                    student.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    student.user.save()
                
                messages.success(self.request, f'Data siswa {student.name} berhasil diperbarui!')
                logger.info(f"Student updated: {student.name} (NISN: {student.nisn}) by {self.request.user.username}")
                
                return super().form_valid(form)
                
        except IntegrityError:
            messages.error(self.request, 'NISN sudah digunakan siswa lain!')
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            messages.error(self.request, 'Terjadi kesalahan saat menyimpan data')
            return self.form_invalid(form)

@method_decorator(csrf_protect, name='dispatch')
class BatchImportView(LoginRequiredMixin, IsStaffMixin, TemplateView):
    """Enhanced batch import with better error handling and UI"""
    template_name = 'students/batch_import.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Batch Import Siswa',
            'breadcrumb_title': 'Import Data',
            'max_file_size': '5MB',
            'max_records': 1000,
            'required_columns': ['nama', 'nisn', 'kelas', 'jenis_kelamin', 'tanggal_lahir'],
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle both AJAX and form submissions"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax_upload(request)
        else:
            return self.handle_form_upload(request)
    
    def handle_ajax_upload(self, request):
        """Handle AJAX file upload with detailed JSON response"""
        try:
            if 'csv_file' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'File CSV tidak ditemukan',
                    'error_type': 'no_file'
                }, status=400)
            
            csv_file = request.FILES['csv_file']
            
            # Validate file
            validation_result = self.validate_file(csv_file)
            if not validation_result['valid']:
                return JsonResponse({
                    'success': False,
                    'message': validation_result['message'],
                    'errors': validation_result.get('errors', []),
                    'error_type': 'validation_error'
                }, status=400)
            
            # Process CSV
            result = self.process_csv_file(csv_file)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': f"Import berhasil! {result['successful']} siswa ditambahkan.",
                    'results': {
                        'total_processed': result['total_processed'],
                        'successful': result['successful'],
                        'errors': result['errors'],
                        'duplicates': result['duplicates'],
                        'error_details': result['error_details'][:10],  # Limit to 10 errors
                    },
                    'redirect_url': reverse_lazy('students:list')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': result['message'],
                    'errors': result.get('error_details', [])[:10],
                    'error_type': 'processing_error'
                }, status=422)
                
        except Exception as e:
            logger.error(f"CSV upload error: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'Terjadi kesalahan internal server',
                'error_type': 'server_error'
            }, status=500)
    
    def handle_form_upload(self, request):
        """Handle traditional form upload with redirect"""
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Silakan pilih file CSV untuk diupload')
            return redirect('students:batch_import')
        
        csv_file = request.FILES['csv_file']
        
        # Validate file
        validation_result = self.validate_file(csv_file)
        if not validation_result['valid']:
            messages.error(request, validation_result['message'])
            if validation_result.get('errors'):
                for error in validation_result['errors'][:5]:  # Show max 5 errors
                    messages.warning(request, error)
            return redirect('students:batch_import')
        
        # Process CSV
        result = self.process_csv_file(csv_file)
        
        if result['success']:
            messages.success(request, f"Import berhasil! {result['successful']} siswa ditambahkan.")
            if result['errors'] > 0:
                messages.warning(request, f"{result['errors']} record gagal diproses.")
            if result['duplicates'] > 0:
                messages.info(request, f"{result['duplicates']} record duplikat diabaikan.")
        else:
            messages.error(request, result['message'])
            # Show some error details
            for error in result.get('error_details', [])[:5]:
                messages.warning(request, error)
        
        return redirect('students:list')
        
    def validate_file(self, file):
        """Comprehensive file validation with detailed error reporting"""
        try:
            if not file.name.lower().endswith('.csv'):
                return {
                    'valid': False,
                    'message': 'File harus berformat CSV (.csv)',
                    'error_code': 'invalid_extension'
                }
            
            if file.size > 5 * 1024 * 1024:
                return {
                    'valid': False,
                    'message': f'Ukuran file terlalu besar ({file.size // 1024 // 1024}MB). Maksimal 5MB',
                    'error_code': 'file_too_large'
                }
            
            if file.size == 0:
                return {
                    'valid': False,
                    'message': 'File kosong. Pilih file CSV yang berisi data',
                    'error_code': 'empty_file'
                }
            
            # Read and validate CSV structure
            file.seek(0)  # Reset file pointer
            try:
                content = file.read().decode('utf-8-sig')  # Handle BOM
            except UnicodeDecodeError:
                try:
                    file.seek(0)
                    content = file.read().decode('latin-1')
                except UnicodeDecodeError:
                    return {
                        'valid': False,
                        'message': 'File tidak dapat dibaca. Pastikan encoding UTF-8 atau Latin-1',
                        'error_code': 'encoding_error'
                    }
            
            file.seek(0)  # Reset again for later use
            
            if not content.strip():
                return {
                    'valid': False,
                    'message': 'File CSV kosong atau hanya berisi whitespace',
                    'error_code': 'empty_content'
                }
            
            lines = content.strip().split('\n')
            if len(lines) < 2:
                return {
                    'valid': False,
                    'message': 'File CSV harus memiliki minimal header dan 1 baris data',
                    'error_code': 'insufficient_data'
                }
            
            # Auto-detect delimiter FIRST
            header_line = lines[0].strip()
            delimiter = self.detect_delimiter(header_line)
            
            # Parse header with detected delimiter
            header_cols = []
            if delimiter:
                # Split and clean header columns
                raw_cols = header_line.split(delimiter)
                header_cols = [col.strip().lower() for col in raw_cols if col.strip()]
            
            # Expected columns
            expected_columns = ['nama', 'nisn', 'kelas', 'jenis_kelamin', 'tanggal_lahir']
            
            # FIXED: Check if all required columns are present
            missing_cols = []
            for expected_col in expected_columns:
                if not any(self.normalize_column_name(header_col) == self.normalize_column_name(expected_col) 
                        for header_col in header_cols):
                    missing_cols.append(expected_col)
            
            if missing_cols:
                return {
                    'valid': False,
                    'message': f'Kolom yang diperlukan tidak ditemukan: {", ".join(missing_cols)}',
                    'errors': [
                        f'Header ditemukan: {", ".join(header_cols)}',
                        f'Header yang diperlukan: {", ".join(expected_columns)}',
                        f'Pastikan header persis sama dengan format template'
                    ],
                    'error_code': 'missing_columns'
                }
            
            extra_cols = []
            for header_col in header_cols:
                if not any(self.normalize_column_name(header_col) == self.normalize_column_name(expected_col) 
                        for expected_col in expected_columns):
                    extra_cols.append(header_col)
            
            data_lines = len(lines) - 1  # Exclude header
            if data_lines > 1000:
                return {
                    'valid': False,
                    'message': f'Terlalu banyak record ({data_lines}). Maksimal 1000 siswa per upload',
                    'error_code': 'too_many_records'
                }
            
            # Validate a few sample rows
            sample_errors = self.validate_sample_rows(lines[1:6], delimiter, header_cols)
            if sample_errors:
                return {
                    'valid': False,
                    'message': 'Format data tidak valid pada beberapa baris',
                    'errors': sample_errors,
                    'error_code': 'data_format_error'
                }
            
            validation_result = {
                'valid': True,
                'total_records': data_lines,
                'delimiter': delimiter,
                'header_cols': header_cols
            }
            
            # Add warnings for extra columns
            if extra_cols:
                validation_result['warnings'] = [f'Kolom tambahan akan diabaikan: {", ".join(extra_cols)}']
            
            return validation_result
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}", exc_info=True)
            return {
                'valid': False,
                'message': 'Terjadi kesalahan saat memvalidasi file',
                'error_code': 'validation_exception'
            }

    def normalize_column_name(self, col_name):
        """Normalize column name for comparison"""
        if not col_name:
            return ''
        
        # Remove spaces, underscores, and convert to lowercase
        normalized = col_name.lower().strip()
        normalized = normalized.replace('_', '').replace(' ', '')
        
        # Handle common variations
        variations = {
            'namalengkap': 'nama',
            'namasiswa': 'nama',
            'jeniskelamin': 'jenis_kelamin',
            'gender': 'jenis_kelamin',
            'tanggallahir': 'tanggal_lahir',
            'tgllahir': 'tanggal_lahir',
            'birthdate': 'tanggal_lahir',
            'class': 'kelas',
            'studentclass': 'kelas',
        }
        
        return variations.get(normalized, normalized)

    def detect_delimiter(self, header):
        """Enhanced delimiter detection"""
        if not header:
            return ','
        
        delimiters = {',': 0, ';': 0, '\t': 0, '|': 0}
        
        for delimiter in delimiters:
            delimiters[delimiter] = header.count(delimiter)
        
        # Return the delimiter with highest count (and > 0)
        best_delimiter = max(delimiters.items(), key=lambda x: x[1])
        
        if best_delimiter[1] > 0:
            return best_delimiter[0]
        
        return ','  # Default to comma

    def validate_sample_rows(self, sample_rows, delimiter, header_cols):
        """Enhanced sample row validation"""
        errors = []
        expected_columns_count = len(header_cols)
        
        for i, row in enumerate(sample_rows[:3], 1):
            if not row.strip():
                continue
            
            cols = row.split(delimiter)
            actual_cols_count = len([col for col in cols if col.strip()])
            
            if actual_cols_count != expected_columns_count:
                errors.append(
                    f'Baris {i + 1}: Jumlah kolom tidak sesuai '
                    f'(ditemukan {actual_cols_count}, diperlukan {expected_columns_count})'
                )
            
            # Basic NISN validation (assuming NISN is in position based on header)
            try:
                nisn_index = None
                for idx, header in enumerate(header_cols):
                    if self.normalize_column_name(header) == 'nisn':
                        nisn_index = idx
                        break
                
                if nisn_index is not None and len(cols) > nisn_index:
                    nisn = cols[nisn_index].strip()
                    if nisn and (not nisn.isdigit() or len(nisn) != 10):
                        errors.append(f'Baris {i + 1}: Format NISN tidak valid ({nisn})')
            except (IndexError, ValueError):
                pass  # Skip if can't validate NISN
        
        return errors[:3]  # Return max 3 errors

    def process_csv_file(self, file):
        """Enhanced CSV processing with better column mapping"""
        result = {
            'success': False,
            'total_processed': 0,
            'successful': 0,
            'errors': 0,
            'duplicates': 0,
            'error_details': [],
            'message': ''
        }
        
        try:
            file.seek(0)
            content = file.read()
            
            # Try different encodings
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    content_str = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                result['message'] = 'Tidak dapat membaca file dengan encoding yang didukung'
                return result
            
            # Auto-detect delimiter
            lines = content_str.strip().split('\n')
            if not lines:
                result['message'] = 'File kosong'
                return result
                
            delimiter = self.detect_delimiter(lines[0])
            
            csv_reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
            
            # Normalize and map fieldnames
            if csv_reader.fieldnames:
                fieldname_mapping = {}
                normalized_fieldnames = []
                
                for original_name in csv_reader.fieldnames:
                    normalized = self.normalize_column_name(original_name)
                    fieldname_mapping[normalized] = original_name.strip()
                    normalized_fieldnames.append(normalized)
                
                # Verify we have all required fields
                required_fields = ['nama', 'nisn', 'kelas', 'jenis_kelamin', 'tanggal_lahir']
                missing_fields = [field for field in required_fields if field not in normalized_fieldnames]
                
                if missing_fields:
                    result['message'] = f'Field yang diperlukan tidak ditemukan: {", ".join(missing_fields)}'
                    return result
            
            # Track processed NISNs
            processed_nisns = set()
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_reader, start=2):
                    result['total_processed'] += 1
                    
                    try:
                        # Map row data using field mapping
                        mapped_row = {}
                        for normalized_field, original_field in fieldname_mapping.items():
                            if normalized_field in ['nama', 'nisn', 'kelas', 'jenis_kelamin', 'tanggal_lahir']:
                                mapped_row[normalized_field] = row.get(original_field, '').strip()
                        
                        cleaned_data = self.clean_row_data_mapped(mapped_row, row_num)
                        
                        if not cleaned_data['valid']:
                            result['errors'] += len(cleaned_data['errors'])
                            result['error_details'].extend(cleaned_data['errors'])
                            continue
                        
                        data = cleaned_data['data']
                        
                        if data['nisn'] in processed_nisns:
                            result['duplicates'] += 1
                            result['error_details'].append(
                                f"Baris {row_num}: NISN {data['nisn']} duplikat dalam file"
                            )
                            continue
                        
                        processed_nisns.add(data['nisn'])
                        
                        if Student.objects.filter(nisn=data['nisn']).exists():
                            result['duplicates'] += 1
                            result['error_details'].append(
                                f"Baris {row_num}: NISN {data['nisn']} sudah ada dalam sistem"
                            )
                            continue
                        
                        student = Student.objects.create(**data)
                        
                        try:
                            user, password = student.create_user_account()
                        except Exception as e:
                            logger.warning(f"Failed to create user account for {student.name}: {str(e)}")
                            # Student is still created, just without user account
                        
                        result['successful'] += 1
                        
                    except IntegrityError as e:
                        result['errors'] += 1
                        error_msg = f"Baris {row_num}: Data tidak valid (kemungkinan NISN duplikat)"
                        result['error_details'].append(error_msg)
                        logger.warning(f"IntegrityError: {error_msg} - {str(e)}")
                        
                    except Exception as e:
                        result['errors'] += 1
                        error_msg = f"Baris {row_num}: {str(e)}"
                        result['error_details'].append(error_msg)
                        logger.error(f"Row processing error: {error_msg}")
            
            # Determine success status and message
            if result['successful'] > 0:
                result['success'] = True
                result['message'] = f"Import selesai. {result['successful']} siswa berhasil ditambahkan."
                
                if result['errors'] > 0 or result['duplicates'] > 0:
                    result['message'] += f" {result['errors']} error, {result['duplicates']} duplikat."
            else:
                result['message'] = "Tidak ada siswa yang berhasil ditambahkan."
                
            # Log successful import
            if result['successful'] > 0:
                logger.info(f"Batch import completed: {result['successful']} students created by {self.request.user.username}")
                
        except Exception as e:
            logger.error(f"CSV processing error: {str(e)}", exc_info=True)
            result['message'] = f'Terjadi kesalahan saat memproses file CSV: {str(e)}'
            result['error_details'].append(f"System error: {str(e)}")
        
        return result

    def clean_row_data_mapped(self, row, row_num):
        """Clean row data with mapped field names"""
        errors = []
        
        try:
            # Extract and clean data
            nama = str(row.get('nama', '')).strip()
            nisn = str(row.get('nisn', '')).strip()
            kelas = str(row.get('kelas', '')).strip().upper()
            jenis_kelamin = str(row.get('jenis_kelamin', '')).strip().upper()
            tanggal_lahir = str(row.get('tanggal_lahir', '')).strip()
            
            # Validate nama
            if not nama:
                errors.append(f"Baris {row_num}: Nama tidak boleh kosong")
            elif len(nama) < 2:
                errors.append(f"Baris {row_num}: Nama terlalu pendek (minimal 2 karakter)")
            elif len(nama) > 200:
                errors.append(f"Baris {row_num}: Nama terlalu panjang (maksimal 200 karakter)")
            elif not re.match(r'^[a-zA-Z\s.\']+$', nama):
                errors.append(f"Baris {row_num}: Nama hanya boleh berisi huruf, spasi, titik, dan apostrof")
            
            # Validate NISN
            if not nisn:
                errors.append(f"Baris {row_num}: NISN tidak boleh kosong")
            elif not nisn.isdigit():
                errors.append(f"Baris {row_num}: NISN harus berupa angka (ditemukan: {nisn})")
            elif len(nisn) != 10:
                errors.append(f"Baris {row_num}: NISN harus 10 digit (ditemukan: {len(nisn)} digit)")
            
            # Validate kelas
            if not kelas:
                errors.append(f"Baris {row_num}: Kelas tidak boleh kosong")
            elif not re.match(r'^[789][A-Z]$', kelas):
                errors.append(f"Baris {row_num}: Format kelas tidak valid (harus 7A, 8B, 9C, dll. Ditemukan: {kelas})")
            
            # Validate jenis kelamin
            if jenis_kelamin not in ['L', 'P']:
                errors.append(f"Baris {row_num}: Jenis kelamin harus L atau P (ditemukan: {jenis_kelamin})")
            
            # Validate and parse tanggal lahir
            birth_date = None
            if not tanggal_lahir:
                errors.append(f"Baris {row_num}: Tanggal lahir tidak boleh kosong")
            else:
                # Try multiple date formats
                date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%y']
                parsed = False
                
                for date_format in date_formats:
                    try:
                        birth_date = datetime.strptime(tanggal_lahir, date_format).date()
                        # Handle 2-digit years
                        if birth_date.year < 1950:  # Assume it's 20xx
                            birth_date = birth_date.replace(year=birth_date.year + 100)
                        parsed = True
                        break
                    except ValueError:
                        continue
                
                if not parsed:
                    errors.append(f"Baris {row_num}: Format tanggal lahir tidak valid (gunakan DD/MM/YYYY)")
                else:
                    # Validate date range
                    today = datetime.now().date()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    
                    if age < 10 or age > 25:
                        errors.append(f"Baris {row_num}: Usia tidak wajar ({age} tahun)")
                    
                    if birth_date > today:
                        errors.append(f"Baris {row_num}: Tanggal lahir tidak boleh di masa depan")
            
            if errors:
                return {'valid': False, 'errors': errors}
            
            # Return cleaned data
            return {
                'valid': True,
                'data': {
                    'name': nama.title().strip(),
                    'nisn': nisn,
                    'student_class': kelas,
                    'gender': jenis_kelamin,
                    'birth_date': birth_date,
                    'entry_year': datetime.now().year,
                    'test_status': 'pending',
                    'birth_place': '',
                    'phone': '',
                    'address': '',
                    'parent_phone': '',
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Baris {row_num}: Error memproses data - {str(e)}"]
            }


@require_http_methods(["POST"])
@csrf_protect
def reset_student_password(request, pk):
    """Reset password for specific student (AJAX endpoint)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        student = get_object_or_404(Student, pk=pk)
        new_password = student.reset_password()
        
        if new_password:
            logger.info(f"Password reset by {request.user.username} for student: {student.name}")
            return JsonResponse({
                'success': True,
                'message': f'Password berhasil direset untuk {student.name}',
                'new_password': new_password
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Gagal mereset password. Siswa belum memiliki akun user.'
            })
            
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Terjadi kesalahan saat mereset password'
        })

@require_http_methods(["POST"])
@csrf_protect 
def unlock_student_account(request, pk):
    """Unlock student account (AJAX endpoint)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        student = get_object_or_404(Student, pk=pk)
        student.unlock_account()
        
        logger.info(f"Account unlocked by {request.user.username} for student: {student.name}")
        return JsonResponse({
            'success': True,
            'message': f'Akun {student.name} berhasil dibuka kembali'
        })
        
    except Exception as e:
        logger.error(f"Account unlock error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Terjadi kesalahan saat membuka akun'
        })

def export_students_csv(request):
    """Export students data as CSV"""
    if not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki izin untuk mengekspor data')
        return redirect('students:list')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="data_siswa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['NISN', 'Nama', 'Kelas', 'Jenis Kelamin', 'Tanggal Lahir', 'Tempat Lahir', 'Status Tes', 'Tahun Masuk'])
    
    students = Student.objects.all().order_by('student_class', 'name')
    for student in students:
        writer.writerow([
            student.nisn,
            student.name,
            student.student_class,
            student.get_gender_display(),
            student.birth_date.strftime('%d/%m/%Y'),
            student.birth_place,
            student.get_test_status_display(),
            student.entry_year
        ])
    
    logger.info(f"Students data exported by {request.user.username}")
    return response

def download_csv_template(request):
    """Download CSV template for batch import"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="template_import_siswa.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['nama', 'nisn', 'kelas', 'jenis_kelamin', 'tanggal_lahir'])
    writer.writerow(['Ahmad Fauzan', '1234567890', '8A', 'L', '15/03/2010'])
    writer.writerow(['Siti Nurhaliza', '0987654321', '8A', 'P', '22/07/2010'])
    
    return response

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from .models import Student, RMIBResult, Prestasi
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ==================== RMIB CATEGORIES - DEFINE HERE ====================
RMIB_CATEGORIES = {
    'outdoor': {
        'name': 'Outdoor (Alam Terbuka)',
        'description': 'Aktivitas yang berhubungan dengan alam dan lingkungan luar',
        'icon': 'fas fa-tree',
        'color': 'green'
    },
    'mechanical': {
        'name': 'Mechanical (Mekanik)',
        'description': 'Pekerjaan dengan mesin, alat, dan teknologi',
        'icon': 'fas fa-cog',
        'color': 'blue'
    },
    'computational': {
        'name': 'Computational (Komputasi)',
        'description': 'Bekerja dengan angka, data, dan analisis',
        'icon': 'fas fa-calculator',
        'color': 'purple'
    },
    'scientific': {
        'name': 'Scientific (Sains)',
        'description': 'Penelitian, eksperimen, dan penemuan ilmiah',
        'icon': 'fas fa-flask',
        'color': 'indigo'
    },
    'personal_contact': {
        'name': 'Personal Contact (Hubungan Personal)',
        'description': 'Berinteraksi dan membantu orang lain',
        'icon': 'fas fa-handshake',
        'color': 'pink'
    },
    'aesthetic': {
        'name': 'Aesthetic (Estetika)',
        'description': 'Seni, desain, dan keindahan',
        'icon': 'fas fa-palette',
        'color': 'orange'
    },
    'literary': {
        'name': 'Literary (Sastra)',
        'description': 'Menulis, membaca, dan komunikasi verbal',
        'icon': 'fas fa-book',
        'color': 'teal'
    },
    'musical': {
        'name': 'Musical (Musik)',
        'description': 'Musik, suara, dan harmoni',
        'icon': 'fas fa-music',
        'color': 'red'
    },
    'social_service': {
        'name': 'Social Service (Pelayanan Sosial)',
        'description': 'Membantu masyarakat dan kesejahteraan sosial',
        'icon': 'fas fa-hands-helping',
        'color': 'amber'
    },
    'clerical': {
        'name': 'Clerical (Administratif)',
        'description': 'Administrasi, organisasi, dan tata kelola',
        'icon': 'fas fa-file-alt',
        'color': 'gray'
    },
    'practical': {
        'name': 'Practical (Praktis)',
        'description': 'Pekerjaan praktis dan aplikatif sehari-hari',
        'icon': 'fas fa-tools',
        'color': 'yellow'
    },
    'medical': {
        'name': 'Medical (Medis)',
        'description': 'Kesehatan dan perawatan medis',
        'icon': 'fas fa-heartbeat',
        'color': 'red'
    }
}


# ==================== RMIB TEST VIEWS ====================

@login_required
def rmib_test_interface(request, student_pk):
    """Display RMIB test interface"""
    student = get_object_or_404(Student, pk=student_pk)
    
    # Check if student can take test
    if not student.can_take_test():
        messages.warning(request, 'Siswa ini sudah menyelesaikan tes RMIB.')
        return redirect('students:detail', pk=student_pk)
    
    # Check if there's existing progress
    has_progress = hasattr(student, 'rmib_result') and student.rmib_result.levels
    
    # Convert to JSON for template
    rmib_categories_json = json.dumps(RMIB_CATEGORIES)
    
    context = {
        'student': student,
        'rmib_categories': RMIB_CATEGORIES,
        'rmib_categories_json': rmib_categories_json,
        'has_progress': has_progress,
        'total_categories': len(RMIB_CATEGORIES)
    }
    
    return render(request, 'students/rmib_test.html', context)


@login_required
@require_http_methods(["POST"])
def start_rmib_test(request, student_pk):
    """Start RMIB test and update student status"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if student.test_status == 'pending':
            student.test_status = 'in_progress'
            student.test_date = timezone.now()
            student.save()
        
        logger.info(f"Started RMIB test for student {student.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Tes RMIB dimulai',
            'test_date': student.test_date.isoformat() if student.test_date else None
        })
    except Exception as e:
        logger.error(f"Start test error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def save_rmib_progress(request, student_pk):
    """Save RMIB test progress (autosave)"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        data = json.loads(request.body)
        
        levels = data.get('levels', {})
        
        # Get or create RMIB result
        rmib_result, created = RMIBResult.objects.get_or_create(
            student=student,
            defaults={
                'submitted_at': timezone.now(),
                'levels': levels
            }
        )
        
        # Update levels if not created
        if not created:
            rmib_result.levels = levels
            rmib_result.save()
        
        logger.info(f"Saved progress for {student.name}: {len(levels)} levels")
        
        return JsonResponse({
            'success': True,
            'message': 'Progress berhasil disimpan',
            'saved_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Save progress error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def load_rmib_progress(request, student_pk):
    """Load saved RMIB progress"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if hasattr(student, 'rmib_result') and student.rmib_result.levels:
            return JsonResponse({
                'success': True,
                'has_progress': True,
                'levels': student.rmib_result.levels,
                'saved_at': student.rmib_result.updated_at.isoformat()
            })
        else:
            return JsonResponse({
                'success': True,
                'has_progress': False,
                'levels': {}
            })
            
    except Exception as e:
        logger.error(f"Load progress error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def submit_rmib_test(request, student_pk):
    """Submit RMIB test - Level-Based"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        data = json.loads(request.body)
        levels = data.get('levels', {})
        
        logger.info(f"Submitting RMIB for student {student_pk}: {len(levels)} levels")
        
        # Validate - all 12 categories must have levels
        if len(levels) != 12:
            return JsonResponse({
                'success': False,
                'message': f'Semua 12 kategori harus diisi. Diterima: {len(levels)}'
            }, status=400)
        
        # Validate level range (1-12)
        for category, level in levels.items():
            try:
                level_int = int(level)
                if level_int < 1 or level_int > 12:
                    return JsonResponse({
                        'success': False,
                        'message': f'Level harus antara 1-12. Kategori {category}: {level}'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'Level harus berupa angka. Kategori {category}: {level}'
                }, status=400)
        
        # Create or update RMIB result
        rmib_result, created = RMIBResult.objects.get_or_create(
            student=student,
            defaults={'submitted_at': timezone.now()}
        )
        
        # Save levels dan calculate scores
        rmib_result.levels = levels
        rmib_result.calculate_scores()
        rmib_result.submitted_at = timezone.now()
        rmib_result.save()
        
        # Update student status
        student.test_status = 'completed'
        student.test_date = timezone.now()
        student.save(update_fields=['test_status', 'test_date'])
        
        logger.info(f"✅ RMIB submitted for {student.name}. Total: {rmib_result.total_score} poin")
        
        return JsonResponse({
            'success': True,
            'message': 'Tes RMIB berhasil diselesaikan!',
            'redirect_url': f'/students/{student_pk}/rmib/result/',
            'total_score': rmib_result.total_score,
            'primary_interest': rmib_result.primary_interest,
            'primary_level': rmib_result.primary_level
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data tidak valid'
        }, status=400)
    except Exception as e:
        logger.error(f"Submit error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def rmib_result_view(request, student_pk):
    """Display RMIB results - Level-Based"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        # Check if completed
        if not hasattr(student, 'rmib_result'):
            messages.warning(request, 'Anda belum menyelesaikan tes RMIB.')
            return redirect('students:rmib_test', student_pk=student_pk)
        
        rmib_result = student.rmib_result
        
        # Get ranking sorted by level (highest first)
        ranking_data = []
        for rank, (category_key, level) in enumerate(rmib_result.get_ranking_summary(), 1):
            category_info = RMIB_CATEGORIES.get(category_key, {})
            score = level * 5
            
            ranking_data.append({
                'rank': rank,
                'category_key': category_key,
                'category_name': category_info.get('name', category_key),
                'level': level,
                'score': score,
                'icon': category_info.get('icon', 'fas fa-circle')
            })
        
        # Get primary interest name
        primary_interest_info = RMIB_CATEGORIES.get(rmib_result.primary_interest, {})
        primary_interest_name = primary_interest_info.get('name', rmib_result.primary_interest)
        
        context = {
            'student': student,
            'rmib_result': rmib_result,
            'categories': ranking_data,
            'total_score': rmib_result.total_score,
            'primary_interest': primary_interest_name,
            'primary_level': rmib_result.primary_level,
            'prestasi_list': student.prestasi.all()
        }
        
        logger.info(f"✅ Displaying RMIB result for student {student.name}")
        
        return render(request, 'students/rmib_result.html', context)
    
    except Exception as e:
        logger.error(f"❌ RMIB result view error: {str(e)}", exc_info=True)
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('core:dashboard')


@login_required
def export_rmib_pdf(request, student_pk):
    """Export RMIB result to PDF - placeholder for now"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if not hasattr(student, 'rmib_result'):
            messages.error(request, 'Tidak ada hasil RMIB untuk diekspor.')
            return redirect('students:detail', pk=student_pk)
        
        # For now, redirect to result page
        # TODO: Implement PDF generation with WeasyPrint or ReportLab
        messages.info(request, 'Fitur export PDF akan segera tersedia.')
        return redirect('students:rmib_result', student_pk=student_pk)
    
    except Exception as e:
        logger.error(f"Export PDF error: {str(e)}")
        messages.error(request, f'Gagal mengekspor: {str(e)}')
        return redirect('students:detail', pk=student_pk)

# ==================== EDIT & RESTART RMIB ====================

@login_required
def rmib_edit_confirmation(request, student_pk):
    """Show confirmation before editing RMIB"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if not hasattr(student, 'rmib_result'):
            messages.error(request, 'Tidak ada hasil RMIB untuk diedit.')
            return redirect('students:detail', pk=student_pk)
        
        rmib_result = student.rmib_result
        
        # Check if result is completed
        if rmib_result.status != 'completed':
            messages.warning(request, 'Hanya hasil yang sudah diselesaikan yang dapat diedit.')
            return redirect('students:rmib_result', student_pk=student_pk)
        
        # Get ranking data for display
        ranking_data = []
        for rank, (category_key, level) in enumerate(rmib_result.get_ranking_summary(), 1):
            category_info = RMIB_CATEGORIES.get(category_key, {})
            score = level * 5
            
            ranking_data.append({
                'rank': rank,
                'category_key': category_key,
                'category_name': category_info.get('name', category_key),
                'level': level,
                'score': score
            })
        
        context = {
            'student': student,
            'rmib_result': rmib_result,
            'categories': ranking_data,
            'total_score': rmib_result.total_score,
            'submitted_at': rmib_result.submitted_at
        }
        
        return render(request, 'students/rmib_edit_confirmation.html', context)
    
    except Exception as e:
        logger.error(f"Edit confirmation error: {str(e)}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('students:detail', pk=student_pk)


@login_required
@require_http_methods(["POST"])
def rmib_restart_test(request, student_pk):
    """Restart RMIB test for editing"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if not hasattr(student, 'rmib_result'):
            return JsonResponse({
                'success': False,
                'message': 'Tidak ada hasil RMIB untuk diedit'
            }, status=400)
        
        rmib_result = student.rmib_result
        
        # Mark as in_progress for editing
        rmib_result.reset_for_editing()
        
        logger.info(f"Restarting RMIB for student {student.name} (Edit Mode)")
        
        return JsonResponse({
            'success': True,
            'message': 'Tes siap untuk diedit',
            'redirect_url': f'/students/{student_pk}/rmib/test/',
            'previous_levels': rmib_result.levels
        })
    
    except Exception as e:
        logger.error(f"Restart test error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def submit_rmib_test_edited(request, student_pk):
    """Submit edited RMIB test"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        data = json.loads(request.body)
        levels = data.get('levels', {})
        
        logger.info(f"Submitting edited RMIB for student {student_pk}")
        
        # Validate
        if len(levels) != 12:
            return JsonResponse({
                'success': False,
                'message': f'Semua 12 kategori harus diisi. Diterima: {len(levels)}'
            }, status=400)
        
        # Validate level range
        for category, level in levels.items():
            try:
                level_int = int(level)
                if level_int < 1 or level_int > 12:
                    return JsonResponse({
                        'success': False,
                        'message': f'Level harus antara 1-12. Kategori {category}: {level}'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'Level harus berupa angka. Kategori {category}: {level}'
                }, status=400)
        
        # Get existing result
        if not hasattr(student, 'rmib_result'):
            return JsonResponse({
                'success': False,
                'message': 'Hasil RMIB tidak ditemukan'
            }, status=400)
        
        rmib_result = student.rmib_result
        
        # Update levels and calculate scores
        rmib_result.levels = levels
        rmib_result.calculate_scores()
        rmib_result.status = 'completed'
        rmib_result.edited_at = timezone.now()
        rmib_result.save()
        
        logger.info(f"✅ Edited RMIB submitted for {student.name}. New Total: {rmib_result.total_score} poin")
        
        return JsonResponse({
            'success': True,
            'message': 'Hasil tes berhasil diperbarui!',
            'redirect_url': f'/students/{student_pk}/rmib/result/',
            'total_score': rmib_result.total_score,
            'edited_at': rmib_result.edited_at.isoformat()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format data tidak valid'
        }, status=400)
    except Exception as e:
        logger.error(f"Submit edited error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def rmib_cancel_edit(request, student_pk):
    """Cancel editing and revert to completed status"""
    try:
        student = get_object_or_404(Student, pk=student_pk)
        
        if not hasattr(student, 'rmib_result'):
            return JsonResponse({
                'success': False,
                'message': 'Hasil RMIB tidak ditemukan'
            }, status=400)
        
        rmib_result = student.rmib_result
        rmib_result.status = 'completed'
        rmib_result.save()
        
        logger.info(f"Cancelled edit for student {student.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Penyuntingan dibatalkan',
            'redirect_url': f'/students/{student_pk}/rmib/result/'
        })
    
    except Exception as e:
        logger.error(f"Cancel edit error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

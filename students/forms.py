from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date, datetime
import re
from .models import Student, Prestasi

class StudentForm(forms.ModelForm):
    """Enhanced student form with comprehensive validation"""
    
    class Meta:
        model = Student
        fields = [
            'name', 'nisn', 'gender', 'birth_date', 'birth_place', 
            'student_class', 'entry_year', 'phone', 'address', 'parent_phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Nama lengkap siswa',
                'maxlength': '200'
            }),
            'nisn': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': '10 digit NISN',
                'maxlength': '10',
                'pattern': '[0-9]{10}'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'type': 'date'
            }),
            'birth_place': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Tempat lahir'
            }),
            'student_class': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Contoh: 8A, 7B, 9C',
                'pattern': '[789][A-Z]'
            }),
            'entry_year': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'min': '2020',
                'max': '2030',
                'value': datetime.now().year
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Nomor HP siswa (opsional)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'rows': 3,
                'placeholder': 'Alamat lengkap (opsional)'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Nomor HP orang tua (opsional)'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('Nama tidak boleh kosong')
        
        if len(name) < 2:
            raise ValidationError('Nama terlalu pendek (minimal 2 karakter)')
        
        if len(name) > 200:
            raise ValidationError('Nama terlalu panjang (maksimal 200 karakter)')
        
        # Check for valid characters (letters, spaces, dots, apostrophes)
        if not re.match(r"^[a-zA-Z\s.\']+$", name):
            raise ValidationError('Nama hanya boleh berisi huruf, spasi, titik, dan apostrof')
        
        # Check for minimum word count
        if len(name.split()) < 2:
            raise ValidationError('Nama harus minimal 2 kata')
        
        return name.title()  # Convert to proper case
    
    def clean_nisn(self):
        nisn = self.cleaned_data.get('nisn', '').strip()
        
        if not nisn:
            raise ValidationError('NISN tidak boleh kosong')
        
        if not nisn.isdigit():
            raise ValidationError('NISN hanya boleh berisi angka')
        
        if len(nisn) != 10:
            raise ValidationError('NISN harus terdiri dari 10 digit')
        
        # Check for uniqueness (excluding current instance if updating)
        queryset = Student.objects.filter(nisn=nisn)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('NISN sudah digunakan siswa lain')
        
        return nisn
    
    def clean_student_class(self):
        student_class = self.cleaned_data.get('student_class', '').strip().upper()
        
        if not student_class:
            raise ValidationError('Kelas tidak boleh kosong')
        
        # Validate class format (7A, 8B, 9C, etc.)
        if not re.match(r'^[789][A-Z]$', student_class):
            raise ValidationError('Format kelas tidak valid (gunakan format: 7A, 8B, 9C)')
        
        return student_class
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        
        if not birth_date:
            raise ValidationError('Tanggal lahir tidak boleh kosong')
        
        # Check if date is not in the future
        if birth_date > date.today():
            raise ValidationError('Tanggal lahir tidak boleh di masa depan')
        
        # Check reasonable age range (10-25 years)
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 10:
            raise ValidationError(f'Usia terlalu muda ({age} tahun). Minimal 10 tahun')
        
        if age > 25:
            raise ValidationError(f'Usia terlalu tua ({age} tahun). Maksimal 25 tahun')
        
        return birth_date
    
    def clean_entry_year(self):
        entry_year = self.cleaned_data.get('entry_year')
        current_year = datetime.now().year
        
        if entry_year and (entry_year < 2020 or entry_year > current_year + 1):
            raise ValidationError(f'Tahun masuk harus antara 2020 - {current_year + 1}')
        
        return entry_year
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        
        if phone:
            # Remove common formatting characters
            phone = re.sub(r'[\s\-\(\)\+]', '', phone)
            
            # Check if it's a valid Indonesian phone number
            if not re.match(r'^(08|628|\+628)[0-9]{8,12}$', phone):
                raise ValidationError('Format nomor HP tidak valid (gunakan format: 08xxxxxxxxx)')
            
            # Normalize to 08xx format
            if phone.startswith('+628'):
                phone = '08' + phone[4:]
            elif phone.startswith('628'):
                phone = '08' + phone[3:]
        
        return phone
    
    def clean_parent_phone(self):
        parent_phone = self.cleaned_data.get('parent_phone', '').strip()
        
        if parent_phone:
            # Remove common formatting characters
            parent_phone = re.sub(r'[\s\-\(\)\+]', '', parent_phone)
            
            # Check if it's a valid Indonesian phone number
            if not re.match(r'^(08|628|\+628)[0-9]{8,12}$', parent_phone):
                raise ValidationError('Format nomor HP orang tua tidak valid (gunakan format: 08xxxxxxxxx)')
            
            # Normalize to 08xx format
            if parent_phone.startswith('+628'):
                parent_phone = '08' + parent_phone[4:]
            elif parent_phone.startswith('628'):
                parent_phone = '08' + parent_phone[3:]
        
        return parent_phone

class PrestasiForm(forms.ModelForm):
    """Enhanced prestasi form"""
    
    class Meta:
        model = Prestasi
        fields = ['jenis', 'nama', 'tingkat', 'peringkat', 'tahun', 'keterangan', 'sertifikat', 'bonus_score']
        widgets = {
            'jenis': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all'
            }),
            'nama': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Nama prestasi'
            }),
            'tingkat': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all'
            }),
            'peringkat': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Contoh: Juara 1, Harapan 2'
            }),
            'tahun': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'min': '2020',
                'max': datetime.now().year,
                'value': datetime.now().year
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'rows': 3,
                'placeholder': 'Keterangan tambahan (opsional)'
            }),
            'sertifikat': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'bonus_score': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'min': '0',
                'max': '100',
                'value': '0'
            }),
        }
    
    def clean_nama(self):
        nama = self.cleaned_data.get('nama', '').strip()
        
        if not nama:
            raise ValidationError('Nama prestasi tidak boleh kosong')
        
        if len(nama) < 3:
            raise ValidationError('Nama prestasi terlalu pendek (minimal 3 karakter)')
        
        if len(nama) > 200:
            raise ValidationError('Nama prestasi terlalu panjang (maksimal 200 karakter)')
        
        return nama.title()
    
    def clean_tahun(self):
        tahun = self.cleaned_data.get('tahun')
        current_year = datetime.now().year
        
        if tahun and (tahun < 2020 or tahun > current_year):
            raise ValidationError(f'Tahun prestasi harus antara 2020 - {current_year}')
        
        return tahun
    
    def clean_sertifikat(self):
        sertifikat = self.cleaned_data.get('sertifikat')
        
        if sertifikat:
            # Check file size (5MB limit)
            if sertifikat.size > 5 * 1024 * 1024:
                raise ValidationError('Ukuran file terlalu besar (maksimal 5MB)')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            file_extension = sertifikat.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Format file tidak didukung (gunakan: PDF, JPG, PNG)')
        
        return sertifikat

class StudentBatchImportForm(forms.Form):
    """Enhanced batch import form"""
    
    csv_file = forms.FileField(
        label='File CSV',
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'hidden',
            'id': 'csvFileInput'
        }),
        help_text='Upload file CSV dengan data siswa (maksimal 5MB, 1000 records)'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        
        if not file:
            raise ValidationError('File CSV wajib diupload')
        
        if not file.name.lower().endswith('.csv'):
            raise ValidationError('File harus berformat CSV (.csv)')
        
        if file.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError(f'Ukuran file terlalu besar ({file.size // 1024 // 1024}MB). Maksimal 5MB')
        
        if file.size == 0:
            raise ValidationError('File kosong. Pilih file yang berisi data')
        
        return file

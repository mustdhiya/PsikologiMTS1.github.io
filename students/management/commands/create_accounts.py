from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student

class Command(BaseCommand):
    help = 'Create user accounts untuk semua siswa yang belum punya akun'

    def handle(self, *args, **options):
        students = Student.objects.filter(user__isnull=True)
        
        if not students.exists():
            self.stdout.write(self.style.SUCCESS('✓ Semua siswa sudah punya akun!'))
            return
        
        self.stdout.write(f'Ditemukan {students.count()} siswa tanpa akun')
        
        success_count = 0
        error_count = 0
        
        for student in students:
            try:
                # Generate password
                student.generate_password()
                
                # Create account
                user = User.objects.create_user(
                    username=student.nisn,
                    email=f"{student.nisn}@student.mts1samarinda.id",
                    first_name=student.name.split()[0],
                    last_name=' '.join(student.name.split()[1:]) if len(student.name.split()) > 1 else '',
                    password=student.generated_password
                )
                
                student.user = user
                student.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {student.name} - Username: {student.nisn}, Password: {student.generated_password}'
                    )
                )
                success_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {student.name}: {str(e)}')
                )
                error_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n=== SELESAI ===')
        )
        self.stdout.write(f'Berhasil: {success_count}')
        self.stdout.write(f'Gagal: {error_count}')

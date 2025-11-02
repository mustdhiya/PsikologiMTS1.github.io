import csv
import os
from django.core.management.base import BaseCommand
from students.models import AchievementType


class Command(BaseCommand):
    help = 'Import achievement types from CSV file with RMIB categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='klasifikasi_lengkap_prestasi_rmib.csv',
            help='Path to CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        clear = options['clear']

        # Check if file exists
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'❌ File not found: {csv_file}'))
            return

        # Clear existing data if requested
        if clear:
            count = AchievementType.objects.all().count()
            AchievementType.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Deleted {count} existing achievement types'))

        # RMIB category mapping
        rmib_mapping = {
            'SCI': 'scientific',
            'COMP': 'computational',
            'OUT': 'outdoor',
            'MECH': 'mechanical',
            'PERS': 'personal_contact',
            'AESTH': 'aesthetic',
            'LIT': 'literary',
            'MUS': 'musical',
            'SS': 'social_service',
            'CLER': 'clerical',
            'PRAC': 'practical',
            'MED': 'medical'
        }

        # Category type mapping
        category_mapping = {
            'Akademik': 'academic',
            'Non-Akademik': 'non_academic'
        }

        created_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(self.style.SUCCESS(f'\n📂 Reading file: {csv_file}\n'))

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Skip empty rows
                        if not row.get('Bidang Prestasi') or row.get('Bidang Prestasi').strip() == '':
                            continue

                        # Extract data
                        name = row['Bidang Prestasi'].strip()
                        category_raw = row['Kategori Utama'].strip()
                        description = row.get('Keterangan', '').strip()
                        
                        # Extract RMIB categories
                        rmib_primary_raw = row.get('Kategori RMIB Primer', '').strip()
                        rmib_secondary_raw = row.get('Kategori RMIB Sekunder', '').strip()

                        # Parse RMIB primary
                        rmib_primary = None
                        if rmib_primary_raw and rmib_primary_raw != '-':
                            for key, value in rmib_mapping.items():
                                if key in rmib_primary_raw:
                                    rmib_primary = value
                                    break

                        # Parse RMIB secondary - DEFAULT TO NULL IF EMPTY
                        rmib_secondary = None
                        if rmib_secondary_raw and rmib_secondary_raw != '-':
                            for key, value in rmib_mapping.items():
                                if key in rmib_secondary_raw:
                                    rmib_secondary = value
                                    break

                        # Get category type
                        category = category_mapping.get(category_raw, 'other')

                        # Check if already exists
                        if AchievementType.objects.filter(name=name).exists():
                            skipped_count += 1
                            continue

                        # Create achievement type
                        achievement = AchievementType.objects.create(
                            name=name,
                            category=category,
                            description=description or f'{name} - {category_raw}',
                            rmib_primary=rmib_primary,
                            rmib_secondary=rmib_secondary  # Can be None
                        )

                        created_count += 1
                        primary_display = rmib_primary.upper() if rmib_primary else 'N/A'
                        secondary_display = rmib_secondary.upper() if rmib_secondary else '-'
                        self.stdout.write(self.style.SUCCESS(
                            f'✅ {created_count:2d}. {name:30s} | P: {primary_display:10s} | S: {secondary_display}'
                        ))

                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'❌ Row {row_num}: {str(e)}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            return

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'⚠️  Skipped (already exists): {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'❌ Errors: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total in DB: {AchievementType.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

import imp
import os
import sys

# ✅ SET ENVIRONMENT VARIABLES SEBELUM IMPORT DJANGO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psikologimts1.settings')
os.environ['ENVIRONMENT'] = 'production'      # ← TAMBAH INI
os.environ['DEBUG'] = 'False'                  # ← TAMBAH INI
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'  # Atau MySQL sesuai setup

# Baru setelah ini import Django
sys.path.insert(0, os.path.dirname(__file__))

wsgi = imp.load_source('wsgi', 'psikologimts1/wsgi.py')
application = wsgi.application

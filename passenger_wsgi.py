import imp
import os
import sys

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables SEBELUM import Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psikologimts1.settings')

# Import WSGI application
import django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import imp
import os
import sys

# ✅ SET ENVIRONMENT UNTUK PRODUCTION
os.environ['DJANGO_SETTINGS_MODULE'] = 'psikologimts1.settings'
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEBUG'] = 'False'

# Add path
sys.path.insert(0, os.path.dirname(__file__))

# Load Django
wsgi = imp.load_source('wsgi', 'psikologimts1/wsgi.py')
application = wsgi.application

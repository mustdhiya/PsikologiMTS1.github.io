import sys, os

# PyMySQL
import pymysql
pymysql.install_as_MySQLdb()

# Virtual environment
sys.path.insert(0, '/home/prep8924/virtualenv/python/PsikologiMTS1.github.io/3.11/lib/python3.11/site-packages')

# Django project
sys.path.insert(0, '/home/prep8924/python/PsikologiMTS1.github.io')

# Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'psikologimts1.settings'

# WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

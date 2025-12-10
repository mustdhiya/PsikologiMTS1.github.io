import os
import sys
import pymysql

pymysql.install_as_MySQLdb()

# path ke env
sys.path.insert(0, '/home/prep8924/virtualenv/public_html/psikologi/3.12/lib/python3.12/site-packages')

# path ke folder repo django (manage.py)
sys.path.insert(0, '/home/prep8924/public_html/psikologi/PsikologiMTS1.github.io')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psikologimts1.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

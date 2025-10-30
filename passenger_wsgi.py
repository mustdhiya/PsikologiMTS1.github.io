import os
import sys

# Ganti 'username_anda' dengan username cPanel Anda
sys.path.insert(0, '/home/prep8924/psikologimts1')

os.environ['DJANGO_SETTINGS_MODULE'] = 'psikologimts1.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

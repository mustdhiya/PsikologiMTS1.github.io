import imp
import os
import sys
sys.path.insert(0, "/home/prep8924/python/PsikologiMTS1.github.io/psikologimts1")

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'psikologimts1.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


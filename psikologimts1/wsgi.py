"""
WSGI config for psikologimts1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import sys
import os

# Add Django project to path
sys.path.insert(0, '/home/prep8924/apps/PsikologiMTS1hub.io')

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psikologimts1.settings')
os.environ['DEBUG'] = 'True'

# Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

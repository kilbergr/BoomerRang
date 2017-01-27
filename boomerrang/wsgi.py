"""
WSGI config for boomerrang project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys 

from django.core.wsgi import get_wsgi_application


DJANGO_PATH =  os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys.path.append(DJANGO_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boomerrang.settings")

application = get_wsgi_application()

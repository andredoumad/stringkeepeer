"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stringkeeper.settings")

import django
import channels
from channels.routing import get_default_application

django.setup()
application = get_default_application()
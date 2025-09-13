"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Set the default Django settings module for the 'wsgi' application.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# This application object is used by any WSGI server configured to use this file.
application = get_wsgi_application()

# Use WhiteNoise to serve static files in production
application = WhiteNoise(
    application,
    root=os.path.join(BASE_DIR, 'staticfiles'),
    prefix='/static/',
)

# Add media files to WhiteNoise (if needed)
application.add_files(
    os.path.join(BASE_DIR, 'media'),
    prefix='/media/',
)

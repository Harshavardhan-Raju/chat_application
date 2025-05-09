"""
WSGI config for chat project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import sys
import os

# Add your project directory
sys.path.append('/home/harshavardhanraju/chat_application')

# Set environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'chat.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


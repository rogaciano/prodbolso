"""
Settings package initialization.
This file determines which settings file to use based on the environment.
"""
import os

# Default to development settings
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *

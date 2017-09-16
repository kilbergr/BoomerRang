"""Production settings and globals."""
from boomerrang.settings.base import *  # noqa
from postgresify import postgresify

DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com']

# Enables versioned and compressed static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DATABASES = postgresify()

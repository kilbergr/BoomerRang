"""Production settings and globals."""

from postgresify import postgresify

from boomerrang.settings.base import *  # noqa


DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com']

DATABASES = postgresify()

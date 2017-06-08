from config.settings import *

AUTH_PASSWORD_VALIDATORS = []

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += ['corsheaders']

MIDDLEWARE_CLASSES += ['corsheaders.middleware.CorsMiddleware']

CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:8081'
)

CORS_ALLOW_METHODS = (
    'GET',
)

# DEBUG = False
# ALLOWED_HOSTS = ['*']

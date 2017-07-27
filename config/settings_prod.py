from config.settings import *

try:
    from .secrets_prod import SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, EMAIL_HOST_PASSWORD
except ImportError:
    raise Exception('You need to update secrets_prod.py with your own values')

DEBUG = False
ALLOWED_HOSTS = ['linkage.fr']
USE_X_FORWARDED_HOST = True

SECRET_KEY = 'to_be_changed_in_to_a_random_var_on_disk'

INSTALLED_APPS += ['raven.contrib.django.raven_compat']
RAVEN_CONFIG = {
    'dsn': 'https://7ac6001f054841b4ac1a20b81e304936:856b334666e74846b49118f3a924d184@sentry.io/142091',
    'release': COMMIT_HASH,
}


EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = 'no-reply@linkage.fr'
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@linkage.fr'
SERVER_EMAIL = 'no-reply@linkage.fr'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '620338696601-94u7gvh4avrlocro69mq73oudr3n5ar5.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}
SOCIAL_AUTH_GOOGLE_OAUTH2_REQUEST_TOKEN_EXTRA_ARGUMENTS = {'access_type': 'offline'}

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_GOOGLE_GMAIL_KEY = '620338696601-94u7gvh4avrlocro69mq73oudr3n5ar5.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_GMAIL_SECRET = SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
SOCIAL_AUTH_GOOGLE_GMAIL_AUTH_EXTRA_ARGUMENTS = {'access_type': 'offline'}
SOCIAL_AUTH_GOOGLE_GMAIL_REQUEST_TOKEN_EXTRA_ARGUMENTS = {'access_type': 'offline'}
SOCIAL_AUTH_GOOGLE_GMAIL_SCOPE = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

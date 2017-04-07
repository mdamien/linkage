from config.settings import *

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
EMAIL_HOST_PASSWORD = 'no_reply_linkage_fr_password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@linkage.fr'
SERVER_EMAIL = 'no-reply@linkage.fr'

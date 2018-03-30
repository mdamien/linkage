from config.settings_dev import *

"""
DEBUG = False
ALLOWED_HOSTS = ['*']
"""

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ('admin_gitlog', 'simple_admin_upload', )]

LINKAGE_ENTERPRISE = True

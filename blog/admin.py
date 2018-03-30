from django.contrib import admin
from django.apps import apps
from django.conf import settings

# auto-register all models
app = apps.get_app_config('blog')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

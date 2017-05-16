from django.contrib import admin
from django.apps import apps

from core.models import Graph

admin.site.site_header = 'Linkage'

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'public')

    def view_on_site(self, obj):
        return 'https://linkage.fr/' + obj.get_absolute_url()

# auto-register all models
app = apps.get_app_config('core')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

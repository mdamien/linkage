from django.contrib import admin
from django.apps import apps

from core.models import *

admin.site.site_header = 'Linkage'

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user', 'public')
    exclude = ('edges', 'tdm')

    def view_on_site(self, obj):
        return 'https://linkage.fr/' + obj.get_absolute_url()

@admin.register(ProcessingResult)
class ProcessingResultAdmin(admin.ModelAdmin):
    list_display = ('graph', 'param_clusters', 'param_topics', 'crit')
    exclude = ('topics_per_edges_mat', 'topics_mat')
        
# auto-register all models
app = apps.get_app_config('core')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

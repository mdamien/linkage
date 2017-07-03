from django.contrib import admin
from django.apps import apps

from simple_admin_upload.models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'size')

    def name(self, obj):
        return obj.content.name

    def size(self, obj):
        return obj.content.size

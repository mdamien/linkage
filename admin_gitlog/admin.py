import os

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.template.response import TemplateResponse
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group


class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        app_list = self.get_app_list(request)

        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
            gitlog=os.popen('git log -n 5').read(),
        )
        context.update(extra_context or {})

        request.current_app = self.name

        return TemplateResponse(request, 'admin/my_custom_index.html', context)

# TODO: figure out why these models don't auto-register to the new admin
admin.site = CustomAdminSite()
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
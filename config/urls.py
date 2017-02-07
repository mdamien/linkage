from django.conf.urls import url
from django.contrib import admin

import core

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', core.urls),
]

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core import views as core_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    url(r'', include('core.urls')),
    url(r'blog/', include('blog.urls')),
    url(r'^admin/', include('loginas.urls')),
    url(r'^404/', core_views.handler404),
    url(r'^500/', core_views.handler500),
    url(r'^403/', core_views.handler403),
]

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'

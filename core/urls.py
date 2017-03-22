from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^jobs/add/$', views.addjob),
    url(r'^jobs/$', views.jobs),
    url(r'^$', views.landing),
    url(r'^result/(?P<pk>\d+)/$', views.result, name='result'),
    url(r'^result/(?P<pk>\d+)/data/$', views.api_result),
    url(r'^result/(?P<pk>\d+)/details/$', views.details),
    url(r'^result/(?P<pk>\d+)/cluster_it/$', views.api_cluster),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),
    url(r'^about/terms/$', views.terms),
]

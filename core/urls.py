from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^result/(?P<pk>\d+)/$', views.result, name='result'),
    url(r'^result/(?P<pk>\d+)/data/$', views.api_result),
]

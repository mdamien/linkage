from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/manifest.json$', views.manifest),
    url(r'^(?P<pk>\d+)/data/labels.json$', views.labels),
    url(r'^(?P<pk>\d+)/data/links.bin$', views.links),
    url(r'^(?P<pk>\d+)/data/meta.json$', views.meta),
    url(r'^(?P<pk>\d+)/data/positions.bin$', views.positions),
]

from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse

class Graph(models.Model):
    name = models.CharField(max_length=100)

    # csv of [origin, dest, text]
    links = models.TextField(blank=True, default='')

    # TODO: output data
    # clusters, groups, matrices,...

    # TODO: user

    imported_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return resolve('core.views.result', pk=self.pk)

    def __str__(self):
        return '"{}" {}'.format(self.name, naturaltime(self.imported_at))

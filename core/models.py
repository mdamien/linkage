from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse

class Graph(models.Model):
    name = models.CharField(max_length=100)

    # csv of [origin, dest, text]
    links = models.TextField(blank=True, default='')

    # TODO: user

    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('result', kwargs={'pk': self.pk})

    def __str__(self):
        return '"{}" {}'.format(self.name, naturaltime(self.created_at))


class ProcessingResult(models.Model):
    graph = models.ForeignKey(Graph)
    log = models.TextField(blank=True, default='')
    progress = models.FloatField(default=0)

    # csv of [node,cluster]
    clusters = models.TextField(blank=True, default='')
    # csv of [node1,node2,topic]
    topics = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({})'.format(naturaltime(self.created_at), self.graph)

from django.db import models

class ProcessedGraph(models.Model):
    name = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)

    # TODO: data
    # nodes, links, clusters, groups, matrices,...

    # TODO: user

    def __str__(self):
        return '"{}"" at {}'.format(name, time)

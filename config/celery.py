import os
from celery import Celery, task

from channels import Group


import graph_processing

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('linkage')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks()

@task()
def process_graph(pk, n_clusters, n_topics):
    print('Processing graph %d' % pk)
    import csv, io
    from core.models import Graph, ProcessingResult
    graph = Graph.objects.get(pk=pk)
    result = ProcessingResult(graph=graph)
    result.save()

    clusters_mat, topics_mat = graph_processing.process2(graph.edges, graph.tdm, n_clusters, n_topics)

    result.progress = 1;
    result.clusters_mat = clusters_mat
    result.topics_mat = topics_mat
    result.save()

    Group("result-%s" % pk).send({
        'text': '%d - DONE' % pk
    })

    return None

import os
from celery import Celery, task

from channels import Group


import graph_processing

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

app = Celery('linkage')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks()

@task()
def process_graph(result_pk, ws_delay=0):
    print('Processing result %d' % result_pk)

    import csv, io
    from core.models import Graph, ProcessingResult

    result = ProcessingResult.objects.get(pk=result_pk)
    graph = result.graph

    print('Processing graph %d' % graph.pk)

    print('CLUSTERS', result.param_clusters)
    print('TOPICS', result.param_topics)

    clusters_mat, topics_mat, log = graph_processing.process(
        graph.edges, graph.tdm,
        result.param_clusters, result.param_topics,
        result.pk)

    result.progress = 1;
    result.log = log
    result.clusters_mat = clusters_mat
    result.topics_mat = topics_mat
    result.save()

    import time
    time.sleep(ws_delay)

    Group("result-%d" % graph.pk).send({
        'text': '%d - DONE' % graph.pk
    })

    return None

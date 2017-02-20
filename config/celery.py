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

    links = list(csv.reader(io.StringIO(graph.links)))

    clusters, topics, topics_terms = graph_processing.process(links, n_clusters, n_topics)

    result.progress = 1;
    result.clusters = clusters
    result.topics = topics
    result.topics_terms = topics_terms
    result.save()

    Group("result-%s" % pk).send({
        'text': '%d - DONE' % pk
    })

    return None

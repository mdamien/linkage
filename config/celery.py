import os
from celery import Celery, task
from channels import Group

import graph_processing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

app = Celery('linkage')
app.config_from_object('django.conf:settings')

@task()
def process_graph(graph_pk, result_pk=None, ws_delay=0):
    """
    if a result is specified, we don't do do range clustering
    """

    print('Processing graph {} with result={}'.format(graph_pk, result_pk))

    import csv, io, random
    from core.models import Graph, ProcessingResult

    param_clusters = 2
    param_topics = 2
    param_max_clusters = 5
    param_max_topics = 5
    if result_pk is not None:
        result = ProcessingResult.objects.get(pk=result_pk)
        print('requested clusters', result.param_clusters)
        print('requested topics', result.param_topics)
        param_clusters = result.param_clusters
        param_topics = result.param_topics
        param_max_topics = None
        param_max_clusters = None

    graph = Graph.objects.get(pk=graph_pk)

    results, log = graph_processing.process(
        graph.edges, graph.tdm,
        param_clusters, param_topics,
        result_pk if result_pk else random.randint(0, 10000),
        param_max_clusters, param_max_topics)

    for result in results:
        try:
            db_result = ProcessingResult.objects.get(
                pk=result_pk,
                param_clusters=result['n_clusters'],
                param_topics=result['n_topics'],
            )
        except:
            result = ProcessingResult(
                graph=graph,
                param_clusters=result['n_clusters'],
                param_topics=result['n_topics']
            )
        result.progress = 1;
        result.log = log # TODO: review db model to store this only once
        result.clusters_mat = result['clusters']
        result.topics_mat = result['topics']
        result.save()

    import time
    time.sleep(ws_delay)

    Group("result-%d" % graph.pk).send({
        'text': '%d - DONE' % graph.pk
    })

    return None

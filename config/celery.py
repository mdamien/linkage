import os
from celery import Celery, task
from channels import Group

import graph_processing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

app = Celery('linkage')
app.config_from_object('django.conf:settings')

@task()
def process_graph(graph_pk, result_pk=None, ws_delay=0):
    print('Processing graph {}'.format(graph_pk))

    import csv, io, random, time
    from core.models import Graph, ProcessingResult

    t = time.process_time()

    graph = Graph.objects.get(pk=graph_pk)

    param_clusters = graph.job_param_clusters
    param_topics = graph.job_param_topics
    param_max_clusters = graph.job_param_clusters_max
    param_max_topics = graph.job_param_topics_max


    Group("jobs-%d" % graph.user.pk).send({
        'text': '%d - STARTED' % graph.pk
    })

    results, log = graph_processing.process(
        graph.edges, graph.tdm,
        param_clusters, param_topics,
        result_pk if result_pk else random.randint(0, 10000),
        param_max_clusters, param_max_topics)

    graph.job_log = log
    graph.job_time = time.process_time() - t
    graph.job_progress = 1;
    graph.save()
    
    for group, result in results.items():
        db_result = ProcessingResult(
            graph=graph,
            param_clusters=result['n_clusters'],
            param_topics=result['n_topics']
        )
        db_result.clusters_mat = result['clusters']
        db_result.topics_mat = result['topics']
        db_result.topics_per_edges_mat = result['topics_per_edges']
        db_result.rho_mat = result['rho_mat']
        db_result.pi_mat = result['pi_mat']
        db_result.theta_qr_mat = result['theta_qr_mat']
        db_result.crit = result['crit']
        db_result.save()

    time.sleep(ws_delay)

    Group("jobs-%d" % graph.user.pk).send({
        'text': '%d - DONE' % graph.pk
    })

    return None

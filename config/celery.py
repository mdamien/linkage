import os
from celery import Celery, task
from channels import Group

import graph_processing
from graph_processing.layout import spacialize

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

app = Celery('linkage')
app.config_from_object('django.conf:settings')

@task()
def process_graph(graph_pk, result_pk=None, ws_delay=0):
    print('Processing graph {}'.format(graph_pk))

    import csv, io, random, time
    from core.models import Graph, ProcessingResult

    t = time.time()

    graph = Graph.objects.get(pk=graph_pk)

    param_clusters = graph.job_param_clusters
    param_topics = graph.job_param_topics
    param_max_clusters = graph.job_param_clusters_max
    param_max_topics = graph.job_param_topics_max


    Group("jobs-%d" % graph.user.pk).send({
        'text': '%d - STARTED' % graph.pk
    })

    def update(log, kq_done, msg):
        graph.job_log = log
        kq_todo = (
            (param_max_clusters - param_clusters + 1)
                * (param_max_topics - param_topics + 1)
        )
        graph.job_progress = kq_done / kq_todo
        graph.save()
        Group("jobs-%d" % graph.user.pk).send({
            'text': '%d - UPDATE' % graph.pk
        })

    results, log = graph_processing.process(
        graph.edges, graph.tdm,
        param_clusters, param_topics,
        result_pk if result_pk else random.randint(0, 10000),
        param_max_clusters, param_max_topics,
        update=update)

    graph.job_log = log
    graph.job_time = (time.time() - t) / 100
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


@task()
def retrieve_graph_data(graph_pk, method, **params):
    from core import third_party_import
    links = getattr(third_party_import, method)(params['q'], params['limit'])
    import_graph_data(graph_pk, links, ignore_self_loop=params.get('ignore_self_loop', True))


@task()
def import_graph_data(graph_pk, csv_content, ignore_self_loop=True):
    # print('received csv_content:', csv_content[:100])
    from core import models
    graph = models.Graph.objects.get(pk=graph_pk)
    data = models.graph_data_from_links(csv_content, ignore_self_loop=ignore_self_loop)
    for key in data:
        setattr(graph, key, data[key])
    graph.save()
    if len(graph.labels.strip()) < 2:
        graph.job_error_log = 'No data to process for this graph'
        graph.job_progress = 1.0
        graph.save()
        Group("jobs-%d" % graph.user.pk).send({
            'text': '%d - ERROR' % graph.pk
        })
        return
    spacialize_graph.delay(graph.pk)
    process_graph(graph.pk, ws_delay=2)


@task()
def spacialize_graph(graph_pk):
    from core import models
    graph = models.Graph.objects.get(pk=graph_pk)

    print('spacialize', graph.pk)
    spacialize(graph.edges, graph.labels, graph.pk)
    print('spacialize DONE', graph.pk)


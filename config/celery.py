import os, time, csv, io, random
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

    from core.models import Graph, ProcessingResult

    t = time.time()

    graph = Graph.objects.get(pk=graph_pk)

    param_clusters = graph.job_param_clusters
    param_topics = graph.job_param_topics
    param_max_clusters = graph.job_param_clusters_max
    param_max_topics = graph.job_param_topics_max

    n_repeat = 4

    Group("jobs-%d" % graph.user.pk).send({
        'text': '%d - STARTED' % graph.pk
    })

    def update(log, kq_done, msg):
        graph.job_log = log
        kq_todo = (
            (param_max_clusters - param_clusters + 1)
                * (param_max_topics - param_topics + 1)
        ) * n_repeat
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
        update=update, n_repeat=n_repeat)

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
    from core import third_party_import, models

    ignore_self_loop = params.pop('ignore_self_loop', True)
    filter_largest_subgraph = params.pop('filter_largest_subgraph', False)
    params.pop('directed', None)

    exception_triggered = None
    try:
        links = getattr(third_party_import, method)(**params)
    except Exception as e:
        exception_triggered = e
    if exception_triggered or len(links) < 2:
        graph = models.Graph.objects.get(pk=graph_pk)
        error = 'No results for this request'
        if 'hal_' in method:
            error = 'No HAL results for this request'
        if 'arxiv_' in method:
            error = 'No arXiv results for this request'
        if 'pubmed_' in method:
            error = 'No PubMed results for this request'
        if 'twitter_' in method or 'loklak_' in method:
            error = 'No Twitter results for this request'
        if exception_triggered:
            error = 'Error while importing'
        graph.job_error_log = error
        graph.job_progress = 1.0
        graph.save()
        time.sleep(1)
        Group("jobs-%d" % graph.user.pk).send({
            'text': '%d - ERROR' % graph.pk
        })
        if exception_triggered:
            raise exception_triggered
        return
    import_graph_data(graph_pk, links, filter_largest_subgraph=filter_largest_subgraph, ignore_self_loop=ignore_self_loop)

@task()
def save_csv(graph_pk, csv_content):
    from core import models
    graph = models.Graph.objects.get(pk=graph_pk)
    graph.original_csv = csv_content
    graph.save(update_fields=['original_csv'])
    print('CSV SAVED')


@task()
def import_graph_data(graph_pk, csv_content, filter_largest_subgraph=False, ignore_self_loop=True):
    # print('received csv_content:', csv_content[:100])
    from core import models
    graph = models.Graph.objects.get(pk=graph_pk)

    error = None
    try:
        data = models.graph_data_from_links(csv_content,
            filter_largest_subgraph=filter_largest_subgraph,
            ignore_self_loop=False, # TODO: remove self loop concept from linkage
            directed=graph.directed)
        for key in data:
            setattr(graph, key, data[key])
        graph.save()
    except Exception as e:
        graph.job_error_log = 'Error while importing'
        graph.job_progress = 1.0
        graph.save()
        time.sleep(1)
        Group("jobs-%d" % graph.user.pk).send({
            'text': '%d - ERROR' % graph.pk
        })
        raise e

    if len(graph.labels.strip()) < 2:
        graph.job_error_log = 'No data to process for this graph'
        graph.job_progress = 1.0
        graph.save()
        time.sleep(1)
        Group("jobs-%d" % graph.user.pk).send({
            'text': '%d - ERROR' % graph.pk
        })
        return

    # TODO: re-enable spacialization
    # spacialize_graph.delay(graph.pk)
    # save_csv.delay(graph.pk, csv_content)
    process_graph.delay(graph.pk, ws_delay=2)


@task()
def spacialize_graph(graph_pk):
    from core import models
    graph = models.Graph.objects.get(pk=graph_pk)
    
    print('spacialize', graph.pk)
    spacialize(graph.edges, graph.labels, graph.pk)
    print('spacialize DONE', graph.pk)


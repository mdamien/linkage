import os
from celery import Celery, task

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

# TODO: move this back to core/ when autodiscover_tasks is working
@task()
def process_graph(pk, n_clusters, n_topics):
    print('Processing graph %d' % pk)

    import time, csv, random, io

    from core.models import Graph, ProcessingResult
    graph = Graph.objects.get(pk=pk)

    result = ProcessingResult(graph=graph)
    result.save()

    """
    for i in range(6):
        time.sleep(5)
        result.progress = i*2 / 10
        result.save()
    """

    links = list(csv.reader(io.StringIO(graph.links)))

    NB_OF_CLUSTERS = 3 if n_clusters == None else n_clusters
    all_clusters = ['%d_clusters_%d' % (pk, i) for i in range(NB_OF_CLUSTERS)]

    clusters = io.StringIO()
    writer = csv.writer(clusters)

    nodes = set()
    for link in links:
        if len(link) > 1:
            nodes.add(link[0])
            nodes.add(link[1])

    for node in nodes:
        writer.writerow([node, random.choice(all_clusters)])

    NB_OF_TOPICS = 3 if n_topics == None else n_topics

    topics = io.StringIO()
    writer = csv.writer(topics)
    for link in links:
        if len(link) > 1:
            row = [link[0], link[1]]
            for topic in range(NB_OF_TOPICS):
                row.append(str(random.random()))
            writer.writerow(row)

    result.progress = 1;
    result.clusters = clusters.getvalue()
    result.topics = topics.getvalue()
    result.save()

    return None

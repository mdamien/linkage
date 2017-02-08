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
def process_graph(pk):
    print('Processing graph %d' % pk)

    import time

    from core.models import Graph, ProcessingResult
    graph = Graph.objects.get(pk=pk)

    result = ProcessingResult(graph=graph)
    result.save()

    for i in range(6):
        time.sleep(5)
        result.progress = i*2 / 10
        result.save()

    result.clusters = '1,cluster1\n2,cluster2'
    result.topics = '1,2,topic1\n2,3,topic2'

    result.save()

    return None

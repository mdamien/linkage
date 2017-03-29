from django.core.management.base import BaseCommand, CommandError
from core import models

class Command(BaseCommand):
    help = 're-run on graph_id'

    def add_arguments(self, parser):
        parser.add_argument('graph_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for graph_id in options['graph_id']:
            print('graph:', graph_id)
            try:
                graph = models.Graph.objects.get(pk=graph_id)
            except models.Graph.DoesNotExist:
                raise CommandError('Graph "%s" does not exist' % graph_id)

            results = models.ProcessingResult.objects.filter(graph=graph)
            print('removing', len(results), 'results')
            results.delete()

            from config.celery import process_graph
            process_graph.delay(graph.pk)

            print('job launched')

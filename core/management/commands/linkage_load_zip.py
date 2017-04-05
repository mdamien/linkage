from django.core.management.base import BaseCommand, CommandError
from core import models

import os, csv

class Command(BaseCommand):
    help = 'load .zip export from pierre'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs=1, type=int)
        parser.add_argument('folder', nargs='+', type=str)

    def handle(self, *args, **options):
        for folder in options['folder']:
            print(folder)

            for file in os.listdir(folder):
                if 'cluster' in file:
                    clusters = open(os.path.join(folder, file)).read()
                if 'beta' in file:
                    beta = open(os.path.join(folder, file)).read()
                if 'rho' in file:
                    rho = open(os.path.join(folder, file)).read()
                if 'theta' in file:
                    theta_qr = open(os.path.join(folder, file)).read()
                if 'PI' in file:
                    pi = open(os.path.join(folder, file)).read()

            dictionnary = ' '.join([x[0] for x in csv.reader(open(os.path.join(folder, 'dic.csv'))) ])

            graph = models.Graph.objects.create(
                name=folder,
                job_param_clusters=0,
                job_param_topics=0,
                job_param_clusters_max=0,
                job_param_topics_max=0,
                job_progress=1,
                labels='a b',
                edges='0 0 1',
                dictionnary=dictionnary,
                tdm='0 0 1',
                user=models.User.objects.get(pk=options['user_id'][0]),
            )

            result = models.ProcessingResult.objects.create(
                graph=graph,
                clusters_mat=clusters,
                topics_mat=beta,
                topics_per_edges_mat='0 0 1',
                rho_mat=rho,
                pi_mat=pi,
                theta_qr_mat=theta_qr,
            )

            print('graph', graph)
            graph.save()
            print('result', result)
            result.save()

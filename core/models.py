from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse
from django.contrib.auth.models import User

class Graph(models.Model): # = Job
    name = models.CharField(max_length=100)

    # job stuff
    job_time = models.FloatField(default=0)
    job_log = models.TextField(blank=True, default='')
    job_progress = models.FloatField(default=0)
    job_param_clusters = models.IntegerField(default=2)
    job_param_topics = models.IntegerField(default=2)
    job_param_clusters_max = models.IntegerField(default=5)
    job_param_topics_max = models.IntegerField(default=5)

    # array of labels for each node
    labels = models.TextField(blank=True, default='')
    # sparse matrix as coord_ascii of edges ( = X )
    edges = models.TextField(blank=True, default='')
    # array of words for each term
    dictionnary = models.TextField(blank=True, default='')
    # term count per edge as raw_ascii ( = tdm )
    tdm = models.TextField(blank=True, default='')

    directed = models.BooleanField(default=True)
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('result', kwargs={'pk': self.pk})

    def __str__(self):
        return '"{}" {}'.format(self.name, naturaltime(self.created_at))


class ProcessingResult(models.Model):
    graph = models.ForeignKey(Graph)

    param_clusters = models.IntegerField(default=3)
    param_topics = models.IntegerField(default=3)

    clusters_mat = models.TextField(blank=True, default='')
    topics_mat = models.TextField(blank=True, default='')
    topics_per_edges_mat = models.TextField(blank=True, default='')
    crit = models.FloatField(null=True, blank=True, default=None)

    # clust %
    rho_mat = models.TextField(blank=True, default='')
    # clust to clust %
    pi_mat = models.TextField(blank=True, default='')
    # topics in clust => clust
    theta_qr_mat = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({}) K={}, Q={}'.format(naturaltime(self.created_at), self.graph.name,
            self.param_clusters, self.param_topics)

    def serialize(self):
        return {
            'clusters_mat': self.clusters_mat,
            'topics_mat': self.topics_mat,
            'topics_per_edges_mat': self.topics_per_edges_mat,
            'rho_mat': self.rho_mat,
            'pi_mat': self.pi_mat,
            'theta_qr_mat': self.theta_qr_mat,
            'crit': self.crit,
            'param_clusters': self.param_clusters,
            'param_topics': self.param_topics,
        }


def graph_data_from_links(links):
    import csv, random, io, sys, os
    import collections
    import time
    import string

    csv.field_size_limit(sys.maxsize) # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

    from nltk.tokenize import word_tokenize
    from nltk.stem.snowball import SnowballStemmer
    from nltk.corpus import stopwords

    stemmer = SnowballStemmer("english")
    stopwords = stopwords.words('english')
    punc_table = dict((ord(char), ' ') for char in string.punctuation)

    X = io.StringIO()
    X_writer = csv.writer(X, delimiter=' ')
    DTM = io.StringIO()
    DTM_writer = csv.writer(DTM, delimiter=' ')

    links = list(csv.reader(io.StringIO(links)))

    nodes = [] # labels
    terms = [] # dictionnary

    def node_to_i(node):
        try:
            return nodes.index(node)
        except ValueError:
            nodes.append(node)
            return len(nodes) - 1

    def term_to_i(term):
        try:
            return terms.index(term)
        except ValueError:
            terms.append(term)
            return len(terms) - 1

    edges = collections.OrderedDict()
    for link in links:
        if len(link) > 1:
            tokens = []
            text = link[2] if len(link) > 1 else ''
            for token in word_tokenize(text.translate(punc_table)): # remove punctuation and tokenize
                if token not in stopwords:
                    if len(token) > 2:
                        # remove numbers
                        try:
                            int(token)
                        except:
                            tokens.append(token)
            if len(tokens) > 0: # filter empty links
                start = node_to_i(link[0])
                end = node_to_i(link[1])
                if start != end:
                    edge_name = '%d,%d' % (start, end)
                    if edge_name not in edges:
                        edges[edge_name] = collections.Counter()
                    doc_terms = edges[edge_name]
                    for token in tokens:
                        doc_terms[stemmer.stem(token)] += 1

    def key_to_order_for_tdm(edge_name):
        start, end = [int(x) for x in edge_name.split(',')]
        return start + end*len(nodes)

    for curr_edge, edge_name in enumerate(sorted(edges.keys(), key=key_to_order_for_tdm)):
        start, end = edge_name.split(',')
        X_writer.writerow([start, end, 1])
        for token, count in edges[edge_name].items():
            DTM_writer.writerow([term_to_i(token), curr_edge, count])

    # add empty link to make the matrix square if it's not already a square
    start = end = len(nodes) - 1
    edge_name = '%d,%d' % (start, end)
    if edge_name not in edges:
        X_writer.writerow([start, end, 0])

    labels = io.StringIO()
    labels_writer = csv.writer(labels, delimiter=' ')
    labels_writer.writerow(nodes)

    dictionnary = io.StringIO()
    dictionnary_writer = csv.writer(dictionnary, delimiter=' ')
    dictionnary_writer.writerow(terms)

    return {
        'edges': X.getvalue(),
        'tdm': DTM.getvalue(),
        'labels': labels.getvalue(),
        'dictionnary': dictionnary.getvalue()
    }

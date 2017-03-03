from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.urls import reverse
from django.contrib.auth.models import User

class Graph(models.Model):
    name = models.CharField(max_length=100)

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
    log = models.TextField(blank=True, default='')
    progress = models.FloatField(default=0)

    param_clusters = models.IntegerField(default=3)
    param_topics = models.IntegerField(default=3)

    clusters_mat = models.TextField(blank=True, default='')
    topics_mat = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({})'.format(naturaltime(self.created_at), self.graph)



def graph_data_from_links(links):
    import csv, random, io, sys, os
    import collections
    import time

    csv.field_size_limit(sys.maxsize) # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

    from nltk.tokenize import word_tokenize
    from nltk.stem.snowball import SnowballStemmer
    from nltk.corpus import stopwords


    stemmer = SnowballStemmer("english")
    stopwords = stopwords.words('english')

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

    edges = set()
    curr_edge = 0
    for link in links:
        if len(link) > 1:
            start = node_to_i(link[0])
            end = node_to_i(link[1])
            edge_name = '%d,%d' % (start, end)
            if edge_name in edges:
                continue # TODO: DO NOT IGNORE DUPLICATE LINKS
            edges.add(edge_name)
            X_writer.writerow([start, end, 1])
            doc_terms = collections.Counter()
            for token in word_tokenize(link[2]):
                if token not in stopwords:
                    doc_terms[stemmer.stem(token)] += 1
            for token, count in doc_terms.items():
                DTM_writer.writerow([term_to_i(token), curr_edge, count])
            curr_edge += 1

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
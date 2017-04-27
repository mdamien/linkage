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
    job_param_clusters_max = models.IntegerField(default=10)
    job_param_topics_max = models.IntegerField(default=10)
    job_error_log = models.TextField(blank=True, default='')

    # array of labels for each node
    labels = models.TextField(blank=True, default='')
    # sparse matrix as coord_ascii of edges ( = X )
    edges = models.TextField(blank=True, default='')
    # array of words for each term
    dictionnary = models.TextField(blank=True, default='')
    # term count per edge as raw_ascii ( = tdm )
    tdm = models.TextField(blank=True, default='')

    cluster_to_cluster_cutoff = models.FloatField(default=0.002)

    magic_too_big_to_display_X = models.BooleanField(default=False)
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


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    org_type = models.CharField(max_length=50)

    def __str__(self):
        return '{}: {}'.format(self.user, self.org_type)


def graph_data_from_links(links, ignore_self_loop=True):
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
    stemm_to_lemm = {}

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
                if not ignore_self_loop or start != end:
                    edge_name = '%d,%d' % (start, end)
                    if edge_name not in edges:
                        edges[edge_name] = collections.Counter()
                    doc_terms = edges[edge_name]
                    for token in tokens:
                        stemm = stemmer.stem(token)
                        token = token.lower()
                        if stemm in stemm_to_lemm:
                            lemm = stemm_to_lemm[stemm]
                        else:
                            stemm_to_lemm[stemm] = token.lower()
                            lemm = token
                        doc_terms[lemm] += 1

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


def export_to_zip(graph, results):
    import csv, random, io, sys, os, zipfile

    zip_out = io.BytesIO()
    z = zipfile.ZipFile(zip_out, 'w')

    # edges.csv
    output = io.StringIO()
    writer = csv.writer(output)
    labels = list(csv.reader([graph.labels], delimiter=' '))[0]
    dictionnary = list(csv.reader([graph.dictionnary], delimiter=' '))[0]
    for line in csv.reader(graph.edges.split('\n'), delimiter=' '):
        if len(line) == 3:
            source, target, val = line
            if val == '0':
                continue
            writer.writerow([labels[int(source)], labels[int(target)]])
    edges_csv = output.getvalue()
    z.writestr('edges.csv', output.getvalue())
    z.writestr('raw/X.sp_mat', graph.edges)
    z.writestr('raw/labels', graph.labels)
    z.writestr('raw/tdm.sp_mat', graph.tdm)
    z.writestr('raw/dictionnary', graph.dictionnary)

    # clusters
    for i, result in enumerate(results):
        prefix = 'k%d_q%d/' % (result.param_topics, result.param_clusters)
        
        # clusters.csv
        output = io.StringIO()
        writer = csv.writer(output)
        clusters = list(csv.reader([result.clusters_mat], delimiter=' '))[0]
        clusters = [int(c) for c in clusters if c != '']
        clusters_labeleds = [None] * (max(clusters)+1)
        c = 0
        for cluster in clusters:
            if cluster != '':
                if clusters_labeleds[cluster] is None:
                    clusters_labeleds[cluster] = []
                clusters_labeleds[cluster].append(labels[c])
                c += 1
        for row in clusters_labeleds:
            if row is None:
                row = []
            writer.writerow(row)
        z.writestr(prefix + 'clusters.csv', output.getvalue())

        # topics.csv
        output = io.StringIO()
        writer = csv.writer(output)
        for topic in csv.reader(result.topics_mat.split('\n'), delimiter=' '):
            c = 0
            words = []
            for word_perc in topic:
                if word_perc:
                    words.append((dictionnary[c], float(word_perc)))
                    c += 1
            words = sorted(words, key=lambda x: -x[1])
            row = []
            for w, p in words:
                row.append(w)
                row.append(p)
            writer.writerow(row)
        z.writestr(prefix + 'topics.csv', output.getvalue())

        z.writestr(prefix + 'raw/clusters', result.clusters_mat)
        z.writestr(prefix + 'raw/topics', result.topics_mat)
        z.writestr(prefix + 'raw/topics_per_edges', result.topics_per_edges_mat)
        z.writestr(prefix + 'raw/rho', result.rho_mat)
        z.writestr(prefix + 'raw/PI', result.pi_mat)
        z.writestr(prefix + 'raw/thetaQR', result.theta_qr_mat)
        z.writestr(prefix + 'raw/crit', str(result.crit))

    z.close()
    return zip_out.getvalue()

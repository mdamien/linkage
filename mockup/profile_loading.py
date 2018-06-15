import random, string

def graph_data_from_links(links, filter_largest_subgraph=False, ignore_self_loop=True, directed=False):
    print('start graph data')
    import csv, random, io, sys, os
    import collections
    import time
    import string
    import Stemmer

    csv.field_size_limit(sys.maxsize) # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

    import nltk.tokenize
    from nltk.corpus import stopwords

    stemmer = Stemmer.Stemmer('english')
    stopwords = set(stopwords.words('english')).union(set(stopwords.words('french')))
    punc_table = dict((ord(char), ' ') for char in string.punctuation)

    def tokenize(string):
        string = string.translate(punc_table) # remove punctuation
        for begin, end in nltk.tokenize.WhitespaceTokenizer().span_tokenize(string):
            word = string[begin:end]
            if not word.isdigit() and word not in stopwords:
                yield word

    X = io.StringIO()
    X_writer = csv.writer(X, delimiter=' ')
    DTM = io.StringIO()
    DTM_writer = csv.writer(DTM, delimiter=' ')

    links = list(csv.reader(io.StringIO(links)))

    print('links loaded')

    if filter_largest_subgraph:
        # amazingly complex algorithm to find the subgraph and filter the links :)
        groups = {}
        groups_sizes = []
        g = 0
        for link in links:
            if len(link) > 1:
                source, target = link[0], link[1]
                if source not in groups and target in groups:
                    groups[source] = groups[target]
                    groups_sizes[groups[target]] += 1
                elif source in groups and target not in groups:
                    groups[target] = groups[source]
                    groups_sizes[groups[source]] += 1
                elif source not in groups and target not in groups:
                    groups[target], groups[source] = g, g
                    groups_sizes.append(0)
                    groups_sizes[g] += 2
                    g += 1
                elif groups[target] != groups[source]:
                    if groups_sizes[groups[target]] > groups_sizes[groups[source]]:
                        for node, group in groups.items():
                            if group == groups[source]:
                                groups[node] = groups[target]
                    else:
                        for node, group in groups.items():
                            if group == groups[target]:
                                groups[node] = groups[source]
        best_group = groups_sizes.index(max(groups_sizes))

        links = [link for link in links if len(link) > 1 and groups[link[0]] == best_group]

        print('filtered largest subgraph')

    if not directed:
        # another amazing algo to symmetrize the links in case of undirected graphs
        new_links = []
        for link in links:
            new_links.append(link)
            new_links.append([link[1], link[0]] + link[2:])
        links = new_links

        print('symmetry forced')


    nodes_i = {}  # fast lookup of index
    terms_i = {}  # fast lookup of index
    nodes = [] # labels
    terms = [] # dictionnary
    stemm_to_lemm = {}

    def node_to_i(node):
        if node in nodes_i:
            return nodes_i[node]
        nodes.append(node)
        i = len(nodes) - 1
        nodes_i[node] = i
        return i

    def term_to_i(term):
        if term in terms_i:
            return terms_i[term]
        terms.append(term)
        i = len(terms) - 1
        terms_i[term] = i
        return i

    print('start making edges', len(links))

    edges = collections.OrderedDict()
    for link in links:
        if len(link) > 1:

            # tokenization
            tokens = []
            text = link[2] if len(link) > 1 else ''
            tokens = list(tokenize(text))

            # stemming
            if len(tokens) > 0: # filter empty links
                start = node_to_i(link[0])
                end = node_to_i(link[1])
                if not ignore_self_loop or start != end:
                    edge_name = '%d,%d' % (start, end)
                    if edge_name not in edges:
                        edges[edge_name] = collections.Counter()
                    doc_terms = edges[edge_name]
                    for token, stemm in zip(tokens, stemmer.stemWords(tokens)):
                        token = token.lower()
                        if stemm in stemm_to_lemm:
                            lemm = stemm_to_lemm[stemm]
                        else:
                            stemm_to_lemm[stemm] = token.lower()
                            lemm = token
                        doc_terms[lemm] += 1

    print('edges made')

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

    print('data done')

    return {
        'edges': X.getvalue(),
        'tdm': DTM.getvalue(),
        'labels': labels.getvalue(),
        'dictionnary': dictionnary.getvalue()
    }


import sys
links = open(sys.argv[1]).read()
graph_data_from_links(links, directed=True)

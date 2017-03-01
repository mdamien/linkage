import csv, random, io, sys, os
import collections
import time

csv.field_size_limit(sys.maxsize) # http://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


stemmer = SnowballStemmer("english")
stopwords = stopwords.words('english')

def process(links, n_clusters, n_topics):
    k = random.randint(1, 100)

    NB_OF_CLUSTERS = 3 if n_clusters == None else n_clusters
    all_clusters = ['%d_clusters_%d' % (k, i) for i in range(NB_OF_CLUSTERS)]

    clusters = io.StringIO()
    writer = csv.writer(clusters)

    terms = collections.Counter()

    nodes = set()
    for link in links:
        if len(link) > 1:
            nodes.add(link[0])
            nodes.add(link[1])
            for token in word_tokenize(link[2]):
                if token not in stopwords:
                    terms[stemmer.stem(token)] += 1

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

    topics_terms = io.StringIO()
    writer = csv.writer(topics_terms)
    for topic in range(NB_OF_TOPICS):
        assigned_terms = []
        items = list(terms.most_common())
        N = random.randint(1, len(items))
        for i in range(N):
            item = random.choice(items)
            assigned_terms.append(item[0])
            assigned_terms.append(item[1] + random.random())
        writer.writerow(assigned_terms)

    return clusters.getvalue(), topics.getvalue(), topics_terms.getvalue()


def export(links, output_dir=''):
    open()
    X = io.StringIO()
    X_writer = csv.writer(open(output_dir + 'X.sp_mat', 'w'), delimiter=' ')
    DTM = io.StringIO()
    DTM_writer = csv.writer(open(output_dir + 'tdm.sp_mat', 'w'), delimiter=' ')


def process2(X, tdm, n_clusters, n_topics):
    NB_OF_TOPICS = 3 if n_topics == None else n_topics
    NB_OF_CLUSTERS = 3 if n_clusters == None else n_clusters

    linkage_dir = '../repos/linkage-cpp/'

    os.system('cd %s;rm in/*' % (linkage_dir,))
    os.system('cd %s;rm out/*' % (linkage_dir,))

    open(linkage_dir + 'in/X.sp_mat', 'w').write(X)
    open(linkage_dir + 'in/tdm.sp_mat', 'w').write(tdm)

    os.system('cd %s;./build/linkage %d %d 10 0 1' % (linkage_dir, NB_OF_CLUSTERS, NB_OF_TOPICS))

    clusters = open(linkage_dir + 'out/sp_clust.write.mat').read()

    print('clusters:', len(clusters), clusters)

    topics = open(linkage_dir + 'out/meta.write.mat').read()
    return clusters, topics

if __name__ == '__main__':
    links = [
        ['a', 'b', 'AAAA AA A'],
        ['b', 'c', 'AAAA AAAA AA A AAAA'],
        ['d', 'e', 'BBBB BBB BBB B'],
        ['e', 'a', 'BB BB BBBB B BB'],
        ['a', 'f', 'CC CC BB AA'],
        ['f', 'b', 'CC CC'],
    ]
    X = """0 1 1
1 2 1
2 3 1
4 5 1
1 3 1
5 0 1
1 5 1
5 5 0
"""
    tdm = """0 0 1
0 1 1
1 2 1
2 2 1
1 3 1
2 3 1
3 4 1
3 5 1
3 6 1
"""
    clusters, topics = process2(X, tdm, 3, 3)
    print(clusters)
    print(topics)
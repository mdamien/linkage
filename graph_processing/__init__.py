import csv, random, io
import collections

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
                    terms.update([stemmer.stem(token)])

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

if __name__ == '__main__':
    links = [
        ['a', 'b', 'result.clusters = clusters.getvalue()'],
        ['b', 'c', 'clusters.getvalue(), topics.getvalue()'],
        ['d', 'e', 'result.topics = topics.getvalue()'],
        ['e', 'a', 'result.progress = 1;'],
    ]
    clusters, topics, topics_terms, terms = process(links, 3, 3)
    print(clusters)
    print(topics)
    print(topics_terms)
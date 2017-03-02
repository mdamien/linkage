import os

def process(X, tdm, n_clusters, n_topics):
    NB_OF_TOPICS = 3 if n_topics == None else n_topics
    NB_OF_CLUSTERS = 3 if n_clusters == None else n_clusters

    linkage_dir = '../repos/linkage-cpp/'

    os.system('cd %s;rm in/*' % (linkage_dir,))
    os.system('cd %s;rm out/*' % (linkage_dir,))

    open(linkage_dir + 'in/X.sp_mat', 'w').write(X)
    open(linkage_dir + 'in/tdm.sp_mat', 'w').write(tdm)

    log = os.popen('cd %s;./build/linkage %d %d 10 0 1' % (linkage_dir, NB_OF_TOPICS, NB_OF_CLUSTERS)).read()
    print(log)

    clusters = open(linkage_dir + 'out/sp_clust.write.mat').read()

    print('clusters:', len(clusters), clusters)

    topics = open(linkage_dir + 'out/meta.write.mat').read()
    return clusters, topics, log

if __name__ == '__main__':
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
    clusters, topics, log = process(X, tdm, 2, 4)
    print(clusters)
    print(topics)
    print(log[-100:])
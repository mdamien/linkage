import os

def process(X, tdm, n_clusters, n_topics, id=0):
    linkage_dir = '../repos/linkage-cpp/'
    run_dir = '%sruns/%d/' % (linkage_dir, id)
    run_dir_for_linkage = 'runs/%d/' % id

    os.system('mkdir -p %s' % run_dir)
    os.system('cd %s;rm -rf in' % (run_dir,))
    os.system('cd %s;mkdir in' % (run_dir,))
    os.system('cd %s;rm -rf out' % (run_dir,))
    os.system('cd %s;mkdir out' % (run_dir,))

    open(run_dir + 'in/X.sp_mat', 'w').write(X)
    open(run_dir + 'in/tdm.sp_mat', 'w').write(tdm)

    log = os.popen('cd %s;./build/linkage %d %d 10 0 1 %s' % (
        linkage_dir, n_topics, n_clusters, run_dir_for_linkage)
    ).read()
    print(log)

    try:
        clusters = open(run_dir + 'out/sp_clust.write.mat').read()
    except FileNotFoundError:
        print('ERROR: NOT CLUSTERS')
        clusters = ''

    print('clusters:', len(clusters), clusters)

    try:
        topics = open(run_dir + 'out/meta.write.mat').read()
    except FileNotFoundError:
        print('ERROR: NOT TOPICS')
        topics = ''

    os.system('rm -rf %s' % (run_dir,))

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
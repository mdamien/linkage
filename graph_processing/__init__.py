import os, subprocess, time

def process(X, tdm, n_clusters, n_topics, id=0,
        n_clusters_max=None, n_topics_max=None,
        update=lambda log, kq_done, msg: print('kq_done', kq_done) and print(msg),
        n_repeat=3, max_inner_lda=10, max_outer_lda=10):
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

    n_topics_max = n_topics if n_topics_max is None else n_topics_max
    n_clusters_max = n_clusters if n_clusters_max is None else n_clusters_max

    log = ''
    
    cmd_cd = 'cd {link_dir};'.format(link_dir=linkage_dir) + 'export LD_LIBRARY_PATH="build/arma/";'
    cmd_base = ('./build/linkage ' \
            + '{Kmin} {Kmax} {Qmin} {Qmax} {n_repeat} 0 1 100 0.0001 {max_inner_lda} {max_outer_lda} {dir}').format(
                Kmin=n_topics,
                Kmax=n_topics_max,
                Qmin=n_clusters,
                Qmax=n_clusters_max,
                n_repeat=n_repeat,
                max_inner_lda=max_inner_lda,
                max_outer_lda=max_outer_lda,
                dir=run_dir_for_linkage)

    log += cmd_base + '\n'
    n_done = 0
    update(log, n_done, log)
    last_update = time.time()
    print(cmd_base)
    for line in os.popen(cmd_cd + cmd_base):
        # print(line.strip())
        log += line

        # signal: "[linkage-web-signal] - (K|Q) finished: " << K << ";" << Q << "" << endl
        if '[linkage-web-signal] - (K|Q|rep) finished' in line:
            n_done += 1
        
        diff = time.time() - last_update
        # if diff > 5 or '[linkage-web-signal] - (K|Q) finished' in line:
        if '[linkage-web-signal] - (K|Q|rep) finished' in line:
            update(log, n_done, line.strip())
            last_update = time.time()
    print('processing done')

    groups = {}
    for q in range(n_clusters, n_clusters_max + 1):
        for k in range(n_topics, n_topics_max + 1):
            groups['%d,%d' % (k, q)] = {}

    if len(groups.keys()) == 0:
        print('ERROR: NO (?,?) RESULTS FOUND')

    for group, group_result in groups.items():
        best_result = None
        best_crit = None
        for rep in range(n_repeat):
            result = {}
            group_run_prefix = run_dir + 'out/' + str(rep)

            n_topics, n_clusters = [int(x) for x in group.split(',')]
            result['n_topics'] = n_topics
            result['n_clusters'] = n_clusters
            try:
                clusters = open(group_run_prefix + 'cluster(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO CLUSTERS FOR %s' % group)
                clusters = ''
            print('clusters:', len(clusters), clusters)
            result['clusters'] = clusters

            try:
                topics = open(group_run_prefix + 'beta(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO TOPICS FOR %s' % group)
                topics = ''
            result['topics'] = topics

            try:
                topics_per_edges = open(group_run_prefix + 'phi_sum(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO TOPICS FOR %s' % group)
                topics_per_edges = ''
            result['topics_per_edges'] = topics_per_edges

            try:
                rho_mat = open(group_run_prefix + 'rho(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO TOPICS FOR %s' % group)
                rho_mat = ''
            result['rho_mat'] = rho_mat

            try:
                pi_mat = open(group_run_prefix + 'PI(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO TOPICS FOR %s' % group)
                pi_mat = ''
            result['pi_mat'] = pi_mat

            try:
                theta_qr_mat = open(group_run_prefix + 'thetaQR(%s)' % group).read()
            except FileNotFoundError:
                print('ERROR: NO TOPICS FOR %s' % group)
                theta_qr_mat = ''
            result['theta_qr_mat'] = theta_qr_mat

            try:
                crit = float(open(group_run_prefix + 'crit(%s)' % group).read())
            except FileNotFoundError:
                print('ERROR: NO CRIT FOR %s' % group)
                crit = None
            result['crit'] = crit

            if not best_crit or (crit and crit > best_crit):
                best_result = result
                best_crit = crit

        for key in best_result:
            group_result[key] = best_result[key]
    # os.system('rm -rf %s' % (run_dir,))

    return groups, log

if __name__ == '__main__':
    from sample_graph import X, tdm
    groups, log = process(X, tdm, 2, 2, n_clusters_max=3, n_topics_max=2)

    for group in groups:
        print(group)
        print('score:', groups[group]['crit'])
        print(groups[group]['clusters'])

    print('log:', log[-100:])

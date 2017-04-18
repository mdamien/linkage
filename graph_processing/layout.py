import os, subprocess, time

def spacialize(X, labels, id=0):
    viz_dir = '/home/mel/prog/scratch/mega-viz'
    runs_dir = 'pm_runs/'
    run_dir = '%s/%d/' % (runs_dir, id)

    abs_run_dir = os.getcwd() + '/' + run_dir

    os.system('mkdir -p %s' % run_dir)
    os.system('cd %s;rm -rf in' % (run_dir,))
    os.system('cd %s;mkdir in' % (run_dir,))
    os.system('cd %s;rm -rf out' % (run_dir,))
    os.system('cd %s;mkdir out' % (run_dir,))
    os.system('cd %s;rm -rf layout' % (run_dir,))
    os.system('cd %s;mkdir layout' % (run_dir,))

    open(run_dir + 'in/X', 'w').write(X)
    open(run_dir + 'in/labels', 'w').write(labels)

    os.system('cd %s;node to_bin.js %s' % (viz_dir, abs_run_dir))

    # TODO: stop after step N
    os.system('cd %s/layout; %s/ngraph.native/layout++ ../out/links.bin' % (run_dir, viz_dir))

if __name__ == '__main__':
    X = """0 1 1
0 2 1
3 4 1
4 0 1
"""
    labels = "a b c d e"
    spacialize(X, labels)

Linkage
=======

The linkage web server is a Django app with a React/Vivagraph frontend. We also use celery to run jobs (here the linkage clustering)

You won't be able to run the linkage algorithm from those sources, the core alogo

### Installation and usage

```
# you must have a python3 virtualenv
sudo apt-get install python3 virtualenv python3-dev
virtualenv -p python3 venv
./venv/bin/activate

# install the dependencies
pip install -r requirements.txt

# create the postgres user / db with the SQL in ./mockup/init_pgsql.sql

# migrate the django app
./manage.py migrate

# a redis server must run (sudo apt-get install redis-server)

# install the javascript toolchain
sudo apt-get install npm nodejs
sudo npm install -g webpack-cli
cd frontend; npm install # in dev

# nltk tokenizer
python
> import nltk
> nltk.download() # and download the "stopwords" and the "punkt" dataset

# In dev you must run
./manage.py runserver # the server
fish ./scripts/dev_celery # celery (job worker)
fish ./scripts/dev_webpack # webpack (frontend)

You must have the linkage binary at `../repos/linkage-cpp/build/linkage` (compared to the linkage directory)

[TODO: add linkage-cpp diff fork source to this repos]

# In production
install nginx python3 virtualenv python3-dev build-essential
the config used on linkage.fr is available in doc/nginx_config

To make the app ready (static files compiled mostly), just run `fish ./scripts/update_prod`

Then you need to run 3 scripts to make the app ready:
   - fish ./scripts/prod_server # handle HTTP requests
   - fish ./scripts/prod_app # run the python server
   - fish ./scripts/prod_celery # run the job worker


# for linkage-cpp (not included here)
sudo apt-get install clang3.9 libomp-dev liblapack3 libblas3 libarpack2
clang++-3.9 -O3 linkage.cpp -o build/linkage -std=c++11 build/arma/libarmadillo.so -isystem build/arma/include/ -llapack -lblas -DARMA_DONT_USE_WRAPPER -DARMA_USE_BLAS -DARMA_USE_LAPACK -fopenmp=libomp

Linkage
=======

The linkage web server is a Django app with a React/Vivagraph frontend. We also use celery to run jobs (here the linkage clustering)

### Installation and usage

```
# you must have a python3 virtualenv
virtualenv -p python3 venv

# install the dependencies
pip install -r requirements.txt

# create the postgres user / db with the SQL in ./mockup/init_pgsql.sql

# migrate the django app
./manage.py migrate

# a redis server must run (sudo apt-get install redis-server)

# In dev you must run
./manage.py runserver # the server
fish ./scripts/dev_celery # celery (job worker)
fish ./scripts/dev_webpack # webpack (frontend)

You must have the linkage binary at `../repos/linkage-cpp/build/linkage` (compared to the linkage directory)

[TODO: add linkage-cpp fork source to this repos]

# In production
install nginx python3 virtualenv python3-dev build-essential
the config used on linkage.fr is available in doc/nginx_config

To make the app ready (static files compiled mostly), just run `fish ./scripts/update_prod`

Then you need to run 3 scripts to make the app ready:
   - fish ./scripts/prod_server # handle HTTP requests
   - fish ./scripts/prod_app # run the python server
   - fish ./scripts/prod_celery # run the job worker

# scripts
. virtualenv/linkage/bin/activate

# setup DB linkage-entreprise
# other solution: HAVE POSTGRES AND POSTGRES DATA IN THERE ALSO
cd linkage
sudo su postgres
    psql -f doc/init_pgsql.sql
exit
python manage.py migrate --settings=config.settings_enterprise
./manage.py shell --settings=config.settings_enterprise -c "
from django.contrib.auth.models import User
user = User.objects.create_superuser('admin', '', 'admin')
"
python manage.py loaddata --settings=config.settings_enterprise doc/staff_group.json


# run server
# ./manage.py migrate
python manage.py runserver --settings=config.settings_enterprise

# run worker
DJANGO_SETTINGS_MODULE=config.settings_enterprise ../virtualenv/linkage/bin/celery -A config worker -l info

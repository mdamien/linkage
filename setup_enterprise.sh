sudo apt-get install python3 python3-dev redis-server postgresql virtualenv libomp5 libarpack2

virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
python -c "import nltk;nltk.download('punkt');nltk.download('stopwords')"

# setup DB linkage-entreprise
sudo su postgres -c 'psql -f doc/init_pgsql.sql'
python manage.py migrate --settings=config.settings_enterprise
./manage.py shell --settings=config.settings_enterprise -c "
from django.contrib.auth.models import User
user = User.objects.create_superuser('admin', '', 'admin')
"
# python manage.py loaddata --settings=config.settings_enterprise doc/staff_group.json

echo "now you can run in two process:"
echo "    - scripts/enterprise_serv"
echo "    - linkage/scripts/enterprise_celery"

# zip
#  - source linkage OK
#  - lib python (le virtualenv) OK
#  - nltlk
#  - linkage-cpp
#  - arma.so
#
# req: python3, redis, postgres

mkdir linkage_zip

echo "Copying python sources..."
rsync -r --links --exclude=.git --exclude="db.sqlite3" --exclude="node_modules" linkage linkage_zip/
echo "Copying python libs from$VIRTUAL_ENV..."
mkdir -p linkage_zip/virtualenv/
rsync -r --links $VIRTUAL_ENV linkage_zip/virtualenv/

echo "Copying c++ binary..."
mkdir -p linkage_zip/repos/linkage-cpp/build/
rsync -r --links repos/linkage-cpp/build/ linkage_zip/repos/linkage-cpp/build

exit
# scripts

# setup DB linkage-entreprise
# other solution: HAVE POSTGRES AND POSTGRES DATA IN THERE ALSO
# TODO sudo su posgres   pgsql doc/init_pgsql.sql
cd linkage
python manage.py migrate --settings=config.settings_enterprise
./manage.py shell --settings=config.settings_enterprise -c "
from django.contrib.auth.models import User
from core.models import UserProfile

user = User.objects.create_superuser('admin', '', 'admin')
UserProfile(user=user, org_type='pro').save()
"

# run server
# ./manage.py migrate
python manage.py runserver --settings=config.settings_enterprise

# run worker
# TODO: shell version
begin
    set -lx DJANGO_SETTINGS_MODULE config.settings_enterprise
                ../virtualenv/linkage/bin/celery -A config worker -l info
end


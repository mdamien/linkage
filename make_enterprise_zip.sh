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
rsync -r --copy-links --exclude=.git --exclude="db.sqlite3" --exclude="node_modules" linkage linkage_zip/
echo "Copying python libs from$VIRTUAL_ENV..."
mkdir -p linkage_zip/virtualenv/
rsync -r --copy-links $VIRTUAL_ENV linkage_zip/virtualenv/

echo "Copying c++ binary..."
mkdir -p linkage_zip/repos/linkage-cpp/build/
rsync -r --copy-links repos/linkage-cpp/build/ linkage_zip/repos/linkage-cpp/build

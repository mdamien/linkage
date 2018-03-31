# zip
#  - source linkage OK
#  - lib python (le virtualenv) NOT YET WORKING
#  - nltlk
#  - linkage-cpp
#  - arma.so

mkdir linkage_enterprise

echo "Copying python sources..."
rsync -r --copy-links --exclude="collected_static" --exclude=.git --exclude="__pycache__" --exclude="venv/" --exclude="config/*prod*.py" --exclude="db.sqlite3" --exclude="user_uploads/" --exclude="node_modules" linkage linkage_enterprise/

# echo "Copying python libs from$VIRTUAL_ENV..."
# mkdir -p linkage_zip/virtualenv/
# rsync -r --copy-links $VIRTUAL_ENV linkage_zip/virtualenv/

echo "Copying c++ binary..."
mkdir -p linkage_enterprise/repos/linkage-cpp/build/arma/
cp repos/linkage-cpp/build/linkage linkage_enterprise/repos/linkage-cpp/build/linkage
cp repos/linkage-cpp/build/arma/*.so* linkage_enterprise/repos/linkage-cpp/build/arma/
tar -zcvf linkage-enterprise.tar.gz linkage_enterprise
rm -rf linkage_enterprise

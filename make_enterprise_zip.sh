# zip
#  - source linkage OK
#  - lib python (le virtualenv) NOT YET WORKING
#  - nltlk
#  - linkage-cpp
#  - arma.so

mkdir linkage_enterprise

echo "Copying python sources..."
rsync -r --copy-links --exclude=.git --exclude=".pyc" --exclude="venv/" --exclude="config/*prod*.py"
--exclude="db.sqlite3" --exclude="node_modules" linkage linkage_enterprise/

# echo "Copying python libs from$VIRTUAL_ENV..."
# mkdir -p linkage_zip/virtualenv/
# rsync -r --copy-links $VIRTUAL_ENV linkage_zip/virtualenv/

echo "Copying c++ binary..."
mkdir -p linkage_enterprise/repos/linkage-cpp/build/
rsync -r --copy-links repos/linkage-cpp/build/ linkage_enterprise/repos/linkage-cpp/build

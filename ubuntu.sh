#!/bin/bash
REPO=`dirname $(readlink -f $0)`
echo -n "Enter the Database Name You Want: "
read DBNAME

sudo apt-get install \
    postgresql-client \
    python-dev \
    build-essential \
    cmake \
    libqt4-dev \
    postgresql-9.1 \
    libqt4-sql-psql \

#Python 2.x series dependencies
sudo apt-get install \
    python-ply \
    python-psycopg2 \
    python-pygresql \
    python-unittest2 \

#Python 3.x series dependencies
sudo apt-get install \
    python3-ply \
    python3-psycopg2 \
#    python3-pygresql \ #does not exist?


cd "$REPO/src/GUI"
echo "Building perftrack GUI"
cmake -DPYTHON_LIBRARY=/usr/lib/python2.7/config/libpython2.7.so .
make

sudo -u postgres createuser --superuser $USER

echo "This is requesting a password for your database access"
echo "\password $USER" | sudo -u postgres psql

echo -n "Enter the DB password again: "
read -s USER_PASS

createdb $DBNAME

psql -d $DBNAME < "$REPO"/db_admin/postgres/pdropall.sql
psql -d $DBNAME < "$REPO"/db_admin/postgres/pcreate.sql

export DBPASS="$DBNAME,localhost,$USER,$USER_PASS"

echo "Populating some data into database"
PTDF="$REPO/src/dataStore/ptdf_entry.py"
export PTDB="PG_PYGRESQL"
export PYTHONPATH="$REPO/src/dataStore:$REPO/src/data_collection" 

"$PTDF" "$REPO"/share/PTdefaultFocusFramework.ptdf \
    "$REPO"/share/dataCenterResourceHierarchyExtensions.ptdf \
    "$REPO"/etc/PTdefaultMachines.ptdf 

"$REPO"/tests/PTdFgenTester.py --tnsname $DBNAME --username $USER \
    --hostname localhost --data_dir $REPO/tests/PTdFgenTestData

"$PTDF" "$REPO"/tests/PTdFgenTestData/irs-good.ptdf

echo "A database has been built and the perftrack GUI"
echo "dbname: $DBNAME"
echo "host: localhost"
echo "user: $USER"

if [ $? -eq 0 ]
then
    echo "You now have a fully functional perftrack, with some data populated."
    cd "$REPO/src/GUI"
    PYTHONPATH="." ./perftrack
else
    echo "Something went wrong"
fi


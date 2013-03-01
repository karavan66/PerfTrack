#!/bin/bash
REPO=`dirname $(readlink -f $0)`
DBNAME=$USER

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


cd $REPO/src/GUI
echo "Building perftrack GUI"
cmake -DPYTHON_LIBRARY=/usr/lib/python2.7/config/libpython2.7.so .
make

sudo -u postgres createuser --superuser $USER

echo "This is requesting a password for your database access"
echo "\password $USER" | sudo -u postgres psql

createdb $DBNAME

psql -d $DBNAME < $REPO/db_admin/postgres/pdropall.sql
psql -d $DBNAME < $REPO/db_admin/postgres/pcreate.sql

echo "A database has been built (default dbname is your username) and the perftrack GUI"
echo "dbname: $DBNAME"
echo "user: $USER"
echo "host: localhost"

echo "You now need to populate the DB with actual data via ptdf_entry.py"
echo "PYTHONPATH=\"src/dataStore:src/data_collection\" src/dataStore/ptdf_entry.py $REPO/tests/PTdFgenTestData/irs-good-reference.ptdf"
echo " to see something interesting in the GUI"
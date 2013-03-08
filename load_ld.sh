#!/bin/bash
if [ $# -ne 1 ]
then
    echo "Run this like ./load_ld.sh LD_DATA_PATH"
    echo "LD_DATA_PATH should be to extracted data from this archive:"
    echo "https://dl.dropbox.com/u/13119212/pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema.zip (2.4MB)"
    exit 1
fi
LD=$1
if [ ! -e "$LD" ]
then
    echo "That location \"$1\" does not exist"
    exit 1
fi
if [ ! -e "$LD/01_machinePTDF" ]
then
    echo "The location \"$LD\" does not appear to be the LD data"
    exit 1
fi
echo "This Script Assumes Have Run ubuntu.sh at least once and have already created a user w/ password"
echo "It will create/recreate a db for you."
echo -n "What DBNAME Do you want to put this in: "
read DBNAME

#REPO=`dirname $(readlink -f $0)`
REPO=/home/crzysdrs/pt_old/
PTDF="$REPO/src/dataStore/ptdf_entry.py"
PTDF_MULTI="$REPO/src/dataStore/ptdf_multi.py"
export PTDB="PG_PYGRESQL"
export PYTHONPATH="$REPO/src/dataStore:$REPO/src/data_collection"

createdb $DBNAME
psql -d $DBNAME < "$REPO"/db_admin/postgres/pdropall.sql
psql -d $DBNAME < "$REPO"/db_admin/postgres/pcreate.sql

#time python -m cProfile -s "cumulative" "$PTDF" \
#    "$LD"/ \
#    "$LD"/01_machinePTDF \
#    "$LD"/02_esdcPTDF \
#    "$LD"/03_systemPTDF \
#    "$LD"/04_appPTDF_t01 \
#    "$LD"/04_appPTDF_t02 \
#    "$LD"/04_appPTDF_t03

"$PTDF" \
    "$LD"/m_init.ptdf

#time "$PTDF_MULTI" \
#    "$LD"/m_data.ptdf
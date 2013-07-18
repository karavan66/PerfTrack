#!/bin/bash
#
# install.sh: Installs dependencies and builds perftrack.
#

# Prints the text supplied as an argument surrounded by a
# pretty banner.
function banner () {
    text="= $1 ="
    length="${#text}"
    foo=`seq 1 $length`

    banner=`printf '=%.0s' $foo`

    echo
    echo $banner
    echo $text
    echo $banner
    echo
}

# Calls the script that installs packages needed to build PerfTrack, if desired.
function install_dependencies () {
    echo "Do you want to install packages needed to build and run PerfTrack?"
    echo -n "y/n: "
    read INSTALL_DEPS

    if [ "$INSTALL_DEPS" == "y" ] || [ "$INSTALL_DEPS" == "Y" ]; then
        banner "Installing Dependencies"
        scripts/install-dependencies.sh
    else
        echo "Skipping dependencies."
    fi
}

# Builds the PerfTrack GUI.
function build_perftrack () {
    BASE_PATH="$1"
    OLD_PWD="$PWD"

    cd "$BASE_PATH/src/GUI"

    banner "Building PerfTrack GUI"

    # FIXME: Discover Python library rather than hardcoding it
    cmake -DPYTHON_LIBRARY=/usr/lib/python2.7/config/libpython2.7.so .
    make

    cd "$OLD_PWD"
}

function create_db () {
    BASE_PATH="$1"

    banner "Creating PerfTrack Database"

    echo "Creating a database user with your username and full rights."
    echo "You will be asked for your password."
    sudo -u postgres createuser --superuser $USER

    echo "This will set the database user's password:"
    echo "\password $USER" | sudo -u postgres psql

    echo -n "Enter the database user's password again: "
    read -s USER_PASS

    echo -en "\nEnter a name for the database: "
    read DBNAME

    echo "Creating the database $DBNAME..."
    createdb $DBNAME

    echo "Installing database schema..."
    psql -d $DBNAME < "$BASE_PATH"/db_admin/postgres/pdropall.sql
    psql -d $DBNAME < "$BASE_PATH"/db_admin/postgres/pcreate.sql

    # this will make the DBPASS variable available in case user decides
    # to populate the db
    export DBPASS="$DBNAME,localhost,$USER,$USER_PASS"
}

function populate_db () {
    BASE_PATH="$1"

    banner "Populating Database"

    PTDF="$BASE_PATH/src/dataStore/ptdf_entry.py"
    export PTDB="PG_PYGRESQL"
    export PYTHONPATH="$BASE_PATH/src/dataStore:$BASE_PATH/src/data_collection" 

    "$PTDF" "$BASE_PATH"/share/PTdefaultFocusFramework.ptdf \
        "$BASE_PATH"/share/dataCenterResourceHierarchyExtensions.ptdf \
        "$BASE_PATH"/etc/PTdefaultMachines.ptdf 

    "$BASE_PATH"/tests/PTdFgenTester.py --tnsname $DBNAME --username $USER \
        --hostname localhost --data_dir $BASE_PATH/tests/PTdFgenTestData

    "$PTDF" "$BASE_PATH"/tests/PTdFgenTestData/irs-good.ptdf
}

function create_and_populate_db () {
    BASE_PATH="$1"

    banner "Configuring PerfTrack Database"

    echo "Would you like to create a PostgreSQL database for PerfTrack?"
    echo -n "y/n: "
    read CREATE_DB

    # if they want to create db
    if [ "$CREATE_DB" == "y" ] || [ "$CREATE_DB" == "Y" ]; then
        create_db "$BASE_PATH"

        echo "Populate the database with demo data?"
        echo -n "y/n: "
        read POPULATE_DB

        if [ "$POPULATE_DB" == "y" ] || [ "$POPULATE_DB" == "Y" ]; then
            populate_db "$BASE_PATH"
        else
            echo "Skipping database population."
        fi
    else
        echo "Skipping database creation."
    fi
}

#####################
# Begin Main Script #
#####################

REPO=`dirname $(readlink -f $0)`

install_dependencies
build_perftrack "$REPO"
create_and_populate_db "$REPO"

#echo "A database has been built and the perftrack GUI"
#echo "dbname: $DBNAME"
#echo "host: localhost"
#echo "user: $USER"
#
#if [ $? -eq 0 ]
#then
#    echo "You now have a fully functional perftrack, with some data populated."
#    cd "$REPO/src/GUI"
#    PYTHONPATH="." ./perftrack
#else
#    echo "Something went wrong"
#fi


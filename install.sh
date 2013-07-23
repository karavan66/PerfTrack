#!/bin/bash
#
# install.sh: Installs dependencies and builds perftrack.
#

# Prints the text supplied as argument $1 surrounded by a
# pretty banner. If $2 is set, the banner will be printed
# as a 3-line box instead of as a single line.
function banner () {
    text="= $1 ="
    length="${#text}"
    foo=`seq 1 $length`

    print_big_banner="$2"

    banner=`printf '=%.0s' $foo`

    echo
    if [ "$print_big_banner" != "" ]; then
        echo $banner
    fi
    echo $text
    if [ "$print_big_banner" != "" ]; then
        echo $banner
    fi
    echo
}

# Calls the script that installs packages needed to build PerfTrack, if desired.
function install_dependencies () {
    echo "Do you want to install packages needed to build and run PerfTrack?"
    echo -n "y/n: "
    read INSTALL_DEPS

    if [ "$INSTALL_DEPS" == "y" ] || [ "$INSTALL_DEPS" == "Y" ]; then
        banner "Installing Dependencies" "y"
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

    banner "Building PerfTrack GUI" "y"

    # FIXME: Discover Python library rather than hardcoding it
    cmake -DPYTHON_LIBRARY=/usr/lib/python2.7/config/libpython2.7.so .
    make

    cd "$OLD_PWD"
}

# Creates a database superuser account and issues database commands to
# install the database.
function create_db () {
    BASE_PATH="$1"

    banner "Creating PerfTrack Database" "y"

    echo "Creating a database user with your username and full rights."
    echo "To do so, it will ask for your password."
    sudo -u postgres createuser --superuser $USER

    echo "This will set the database user's password:"
    echo "\password $USER" | sudo -u postgres psql

    echo -en "\nEnter a name for the database: "
    read DBNAME

    echo -n "Enter the database user's password: "
    read -s USER_PASS

    echo "Creating the database $DBNAME..."
    createdb $DBNAME

    echo "Installing database schema..."
    psql -d $DBNAME < "$BASE_PATH"/db_admin/postgres/pdropall.sql
    psql -d $DBNAME < "$BASE_PATH"/db_admin/postgres/pcreate.sql

    # this will make the DBPASS variable available in case user decides
    # to populate the db
    export DBPASS="$DBNAME,localhost,$USER,$USER_PASS"
}

# Runs programs that load data into the PerfTrack database.
function populate_db () {
    BASE_PATH="$1"

    banner "Populating Database" "y"

    PTDF="$BASE_PATH/src/dataStore/ptdf_entry.py"
    export PTDB="PG_PYGRESQL"
    export PYTHONPATH="$BASE_PATH/src/dataStore:$BASE_PATH/src/data_collection" 

    banner "Loading default focus framework, resource hierarchy, machines."
    "$PTDF" "$BASE_PATH"/share/PTdefaultFocusFramework.ptdf \
        "$BASE_PATH"/share/dataCenterResourceHierarchyExtensions.ptdf \
        "$BASE_PATH"/etc/PTdefaultMachines.ptdf 

    banner "Running data generation tests."
    "$BASE_PATH"/tests/PTdFgenTester.py --tnsname "$DBNAME" --username "$USER" \
        --hostname localhost --data_dir "$BASE_PATH"/tests/PTdFgenTestData

    if [ "$?" != "0" ]; then
        banner "Some tests failed. Review the output to see what happened."
    else
        banner "All tests passed."
    fi

    banner "Loading irs-good."
    "$PTDF" "$BASE_PATH"/tests/PTdFgenTestData/irs-good.ptdf
}

# Coordinates database creation and data loading.
function create_and_populate_db () {
    BASE_PATH="$1"

    banner "Configuring PerfTrack Database" "y"

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


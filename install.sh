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

# Checks whether user response was affirmative
function is_affirmative () {
    response="$1"

    if [ "$response" == "y" ] || [ "$response" == "Y" ]; then
        return 0
    else
        return 1
    fi
}

# Calls the script that installs packages needed to build PerfTrack, if desired.
function install_dependencies () {
    echo "Do you want to install packages needed to build and run PerfTrack?"
    echo -n "y/n: "
    read INSTALL_DEPS

    if is_affirmative "$INSTALL_DEPS" ; then
        banner "Installing Dependencies" "y"

	banner "Detecting Distribution"

        distro=`detect_supported_distros`
        if [ "$distro" == "ubuntu" ]; then
            echo "Ubuntu Linux Detected"
            scripts/install-dependencies-ubuntu.sh
        elif [ "$distro" == "enterprise-linux" ]; then
            echo "Enterprise Linux Detected"
            scripts/install-dependencies-el.sh
        else
            echo "detect_supported_distros answered \"$distro\""
            echo
            echo "This does not appear to be Ubuntu or a RHEL-based distro."
            echo "Skipping dependency installation."
            echo
            echo "You may be able to modify one of the scripts in scripts/"
            echo "to do what you want."
        fi
    else
        echo "Skipping dependencies."
    fi
}

# Detects Linux distributions supported by dependency scripts.
function detect_supported_distros () {
    detected="unknown"

    if [ -e /etc/redhat-release ] || [ -e /etc/centos-release ]; then
        detected="enterprise-linux"
    fi

    if [ -e /etc/debian_version ]; then
        distributor=`lsb_release -a 2>/dev/null | grep Distributor | cut -f 2`

        if [ "$distributor" == "Ubuntu" ]; then
            detected="ubuntu"
        else
            detected="debian-based"
        fi
    fi

    echo "$detected"
}

# Builds the PerfTrack GUI.
function build_perftrack () {
    BASE_PATH="$1"
    OLD_PWD="$PWD"

    banner "Building PerfTrack GUI" "y"

    cd "$BASE_PATH/src"

    ./build.sh

    build_status="$?"
    if [ "$build_status" == "0" ]; then
        banner "Build Complete"

        echo "Install PerfTrack system-wide?"
        echo -n "y/n: "
        read SYSTEM_INSTALL

        if is_affirmative "$SYSTEM_INSTALL" ; then
            cd "$BASE_PATH/src/build"
            echo "Installing..."
            sudo make install
        fi
    else
        banner "Build Not Successful"
    fi

    cd "$OLD_PWD"

    return $build_status
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

    echo -n "Enter the database user's password to create database: "
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

    if is_affirmative "$CREATE_DB" ; then
        create_db "$BASE_PATH"

        echo "Populate the database with demo data?"
        echo -n "y/n: "
        read POPULATE_DB

        if is_affirmative "$POPULATE_DB" ; then
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

# offer to install package dependencies on Linux
os_kernel=`uname -s`
if [ "$os_kernel" == "Linux" ]; then
    install_dependencies
fi

create_and_populate_db "$REPO"

build_perftrack "$REPO"

if [ "$DBPASS" != "" ]; then
    cat <<DatabaseInstallMsg
The database $DBNAME was created on localhost. A database user named
"$USER" was created with full superuser rights.

You can specify database-related configuration using environment variables.
See the "Environment Variables" section of the user manual for more details.
DatabaseInstallMsg
fi


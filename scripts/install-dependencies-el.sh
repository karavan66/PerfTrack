#!/bin/bash
# install-dependencies-el.sh: Installs packages needed to build and run
# perftrack on RHEL-based distributions.

PKG_CMD="yum -y"

function install_devel_packages () {
    # install basic utilities, compilers, etc
    $PKG_CMD groupinstall "Development Tools"
    $PKG_CMD install cmake curl

    # manual pages
    $PKG_CMD install man man-pages

    # libraries and -devel packages
    $PKG_CMD install \
        qt \
        qt-devel \
        python-devel
}

function fix_pg_hba_conf () {
    pg_hba_path="/var/lib/pgsql/data/pg_hba.conf"
    patched_hba_file="centos-pg_hba.conf"

    pg_diff=`sudo diff -u $pg_hba_path $patched_hba_file`

    if [ "$pg_diff" == "" ]; then
        echo "pg_hba.conf file already allows md5 access from localhost"
    else
        # do a crude check for md5 access to localhost over IPv4 and IPv6
        ipv4_md5=`sudo grep '127.0.0.1' $pg_hba_path | grep md5`
        ipv6_md5=`sudo grep '::1' $pg_hba_path | grep md5`

        # if ipv4 and ipv6 md5 allowed
        if [ "$ipv4_md5" != "" ] && [ "$ipv6_md5" != "" ]; then
            echo "pg_hba file at $pg_hba_path already appears to allow access to localhost via md5."
        else
            # replace default file that only uses ident authentication
            # with one that allows md5 auth
            echo "pg_hba file at $pg_hba_path does not appear to allow access to localhost via md5."
            echo "Installing a file that allows access. Original file will be backed up first."
            echo "See http://www.postgresql.org/docs/8.4/static/auth-pg-hba-conf.html"
            echo

            echo "Backing up $pg_hba_path to $pg_hba_path.orig"
            sudo cp $pg_hba_path $pg_hba_path.orig
            echo "Patching pg_hba.conf file"
            sudo cp $patched_hba_file $pg_hba_path
            sudo chown root:root $pg_hba_path
            sudo chmod 600 $pg_hba_path
        fi
    fi
}

function install_postgres_packages () {
    postgres_data_dir="/var/lib/pgsql"

    # install packages
    echo "Installing PostgreSQL packages ..."
    $PKG_CMD install \
        postgresql \
        postgresql-server \
        postgresql-devel \
        qt-postgresql

    # initialize database data directory
    if ! [ -d $postgres_data_dir ]; then
        echo -e "\nInitializing Postgres data dir ..."
        sudo service postgresql initdb
    fi

    # fix database access config file
    echo -e "\nMaking sure Postgres allows local MD5 access ..."
    fix_pg_hba_conf

    # enable database at system start
    echo -e "\nEnabling Postgres service ..."
    sudo chkconfig postgresql on

    # start db
    echo -e "\nStarting Postgres ..."
    sudo service postgresql start

    # install plpgsql language to default db template
    echo -e "\nInstalling plpgsql procedure language ..."
    sudo -u postgres createlang -U postgres plpgsql template1
}

# install psycopg2 python database library
function install_psycopg2 () {
    psycopg_url="http://initd.org/psycopg/tarballs/PSYCOPG-2-4/psycopg2-2.4.6.tar.gz"
    psycopg_directory="psycopg2-2.4.6"

    old_pwd=`pwd`

    # create build directory
    if ! [ -d temp ]; then
        mkdir temp
    fi

    cd temp

    echo -e "\nDownloading $psycopg_url ..."
    curl --progress-bar $psycopg_url > psycopg.tar.gz

    echo -e "\nUnpacking Psycopg archive ..."
    tar zxf psycopg.tar.gz

    echo -e "\nBuilding Psycopg ..."
    cd $psycopg_directory
    python setup.py build

    echo -e "\nInstalling ..."
    sudo python setup.py install

    cd $old_pwd
}

# install python lex / yacc (ply)
function install_ply () {
    ply_url="http://www.dabeaz.com/ply/ply-3.4.tar.gz"
    ply_dir="ply-3.4"

    old_pwd=`pwd`

    if ! [ -d temp ]; then
        mkdir temp
    fi

    cd temp

    echo -e "\nDownloading $ply_url ..."
    curl --progress-bar $ply_url > ply.tar.gz

    echo -e "\nUnpacking PLY archive ..."
    tar zxf ply.tar.gz

    echo -e "\nBuilding PLY ..."
    cd $ply_dir
    python setup.py build

    echo -e "\nInstalling ..."
    sudo python setup.py install

    cd $old_pwd
}

# install python unittest2 library
function install_unittest2 () {
    unittest2_url="https://pypi.python.org/packages/source/u/unittest2/unittest2-0.5.1.tar.gz"
    unittest2_dir="unittest2-0.5.1"

    old_pwd=`pwd`

    if ! [ -d temp ]; then
        mkdir temp
    fi

    cd temp

    echo -e "\nDownloading $unittest2_url ..."
    curl --progress-bar $unittest2_url > unittest2.tar.gz

    echo -e "\nUnpacking unittest2 ..."
    tar zxf unittest2.tar.gz

    echo -e "Building unittest2 ..."
    cd $unittest2_dir
    python setup.py build

    echo -e "Installing ..."
    sudo python setup.py install

    cd $old_pwd
}

#
# Main Script
#

if [ `whoami` != "root" ]; then
    echo "User isn't root. Will use sudo to install packages."
    echo
    PKG_CMD="sudo $PKG_CMD"
fi

install_devel_packages

install_postgres_packages

install_psycopg2

install_ply

install_unittest2


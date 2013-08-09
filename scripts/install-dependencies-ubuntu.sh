#!/bin/bash
# install-dependencies.sh: Installs packages needed to build and run perftrack.

# FIXME: Add package list, command for RHEL / CentOS

PKG_CMD="apt-get"

if [ `whoami` != "root" ]; then
    echo "User isn't root. Will use sudo to install packages."
    echo
    PKG_CMD="sudo $PKG_CMD"
fi

$PKG_CMD install \
    postgresql-client \
    python-dev \
    build-essential \
    cmake \
    libqt4-dev \
    postgresql-9.1 \
    libqt4-sql-psql \

#Python 2.x series dependencies
$PKG_CMD install \
    python-ply \
    python-psycopg2 \
    python-pygresql \
    python-unittest2 \

#Python 3.x series dependencies
$PKG_CMD install \
    python3-ply \
    python3-psycopg2 \


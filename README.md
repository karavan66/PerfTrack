PerfTrack
=========

PerfTrack is a tool for storing, navigating, and analyzing data from parallel
performance experiments, developed at UC/Lawrence Livermore National Laboratory
under the direction of co-PIs John May (johnmay@llnl.gov) and Karen Karavanic 
(karavan@cs.pdx.edu).

The PerfTrack frontend runs on Linux and OS X. Data collection scripts run on
Linux and AIX, but have primarily been tested on Linux.

Installing PerfTrack
--------------------

To build Perftrack, you will need the following:

- Python 2.6 or 2.7
- An SQL database (PostgreSQL 8.4.x or 9.1.x preferred)
- CMake 2.8
- Qt 4 with SQL database support for your DB of choice
- Psycopg 2.4 if you choose to use PostgreSQL

An installation script, `install.sh`, is included in the source tree. The script
covers several Linux distributions (Ubuntu versions, RHEL, CentOS). It will attempt
the following:

- install package dependencies appropriate for the distribution 
- build the source code
- install the programs built
- create a PostgreSQL database
- install a database schema to the database
- load test data and run tests

Most of these operations will require superuser access, so you may need to build
the program and load data manually. This process is described in the user's manual
provided in the `docs/` directory.


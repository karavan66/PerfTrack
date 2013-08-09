PerfTrack
=========

PerfTrack is a tool for storing, navigating, and analyzing data from parallel
performance experiments, developed at UC/Lawrence Livermore National Laboratory
under the direction of co-PIs John May (johnmay@llnl.gov) and Karen Karavanic 
(karavan@cs.pdx.edu).

Installing PerfTrack
--------------------

An installation script that covers many several Linux distributions, `install.sh`,
is included in the source tree. This script will attempt to the following:

- install package dependencies appropriate for the distribution 
- build the source code
- install the programs built
- create a PostgreSQL database
- install a database schema to the database
- load test data and run tests

Most of these operations will require superuser access, so you may need to build
the program and load data manually. This process is described in the user's manual
provided in the `docs/` directory.


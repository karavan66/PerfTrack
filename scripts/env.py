#!/usr/bin/env python

from subprocess import call
import os, sys

def ptdf(repo):
    return repo + "/src/dataStore/ptdf_entry.py"

def env_db(repo=None):
    if repo == None:
        repo = os.path.dirname(os.path.realpath(__file__)) + "/.."
    
    os.environ['PYTHONPATH'] = ("%s/src/dataStore/:%s/src/data_collection" % (repo, repo))
    os.environ['PTDB'] = 'PG_PYGRESQL'
    return repo

def init_db(repo):

    if not os.environ.get('DBPASS'):
        print "Must set env var DBPASS=dbname,hostname,username,dbpassword"
        print "In DBPASS, username should be your username!"
        sys.exit(1)

    (dbname, dbhost, dbuser, dbpass) = os.environ.get('DBPASS').split(",")
    print "Recreating Database"
    os.system("psql -d %s < %s/db_admin/postgres/pdropall.sql" % (dbname, repo))
    os.system("psql -d %s < %s/db_admin/postgres/pcreate.sql" % (dbname, repo))
    print "PTDF Entry of Default Framework"
    os.system("%s %s/share/PTdefaultFocusFramework.ptdf" % (ptdf(repo), repo))
    os.system("%s %s/share/dataCenterResourceHierarchyExtensions.ptdf" % (ptdf(repo), repo))

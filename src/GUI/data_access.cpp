// data_access.cpp
// John May, 5 November 2004

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#define USE_GROUP_BY 1

#include <qcheckbox.h>
#include <qcombobox.h>
#include <qlineedit.h>
#include <qmap.h>
#include <qmessagebox.h>
#include <qpair.h>
#include <qregexp.h>
#include <qsettings.h>
#include <qspinbox.h>
#include <q3sqlselectcursor.h>
#include <qsqlquery.h>
#include <qstring.h>
#include <qstringlist.h>
#include <qlist.h>

#include <qdatetime.h>
//Added by qt3to4:
#include <Q3ValueList>
// smithm 2008-6-25
// Added to get QSqlQuery::lastError to work
#include <QSqlError>

#include <unistd.h>

#include <iostream>

#include "data_access.h"
#include "host_connection.h"
#include "resource_type_and_name.h"
#include "result_table_cursor.h"

#include "data_access.moc"

// Text keys for storing host and database defaults
const QString APP_KEY = "/Perf Track GUI/";
const QString DB_NAME = "dbName";
const QString HOST_NAME = "hostName";
const QString USER_NAME = "userName";
const QString DB_TYPE = "dbType";
const QString REMOTE_HOST = "remoteHost";
const QString REMOTE_USER = "remoteUser";
const QString DB_PORT = "dbPort";

//! List of ports used by database types.  This is only
//! used for forwarding ports through ssh to access
//! databases on remote machines.  For local access,
//! Qt figures everything out.  This class may need to
//! be extended if we support more remote databases.
struct PortMapClass : public QMap<QString,int> {
	PortMapClass()
	{
		insert("QOCI8", 1521 );
		insert("QPSQL7", 5432 );
		insert("QPSQL", 5432);
		insert("QMYSQL3", 3306 );
	}
	// Look up the value, returning -1 if not found.
	int operator[]( QString key )
	{
		QMap<QString,int>::iterator loc;
		if( (loc = find( key ) ) != end() ) {
			return *loc;
		}
		else {
			return -1;
		}
	}
};

static PortMapClass portMap;

DataAccess::DataAccess( QObject * parent, const char * name )
	: QObject( parent, name ), resultsUsingMetrics( 0 )
	// smithm 2008-6-25
	// Removed curDB from intitialization list because it is no longer a pointer
{
}

DataAccess::~DataAccess()
{
	// Should be no need to close the database, and it can
	// cause hangs.
	
	// smithmtest 2008-7-20
    // This is a hack for MySQL
    // Look for each temp table in the list (case-insensitively) and
	// drop it if needed.
	// QString driver = curDb.driverName();
	// 	QStringList tables = curDb.tables();
	// 	
	// 	if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
	// 		if( !tables.grep( resourceTableName, FALSE ).isEmpty() )
	// 			dropTempTable( resourceTableName );
	// 		if( !tables.grep( addTableName, FALSE ).isEmpty() )
	// 			dropTempTable( addTableName );
	// 		if( !tables.grep( focusTableName, FALSE ).isEmpty() )
	// 			dropTempTable( focusTableName );
	// 		if( !tables.grep( metricTableName, FALSE ).isEmpty() )
	// 			dropTempTable( metricTableName );
	// 		if( !tables.grep( metricAddTableName, FALSE ).isEmpty() )
	// 			dropTempTable( metricAddTableName );
	// 		if( !tables.grep( resultTableName, FALSE ).isEmpty() )
	// 			dropTempTable( resultTableName );
	//     }
}

bool DataAccess::setupDBConnection()
{
	QString dbname;
	QString dbuname;
	QString password;
	QString host;
	QString dbtype;
	QString remotehost;
	QString remotehostuname;
	int port_to_forward;
	int user_port;
	QSettings settings;
	HostConnection * hostConn = NULL;
	bool saveDefaults = FALSE;

	// Get default settings, if available
	settings.setPath( "llnl.gov", "Perf Track GUI", QSettings::User );

	// Get database information and try to open a connection
	do {
		// Create dialog to request connection info
		DBConnectionDialog * dbcd = new DBConnectionDialog();

		// Set the default values, if available
		dbcd->dbNameLineEdit->setText(
				settings.readEntry( APP_KEY + DB_NAME ) );
		dbcd->userNameLineEdit->setText(
				settings.readEntry( APP_KEY + USER_NAME ) );
		dbcd->hostNameLineEdit->setText(
				settings.readEntry( APP_KEY + HOST_NAME,
				       "localhost" ) );
		dbcd->ext->hostNameLineEdit->setText(
				settings.readEntry( APP_KEY + REMOTE_HOST ) );
		dbcd->ext->userNameLineEdit->setText(
				settings.readEntry( APP_KEY + REMOTE_USER ) );
		dbcd->portSpinBox->setValue( 
				settings.readNumEntry( APP_KEY + DB_PORT, -1 )
				);

		// To set the connection type, see if the default value
		// is in the current list; if so, set that value as current.
		QString defaultDbType = settings.readEntry( APP_KEY + DB_TYPE );
		if( ! defaultDbType.isNull() ) {
			QComboBox * theBox = dbcd->dbTypeComboBox;
			for( int i = 0; i < theBox->count(); ++i ) {
				if( theBox->text( i ) == defaultDbType ) {
					theBox->setCurrentItem( i );
					break;
				}
			}
		}

		// If the first entry was successfully populated, set the
		// focus to the password entry, since it will always be empty
		if( ! dbcd->dbNameLineEdit->text().isEmpty() ) {
			dbcd->passwordLineEdit->setFocus();
		}

		// Pop up the dialog and get the settings if accepted
		if( dbcd->exec() == QDialog::Accepted ) {
			dbname = dbcd->dbNameLineEdit->text();
			dbuname = dbcd->userNameLineEdit->text();
			password = dbcd->passwordLineEdit->text();
			host = dbcd->hostNameLineEdit->text();
			dbtype = dbcd->dbTypeComboBox->currentText();
			remotehost = dbcd->ext->hostNameLineEdit->text();
			remotehostuname = dbcd->ext->userNameLineEdit->text();
			user_port = dbcd->portSpinBox->value();
			saveDefaults
				= dbcd->defaultSettingsCheckBox->isChecked();
			delete dbcd;
		} else {
			// User opted out
			delete dbcd;
			emit databaseConnected( false );
			return false;
		}

		// Try to create a connection
		// If the user specified a host name and user name,
		// attempt to log in to the remote machine.
		if( ! remotehost.isEmpty() && ! remotehostuname.isEmpty() ) {
			// Figure out what port to forward.  If user
			// said "default" we have to look up a value in 
			// a local table based on the db name.  If we
			// don't know the default, ask for help.
			port_to_forward = ( user_port < 0 )
				?  portMap[dbtype] : user_port;
			if( port_to_forward < 0 ) {
				QString message = "Don't know the default port "
					"for " + dbtype + ".  Either enter a "
					"value or use a local connection.";
				int whatNow = QMessageBox::warning( NULL,
					"Default port unknown",
					message, QMessageBox::Retry,
					QMessageBox::Abort );
				if( whatNow == QMessageBox::Abort ) {
					emit databaseConnected( false );
					return false;
				} else {
					continue;
				}
			}

			hostConn = new HostConnection( remotehost,
					remotehostuname, port_to_forward );
			if( hostConn == NULL || hostConn->connect() == false ) {
				QString message = "Failed to connect to "
					+ remotehost + " as " + remotehostuname
					+ ".  See terminal or console for "
					"details.";
				int whatNow = QMessageBox::warning( NULL,
					"Remote Host Connection Error",
					message, QMessageBox::Retry,
					QMessageBox::Abort );
				if( hostConn != NULL ) delete hostConn;
				if( whatNow == QMessageBox::Abort ) {
					emit databaseConnected( false );
					return false;
				} else {
					// Try again
					continue;
				}
			}
		}

		// Now try to log in to the database
		curDb = QSqlDatabase::addDatabase( dbtype );
		// smithm 2008-6-25
		// curDb no longer a pointer, changed -> to .
		curDb.setDatabaseName( dbname );
		curDb.setHostName( host );
		if( user_port >= 0 ) {
			// Set nondefault port number
			curDb.setPort( user_port );
		}

		if( !curDb.open( dbuname, password ) ) {
			QString message = "Failed to connect to ";
			message += dbname + " on host " + host
				+ " as user " + dbuname + ":\n" 
				+ curDb.lastError().text();
			int whatNow = QMessageBox::warning( NULL,
					"Database Connection Error",
					message, QMessageBox::Retry,
					QMessageBox::Abort );

			//QSqlDatabase::removeDatabase( curDb );

			// smithm 2008-7-5
			// void removeDatabase ( QSqlDatabase * db ) is no longer available
			// in Qt 4.  In Qt 4, attempting to remove the database generates a
			// warning that the connection is still in use and all queries will
			// cease to work.  When the user re-enters the correct information
			// the and the same database type is entered the new connection
			// will not be added.  Thus, queries will not work.  However,
			// if we do not remove the database on error and just have the user
			// enter new database information the Qt database library will
			// generate warning about a connection that is still in use, and
			// that it has removed the old connection, but queries will work.

			// smithm 2008-6-25
			// curDb is no longer a pointer
			//curDb = NULL;
			if( hostConn != NULL ) delete hostConn;
			if( whatNow == QMessageBox::Abort ) {
				emit databaseConnected( false );
				return false;
			} 
			// If we get here, user wants to retry;
			// loop around to try again
		} else if( saveDefaults ) {
			// Save defaults only if connection opened successfully
			settings.writeEntry( APP_KEY + DB_NAME, dbname );
			settings.writeEntry( APP_KEY + USER_NAME, dbuname );
			settings.writeEntry( APP_KEY + HOST_NAME, host );
			settings.writeEntry( APP_KEY + DB_TYPE, dbtype );
			settings.writeEntry( APP_KEY + REMOTE_HOST,
					remotehost );
			settings.writeEntry( APP_KEY + REMOTE_USER,
					remotehostuname );
			settings.writeEntry( APP_KEY + DB_PORT, user_port );
		}
	
	// smithm 2006-8-25
	// curDb is no longer a pointer, check to see if it is valid instead.
	//} while( curDb == NULL );
	} while( !curDb.isOpen() );

	// Shouldn't get here until we sucessfully open a connection;
	// failures return earlier
	
	// Set customization strings based on the DBMS we connected to
	initDBCustomizations();

	// Create temporary tables used to cache intermediate results.
	// Different databases handle temp tables differently.  
	// PostGresQL, MySQL, and SQLite automatically drop these tables
	// at the end of each session, so we have to recreate them here.
	// Oracle does not drop the table, but different sessions don't
	// see each other's data.  So we'll check here to see if our
	// tables already exist, and create them if not.  No need to
	// provide a session-specific name, since all DBMS's we've looked
	// at keep the data separate.  No need to drop the tables when
	// we're done either, since that is either done automatically,
	// or else the tables are preserved but truncated.
	resourceTableName = "resources_temp";
	addTableName = "adds_temp";
	focusTableName = "contexts_temp";
	metricTableName = "metrics_temp";
	metricAddTableName = "metric_adds_temp";
	resultTableName = "results_temp";

	// Get a list of current tables
	QStringList tables = curDb.tables();
    
	// Look for each table in the list (case-insensitively) and
	// create it if needed.
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( resourceTableName, "name VARCHAR(255)" );
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( addTableName, "name VARCHAR(255)" );
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( focusTableName, "focus_id INTEGER" );
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( metricTableName, "id INTEGER" );
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( metricAddTableName, "id INTEGER" );
	if( tables.grep( resourceTableName, FALSE ).isEmpty() )
		createTempTable( resultTableName,
			"saved SMALLINT, "
//S sharma -- made changes to add 'chk' column to GUI for showing High, Low, Expected and Unknown values of performance result
//			"value FLOAT, units VARCHAR(255), "
			"value FLOAT, chk VARCHAR(4000), units VARCHAR(255), "
			"metric VARCHAR(255), label VARCHAR(4000), combined SMALLINT, start_time VARCHAR(256), end_time VARCHAR(256), result_id INTEGER " );

	emit databaseConnected( true );
	return true;
}

void DataAccess::initDBCustomizations()
{
	QString driver = curDb.driverName();

	// Database-specific customizations
	if( driver == "QOCI8" ) {
		ociOrderedHint = " /*+ ORDERED */ ";
		tempTableFlag = " GLOBAL TEMPORARY ";
		tempTableSuffix = " ON COMMIT PRESERVE ROWS ";
	} else if ( driver == "QPSQL7" || driver == "QPSQL") {
		// smithm 2008-7-2
		// Changed to setup the same database customizations for the QPSQL7
		// and QPSQL driver.
		tempTableFlag = " GLOBAL TEMPORARY ";
		tempTableSuffix = " ON COMMIT PRESERVE ROWS ";
	} else if ( driver == "QSQLITE" ) {
		tempTableFlag = " TEMPORARY ";
		tempTableSuffix = "";
	// smithm 2008-6-25
	// It appears this should be a comparision and not an assignment.
	//} else if ( driver = "QMYSQL3" ) {
	// smithm 2008-7-8
	// Changed to setup the same database customizations for the QMYSQL3
	// and QMYSQL driver.
    // smithmtest
    // don't create temporary tables in MySQL
	// switched back to temporary tables for now
	} else if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		// MySQL Not tested yet!
		tempTableFlag = " TEMPORARY ";
		tempTableSuffix = " ";
	// smithm 2008-7-2
	// Set default customization for all other databases.
	} else {
		tempTableFlag = " TEMPORARY ";
		tempTableSuffix = "";
	}
	
	// Other DB specific customizations to be added here as needed
}

QStringList DataAccess::queryForStrings( QString queryText )
{
	QStringList results;

	// Prepare the query
	QSqlQuery query( curDb );
	query.setForwardOnly( true );	// optimize for simple traversal

	// Execute the query
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to execute %s\n", queryText.latin1() );
		return results;
	}

	// Walk through the items and put the names in a list
	while( query.next() )  {
		results += query.value(0).toString();
	}

	return results;
}

int DataAccess::queryForInt( QString queryText )
{
	// Prepare the query
	QSqlQuery query( curDb );
	query.setForwardOnly( true );	// optimize for simple traversal

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	// Execute the query
	if( ! query.exec( queryText ) ) {
		fprintf( stderr, "Query failed: %s\n", queryText.latin1() );
		return -1;
	}

	// Walk through the items and put the names in a list
	if( query.next() )  {
		return query.value(0).toInt();
	}

	return -1;
}

Q3ValueList<QStringList> DataAccess::getResourceTypes()
{
	Q3ValueList<QStringList> rt;

// This version gets all known resource types, even if they
// aren't part of any focus
	QStringList resourceTypes = queryForStrings(
			"SELECT DISTINCT type FROM resource_item" );
// This version gets only the resource types that are part of some
// focus, plus their ancestors.  It takes much longer
//	QStringList resourceTypes = queryForStrings(
//			"SELECT DISTINCT type FROM resource_item WHERE id IN "
//			"(SELECT DISTINCT resource_id FROM focus_has_resource "
//			"UNION SELECT DISTINCT aid FROM resource_has_ancestor)"
//		);
	if( resourceTypes.isEmpty() ) return rt;

// Ugly hack!  "metric" is not currently stored in a focus, but we can
// always use it in a query because it's stored with every performance
// result.  This hack needs to be carried through resource selection
// result counting, and result acquisition.
	resourceTypes += "metric";
	resourceTypes.removeDuplicates(); //Annoys me seeing metric twice
	return parseResourceTypes( resourceTypes );
}
	
Q3ValueList<QStringList> DataAccess::parseResourceTypes(QStringList fullResourceTypes )
{
	// We want a list of of lists of resource type strings.
	// The database will pass us a list of resource names,
	// which look like: grid, grid/machine, grid/machine/partion,
	// etc.  We will use the full path names, not just the end
	// names, since the full names are stored with the resource
	// descriptions.  To divide these into groups, we will sort
	// the list of strings we get, which will order them by
	// groups, with the least-specific names appearing first.
	// Whenever a name doesn't contain the preceding name, we
	// start a new group.  The list may include nonhierarchical
	// resource names.  These should work fine; they'll just
	// produce singleton string lists.
	
	fullResourceTypes.sort();

	Q3ValueList<QStringList> resourceChains;
	QString lastString;	// Null string will be contained by any string
	QStringList currentChain;
	QStringList::Iterator rtit;
	for( rtit = fullResourceTypes.begin(); rtit != fullResourceTypes.end();
			++rtit ) {

		// Does this string contain the last one?  If not, start
		// a new chain.
		if( ! (*rtit).contains( lastString ) ) {
			resourceChains += currentChain;
			currentChain.clear();
		}

		// Add current string to the chain.
		currentChain += (*rtit);
		lastString = currentChain[0];
	}

	// Add the last chain, if nonempty
	if( ! currentChain.isEmpty() ) {
		resourceChains += currentChain;
	}

	return resourceChains;
}

void DataAccess::findAttributesByType( QString resourceType, QString filter,void * requester )
{
#ifdef DEBUG
	qWarning( "findAttributesByType looking for resources "
			"of type %s with filter %s\n",
			resourceType.latin1(), filter.latin1() );
#endif

	// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT DISTINCT ra.name "
			"FROM resource_item ri, resource_attribute ra "
			"WHERE ri.id = ra.resource_id "
			"AND type = '" + resourceType + "' ";

	// inFocus determines whether we insist that attributes we're
	// looking for correspond to resources that appear in some focus
	if( false ) {
		queryText += "AND ri.id IN "
				"(SELECT resource_id FROM focus_has_resource) ";
//				"(SELECT resource_id FROM resource_ids_jmm) ";
	}
	
	if( ! filter.isEmpty() )
		queryText += " AND " + filter + " ";

	// Since we're not merging the results, we'll have the database sort
	queryText += "ORDER BY ra.name";

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	// Create a list of results and return it
	QStringList attributes;
	while( query.next() )  {
		attributes += query.value(0).toString();
	}

	if( attributes.count() > 0 ) {
		emit foundAttributesByType( resourceType, attributes,
				requester );
	}
}

void DataAccess::findResourcesByType( QString resourceType, QString filter,void * requester )
{
#ifdef DEBUG
	qWarning( "findResourcesByType looking for resources "
			"of type %s with filter %s\n",
			resourceType.latin1(), filter.latin1() );
#endif

	// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT name, id "
			"FROM resource_item "
			"WHERE type = '" + resourceType + "' ";

	if( ! filter.isEmpty() )
		queryText += " AND " + filter;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

#ifdef USE_OLD_TABLES
	// Create a merged list of names, using either the full name
	// or just the last part (after the final '/'), depending on
	// the compiled value of USE_FULL_RESOURCE_NAMES
	QMap<QString,QPair<QString,QString> > map = buildResultMap( query,
			! USE_FULL_RESOURCE_NAMES );

	if( map.count() > 0 ) {
		emit foundResourcesByType( resourceType, map, requester );
	}
#else
	QMap<QString,int> map = buildResultMap( query );
	if( map.count() > 0 ) {
		emit foundResourcesByType( resourceType, map, requester );
	}
#endif

}

void DataAccess::findAttributesByName( QString attribute, QString filter, SelectionListItem * parentListItem )
{
#ifdef DEBUG
	qWarning( "findAttributesByName looking for "
			"attributes with attribute %s with filter %s\n",
			attribute.latin1(), filter.latin1() );
#endif

		// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

#ifdef USE_OLD_TABLES
	QString queryText = "SELECT value, resource_id "
			"FROM resource_attribute "
			"WHERE name = '" + attribute + "' ";

	if( ! filter.isEmpty() )
		queryText += " AND " + filter;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	QMap<QString,QPair<QString,QString> > map
		= buildResultMap( query, false );

	if( map.count() > 0 ) {
		emit foundAttributesByName( attribute, map, parentListItem );
	}
#else
	QString queryText = "SELECT DISTINCT value "
			"FROM resource_attribute "
			"WHERE name = '" + attribute + "' ";

	if( ! filter.isEmpty() )
		queryText += " AND " + filter + " ";

	queryText += "ORDER BY value";

	QStringList list = queryForStrings( queryText );

	if( list.count() > 0 ) {
		emit foundAttributesByName( attribute, list, parentListItem );
	}
#endif
}

void DataAccess::findResourcesByParent( QString idList, QString filter, SelectionListItem * parentListItem )
{
#ifdef DEBUG
	qWarning( "findResourcesByParent looking for "
			"resources with parent %s with filter %s\n",
			parentValue.latin1(), filter.latin1() );
#endif

	// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT ri.name, ri.id "
			"FROM resource_item ri WHERE ri.parent_id IN "
			"(" + idList + ")";

	if( ! filter.isEmpty() )
		queryText += " AND " + filter;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	QMap<QString,QPair<QString,QString> > map = buildResultMap( query,
			! USE_FULL_RESOURCE_NAMES );

	// See if we got any data; if not, skip the next step
	if( map.count() == 0 ) return;

	// Now we need to look up the type of these resources.  WE
	// ASSUME IT'S THE SAME FOR ALL CHILDREN OF THESE PARENTS,
	// so we look it up once and send a single value, rather than
	// pairing it with each item we return.
	
	QString firstId = idList.section( QChar(','), 0, 0 );
	queryText = "SELECT DISTINCT type FROM resource_item "
		"WHERE parent_id = " + firstId;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	if( ! query.next() ) {	// Get to the first record, if possible
		qWarning( "Failed to get resource type on successul query!" );
		return;
	}

	QString type = query.value(0).toString();

	emit foundResourcesByParent( type, map, parentListItem );

}

void DataAccess::findResourcesByParent( QString parentType, QString baseName, QString filter, SelectionListItem * parentListItem )
{
#ifdef DEBUG
	qWarning( "findResourcesByParent looking for "
			"resources with parent %s with filter %s\n",
			parentValue.latin1(), filter.latin1() );
#endif

	// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText =
		"SELECT ric.name FROM resource_item ric, resource_item rip "
		"WHERE ric.parent_id = rip.id "
		"AND rip.type = '" + parentType + "' "
		"AND rip.name LIKE '%" + baseName + "'";

	if( ! filter.isEmpty() )
		queryText += " AND " + filter;

        //debug
        fprintf(stderr, "findResourcesByParent executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	QMap<QString,int> map = buildResultMap( query );

	// See if we got any data; if not, skip the next step
	if( map.count() == 0 ) return;

	// Now we need to look up the type of these resources.  WE
	// ASSUME IT'S THE SAME FOR ALL CHILDREN OF THESE PARENTS,
	// so we look it up once and send a single value, rather than
	// pairing it with each item we return.
	queryText =
		"SELECT DISTINCT ric.type "
		"FROM resource_item ric, resource_item rip "
		"WHERE ric.parent_id = rip.id "
		"AND rip.type = '" + parentType + "'";

        //debug
        fprintf(stderr, "findResourcesByParent executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	if( ! query.next() ) {	// Get to the first record, if possible
		qWarning( "Failed to get resource type on successul query!" );
		return;
	}

	QString type = query.value(0).toString();

	emit foundResourcesByParent( type, map, parentListItem );

}

// Used for version that refers to resources only by name
// and does not store individual names locally
void DataAccess::findAttributesByResourceName( QString name,SelectionListItem * sli )
{
#ifdef DEBUG
	qWarning( "findAttributesByResourceName looking for attributes "
			"with name %s\n", name.latin1() );
#endif

		// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT ri.name, ra.name, ra.value "
		"FROM resource_attribute ra, resource_item ri "
		"WHERE ri.id = ra.resource_id "
		"AND ri.name LIKE '%" + name + "' ";

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	// Return a map of lists of pairs.  The map key is the
	// resource name (there may be only one), and the corresponding
	// list contains the attributes and their values.
	AttrListMap map;
	AttrListMap::iterator map_it;

	// Add each row from the result to the list.
	while( query.next() ) {
		QString key = query.value(0).toString();
		// See if the list exists for this resource; create it if not
		if( ( map_it = map.find( key ) ) == map.end() ) {
		       map_it = map.insert( key,
				       Q3ValueList<QPair<QString,QString> >() );
		}
		
		// Insert this pair into the relevant list
		(*map_it) += QPair<QString,QString>( query.value(1).toString(),
				query.value(2).toString() );
	}

	emit foundAttributesByResourceName( map, sli );
}

void DataAccess::findExecutionResourcesByName( QString name, SelectionListItem * sli )
{
#ifdef DEBUG
	qWarning( "findExecutionResourcesByName looking for resources "
			"with id %s\n", name.latin1() );
#endif

		// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	// Look up the execution's resource id, then look up matching
	// resource ids in execution_has_resource and find the corresponding
	// names.  When we get rid of resource ids and just use names,
	// this should be a simple one-table lookup
	QString queryText = "SELECT er.type, er.name "
		"FROM resource_item ri, execution_has_resource ehr, "
		"resource_item er "
		"WHERE ri.name = '" + name + "' "
		"AND ri.id = ehr.eid "
		"AND ehr.rid = er.id ";

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	Q3ValueList<QPair<QString,QString> > list;

	// Add each row from the result to the list.
	while( query.next() ) {
		list += QPair<QString,QString>( query.value(0).toString(),
				query.value(1).toString() );
	}

	emit foundExecutionResources( list, sli );
}

// Used when we kept track of resource ids explicitly in the GUI
void DataAccess::findAttributesById( QString id, SelectionListItem * sli )
{
#ifdef DEBUG
	qWarning( "findAttributesById looking for attributes with id %s\n",
			id.latin1() );
#endif

		// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT name, value FROM resource_attribute "
			"WHERE  resource_id = " + id;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	Q3ValueList<QPair<QString,QString> > list;

	// Add each row from the result to the list.
	while( query.next() ) {
		list += QPair<QString,QString>( query.value(0).toString(),
				query.value(1).toString() );
	}

	emit foundAttributesById( id, list, sli );
}

void DataAccess::findExecutionResourcesById( QString id, SelectionListItem * sli )
{
#ifdef DEBUG
	qWarning( "findExecutionResourcesById looking for resources "
			"with id %s\n", id.latin1() );
#endif

		// Prepare the query (on the default db for now: FIX)
	QSqlQuery query;
	query.setForwardOnly( true );	// optimize for simple traversal

	QString queryText = "SELECT ri.type, ri.name "
		"FROM resource_item ri, execution_has_resource ehr "
		"WHERE ehr.rid = ri.id AND ehr.eid = " + id;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) )
		return;

	Q3ValueList<QPair<QString,QString> > list;

	// Add each row from the result to the list.
	while( query.next() ) {
		list += QPair<QString,QString>( query.value(0).toString(),
				query.value(1).toString() );
	}

	emit foundExecutionResources( list, sli );
}

QString DataAccess::findResourceIdsByType( QString type )
{
	QString queryText =
		"SELECT id FROM resource_item WHERE type = '" + type + "'";

	return queryForStrings( queryText ).join(",");
}

int DataAccess::addResourcesByName( QString type, QString name )
{
	if( resourceTableName.isNull() ) {
		qWarning( "No temp table; can't insert data" );
		return -1;
	}

	QString queryText;
	QString addTable;
	QString tempTable;

	if( type != "metric" ) {
		addTable = addTableName;
		tempTable = resourceTableName;
		queryText =
			"INSERT INTO " + addTableName + " "
			"SELECT name FROM resource_item ";
	} else {
		// Record metric ids rather than names to save a join later.
		// Some day, the id will be the same as the name and
		// we won't have to do this.
		addTable = metricAddTableName;
		tempTable = metricTableName;
		queryText =
			"INSERT INTO " + metricAddTableName + " "
			"SELECT id FROM resource_item ";
	}

	queryText += "WHERE type = '" + type + "' ";

	// If name was given (as it usually is), add it
	if( ! name.isNull() ) {
		queryText += "AND name LIKE '%" + name + "'";
	}


        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal


	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to create adds table" );
		return -1;
	}

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + tempTable + " "
		"SELECT * FROM " + addTable;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add resources of type \"" + type + "\"";
		if( ! name.isEmpty() )
			message += " and name \"" + name;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return -1;
	}

	int newItems;		// How many items would now be selected

	// Result count is done differently for metrics
	if( type == "metric" ) {
		// Keep track of the result count for metrics in class variable
		newItems = resultsUsingMetrics
			= getResultCountMetrics( metricAddTableName );
	} else {
		newItems = getResultCountSingle( addTableName );
	}

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	query.exec( "DELETE FROM " + addTable );

	return newItems;
}

int DataAccess::addResourcesByAttribute( QString type, QString attr, QString value )
{
	if( resourceTableName.isNull() ) {
		qWarning( "No temp table; can't insert data" );
		return -1;
	}

	// FIX! Once resource items are indexed by name we can
	// skip the join and just get the names from resource_attribute
	QString queryText;
	QString addTable;
	QString tempTable;

	if( type != "metric" ) {
		addTable = addTableName;
		tempTable = resourceTableName;
		queryText =
			"INSERT INTO " + addTableName + " "
			"SELECT ri.name FROM resource_item ri,";
	} else {
		// Record metric ids rather than names to save a join later.
		// Some day, the id will be the same as the name and
		// we won't have to do this.  For metrics, we have an
		// unnecessary join here already.  That should go away
		// at the same time.
		addTable = metricAddTableName;
		tempTable = metricTableName;
		queryText =
			"INSERT INTO " + metricAddTableName + " "
			"SELECT ri.id FROM resource_item ri,";
	}

	queryText += 
		"resource_attribute ra "
		"WHERE ri.type = '" + type + "' "
		"AND ra.name = '" + attr + "' "
		"AND ra.value = '" + value + "' "
		"AND ra.resource_id = ri.id";

	QSqlQuery query;
	query.setForwardOnly( true );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to add resource by attr to temp table" );
		return -1;
	}

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + tempTable + " "
		"SELECT * FROM " + addTable;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add resources of type \"" + type + "\""
			" with " + attr + " = " + value;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
			return -1;
	}

	int newItems;		// How many items would now be selected

	// Result count is done differently for metrics
	if( type == "metric" ) {
		// Keep track of the result count for metrics in class variable
		newItems = resultsUsingMetrics
			= getResultCountMetrics( metricAddTableName );
	} else {
		newItems = getResultCountSingle( addTableName );
	}

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	query.exec( "DELETE FROM " + addTable );

	return newItems;
}

void DataAccess::deleteResourcesByName( QString type, QString name )
{
	if( resourceTableName.isNull() ) {
		qWarning( "No temp table; can't insert data" );
		return;
	}

	QString queryText;
	if( type != "metric" ) {
		queryText =
			"DELETE FROM " + resourceTableName + " "
			"WHERE name IN "
			"( SELECT name FROM resource_item ";
	} else {
		// Record metric ids rather than names to save a join later.
		// Some day, the id will be the same as the name and
		// we won't have to do this.
		queryText =
			"DELETE FROM " + metricTableName + " "
			"WHERE id IN "
			"( SELECT id FROM resource_item ";
	}

	queryText += "WHERE type = '" + type + "' ";

	// If name was given (as it usually is), add it
	if( ! name.isNull() ) {
		queryText += "AND name LIKE '%" + name + "'";
	}

	queryText += ")";

	QSqlQuery query;
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete resource by name from temp table" );
	}

	// Update the metrics result count, if needed
	if( type == "metric" ) {
		resultsUsingMetrics = getResultCountMetrics( metricTableName );
	}
}

void DataAccess::deleteResourcesByAttribute( QString type, QString attr, QString value )
{
	if( resourceTableName.isNull() ) {
		qWarning( "No temp table; can't insert data" );
		return;
	}

	// FIX! Once resource items are indexed by name we can
	// skip the join and just get the names from resource_attribute
	QString queryText;
	if( type != "metric" ) {
		queryText =
			"DELETE FROM " + resourceTableName + " "
			"WHERE name IN "
			"(SELECT ri.name FROM resource_item ri,";
	} else {
		// Record metric ids rather than names to save a join later.
		// Some day, the id will be the same as the name and
		// we won't have to do this.  For metrics, we have an
		// unnecessary join here already.  That should go away
		// at the same time.
		queryText =
			"DELETE FROM " + metricTableName + " "
			"WHERE id IN "
			"(SELECT ri.id FROM resource_item ri,";
	}
	queryText +=
		"resource_attribute ra "
		"WHERE ri.type = '" + type + "' "
		"AND ra.name = '" + attr + "' "
		"AND ra.value = '" + value + "' "
		"AND ra.resource_id = ri.id)";

	QSqlQuery query;
        //debug

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete resource by attr from temp table" );
	}

	// Update the metrics result count, if needed
	if( type == "metric" ) {
		resultsUsingMetrics = getResultCountMetrics( metricTableName );
	}
}

QMap<QString,QPair<QString,QString> > DataAccess::buildResultMap( QSqlQuery& query, bool truncate )
{
	QMap<QString,QPair<QString,QString> > map;
	QString key;
	QString fullName;
	QString id;
	QString idList;

	// Run through the results, look for existing matches.
	// If no match found, add the pair to the map.  If there
	// is a match, append the id to the list.
	while( query.next() ) {
		fullName = query.value(0).toString();
		key = truncate ? fullName.section( QString(PTRESDELIM), -1 ) : fullName;
		id = query.value(1).toString();

		// Try to insert a new item; if it already exists,
		// use the returned iterator to update.  (This approach
		// should be faster than checking for the item and
		// inserting if not found, because we traverse the map
		// only once.)
		//QPair<QMapIterator<QString,QPair<QString,QString> >,bool>
//			result = map.insert( QPair<const QString,
//					QPair<QString,QString> >
//					( key,
//					  QPair<QString,QString>( id,
//						  fullName ) ) );

		// Append the id if the string was already in the list
		//if( ! result.second ) {
//			(*result.first).first = (*result.first).first
//				+ "," + id;
//			(*result.first).second = (*result.first).second
//				+ "," + fullName;
//		}
		
		// 2008-6-28 smithm
		// The previous insertion optimization does not work in Qt 4.
		// This method works with Qt 4, but is slower because it iterates
		// over the map twice.
		QMap<QString,QPair<QString,QString> >::iterator result;
		QPair<QString,QString> pair = QPair<QString,QString>(id,fullName);
		result = map.begin();
		// Iterate over the map.  If a matching value is found, append the id.
		while(result != map.end()) {
			if (result.value() == pair) {
				QPair<QString,QString> newPair =
					QPair<QString,QString> (result.value().first + "," + id,
					result.value().second + "," + fullName);
				result.value() = newPair;
				continue;
			}
			result++;
		}
		// If the end of the map is reached no matching value was found so
		// insert the pair
		if (result == map.end())
			map.insert(key, pair);
	}

	return map;
}

QMap<QString,int> DataAccess::buildResultMap( QSqlQuery& query )
{
	QMap<QString,int> map;
	QString key;
	QString fullName;

	// Run through the results, look for existing matches.
	// If no match found, add the item to the map.  If there
	// is a match, do nothing.
	while( query.next() ) {
		fullName = query.value(0).toString();
		key = fullName.section( QString(PTRESDELIM), -1 );

		// Insert the new item.  Nothing happens if it
		// already exists.  We don't put any meaningful data in
		// the map; we just want a sorted unique list of keys.
		//2008-6-28 smithm
		// This insertion call doesn't work in Qt 4, updated.
		//map.insert( QPair<const QString, int>( key, 0 ) );
		map.insert(key, 0);
	}

	return map;
}

int DataAccess::getResultCount( QStringList resources, QString metricIds )
{

	// Nothing specified, so there are no matching results
	if( resources.count() == 0 && metricIds.isEmpty() ) return 0;

#ifdef USE_OLD_TABLES
	QString queryText 
	"SELECT COUNT(*) FROM performance_result ";
	if( resources.count() != 0 ) {
#ifdef USE_GROUP_BY
		queryText +=
			"WHERE focus_id IN "
			"( SELECT focus_id FROM focus_has_resource "
			"  WHERE resource_id IN ( " + resources.join(",") + ") "
			"  GROUP BY focus_id "
			"  HAVING COUNT(resource_id) = "
			+ QString::number( resources.count() ) + ")";
#else
		queryText +=
			"WHERE focus_id IN "
			"( (SELECT focus_id FROM focus_has_resource "
				"WHERE resource_id IN ("
				+ resources.first() + ") ) ";

		// Start from the second item in the list, since we've
		// already seen the first one.
		QStringList::ConstIterator rit = resources.begin();
		for( ++rit; rit != resources.end(); ++rit ) {
			queryText += "INTERSECT ( SELECT focus_id FROM "
				"focus_has_resource WHERE resource_id IN "
				"( " + *rit + ") ) ";
		}

		queryText += ")";
#endif

		// Both metric id and resource ids were given
		if( ! metricIds.isEmpty() )
			queryText += " AND metric_id IN (" + metricIds + ")";
	} else {
		// Only the metric ids were given...
		queryText +=
			"WHERE metric_id IN (" + metricIds + ")";
	}
#else
	QString queryText =
		"SELECT COUNT(*) FROM performance_result_has_focus "
		"WHERE focus_id IN "
		" (SELECT "
		+ ociOrderedHint +
		" focus_id FROM "
		+ resourceTableName + " t, focus_has_resource_name fhrn "
		"  WHERE t.name = fhrn.resource_name "
		"  GROUP BY fhrn.focus_id HAVING COUNT(resource_name) = "
		   + QString::number( resources.count() ) + ")";
	// FIX!! Need to handle metric ids 
#endif

	printf( "DataAccess::getResultCount query:\n%s\n", queryText.latin1() );
	
	return queryForInt( queryText );
}

int DataAccess::getResultCountSingle( QString table )
{

	if( table.isNull() ) return -1;

	// As in getResultCount, the ordered hint help Oracle
	// do the joins in a reasonable order
	QString queryText =
  		"SELECT "
		+ ociOrderedHint +
		"COUNT(*) FROM " + table + " t, "
		"focus_has_resource_name fhrn, "
		"performance_result_has_focus prhf "
		"WHERE t.name = fhrn.resource_name "
		"AND fhrn.focus_id = prhf.focus_id";
	return queryForInt( queryText );
}

int DataAccess::getResultCountMetrics( QString tableName ,QStringList labels)
{
	QString queryText =
		"SELECT "
		+ ociOrderedHint +
		"COUNT(*) FROM " + tableName + " m, performance_result pr "
		"WHERE m.id = pr.metric_id ";
	if(!labels.isEmpty()){
	   QStringList::iterator it;
	   bool first = true;
	   for(it=labels.begin(); it != labels.end(); ++it){
               queryText += QString(first ? " AND (": " OR ") + "label='" + (*it) + "' ";
               first = false;
	   }
	   queryText += ")";
	}

	return queryForInt( queryText );
}

int DataAccess::getResultCountLabels (QStringList labels){
        QString queryText  = "select count(*) from performance_result where ";
        bool first = true;
        for (QStringList::iterator it=labels.begin(); it != labels.end(); ++it){
            queryText += QString(first ? "": " OR ") + "label='" + (*it) + "' ";
            first = false;
        }
        return queryForInt(queryText);
}

int DataAccess::getResultCount( int typeCount, QString /*metricIds*/, QStringList labels )
{

	if( typeCount == 0 && resultsUsingMetrics > 0)
		return getResultCountMetrics( metricTableName,labels );

        if (typeCount == 0 && !labels.isEmpty())
                return getResultCountLabels(labels);
	// First step is to reset the list of foci and populate it
	// with the ones that will be selected by the current set 
	// of resources.  This list is cached for use when the
	// results are actually requested.
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( "DELETE FROM " + focusTableName ) ) {
		qWarning( "Failed to delete all rows from %s", qPrintable(focusTableName) );
	}

	QString queryText =
		"INSERT INTO " + focusTableName +
		" SELECT "
		+ ociOrderedHint +
		"focus_id FROM "
		+ resourceTableName + " t, focus_has_resource_name fhrn "
		"WHERE t.name = fhrn.resource_name "
		"GROUP BY fhrn.focus_id";// HAVING COUNT(resource_name) = "
		   //+ QString::number( typeCount );

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to get list of foci" );
		return -1;
	}

	// Now count the performance results with these foci
	//queryText = "SELECT COUNT(prhf.performance_result_id) FROM ";
	queryText = "SELECT COUNT(distinct(prhf.performance_result_id)) FROM ";

	// If the metrics table is being used, add it to the query
	if( resultsUsingMetrics > 0  or !labels.isEmpty()) {
                if(resultsUsingMetrics > 0)
		   queryText += metricTableName + " m, ";
                queryText += " performance_result pr, ";
	}

	queryText +=
		"performance_result_has_focus prhf , "
		+ focusTableName + "  foci "
		"WHERE prhf.focus_id = foci.focus_id ";
	if( resultsUsingMetrics > 0  or !labels.isEmpty()) {
		queryText += 
			"AND pr.id = prhf.performance_result_id ";
                if(resultsUsingMetrics > 0)
			queryText += "AND pr.metric_id = m.id";
	}

        if (!labels.isEmpty()){
           queryText += " AND (";
           bool first =true;
           for(QStringList::iterator it=labels.begin(); it!=labels.end(); ++it){
               queryText += QString(first ? "" : " OR ") + "pr.label='" + (*it) + "' ";
               first  = false;
           }
           queryText += ")";
        }

	//printf( "DataAccess::getResultCount #2 query:\n%s\n", queryText.latin1() );

	return queryForInt( queryText );
}

// I don't believe this one is being used now
void DataAccess::getResults( QStringList resources, QString metricIds, QString filter )
{
	if( resources.count() == 0 && metricIds.isEmpty() ) {
		QMessageBox::information( NULL, "Empty request",
				"No parameters were listed in your request.  "
				"Choose some parameters from the Resources "
				"lists, add them to the Selected Parameters, "
				"and try again.", QMessageBox::Ok );
		return;
	}

#if 0
	// This version of the query works but is somewhat slower
	// (in limited testing) than the other version.  However,
	// this form, using subqueries, is faster than the version
	// with extra joins for getting only the number of results,
	// so we didn't change getResultCount
	QString queryText = 
	       	"SELECT pr.id result_id, pr.start_time start_time, "
		"pr.end_time end_time, "
		"pr.value value, pr.units units, riA.name metric, "
		"riB.name tool, riC.name application_name "
		"FROM performance_result pr,performance_result_has_focus prhf, "
		"resource_item riA, resource_item riB, resource_item riC "
		"WHERE pr.metric_id = riA.id "
		"AND pr.performance_tool_id = riB.id "
		"AND pr.application_id = riC.id "
		"AND pr.id = prhf.performance_result_id "
		"AND prfh.focus_id = fhr.focus_id "
		"AND prhf.focus_id IN "
		"( ( SELECT focus_id FROM focus_has_resource "
		"WHERE resource_id IN (" + resources.first() + ") ) ";
	// Start from the second item in the list, since we've
	// already seen the first one.
	QStringList::ConstIterator rit = resources.begin();
	for( ++rit; rit != resources.end(); ++rit ) {
		queryText += "INTERSECT ( SELECT focus_id FROM "
			"focus_has_resource WHERE resource_id IN "
			"( " + *rit + ") ) ";
	}

	queryText += ")";
#endif
#ifdef USE_OLD_TABLES
	QString queryText =
	       	"SELECT pr.id AS result_id, pr.start_time AS start_time, "
		"pr.end_time AS end_time, "
		"pr.value AS value, pr.units AS units, riA.name AS metric, "
		"riB.name AS tool, riC.name AS application_name "
		"FROM performance_result pr, "
		"resource_item riA, resource_item riB, resource_item riC ";
#ifndef USE_GROUP_BY
	// Add a join on focus_has_resource for each resource
	unsigned i;
	for( i = 0; i < resources.count(); ++i ) {
		queryText += ", focus_has_resource fhr" + QString::number( i )
			+ " ";
	}
#endif

	// Now some more of the query...
	queryText +=
		"WHERE pr.metric_id = riA.id "
		"AND pr.performance_tool_id = riB.id "
		"AND pr.application_id = riC.id ";

	// See if we're selecting on metric ids
	if( ! metricIds.isEmpty() ) {
		queryText += "AND pr.metric_id IN (" + metricIds + ") ";
	}
	
#ifdef USE_GROUP_BY
	// Get the set of matching foci and the corresponding results
	queryText +=
		"AND pr.focus_id IN "
		"( SELECT focus_id FROM focus_has_resource "
		"  WHERE resource_id IN ( " + resources.join(",") + ") "
		"  GROUP BY focus_id "
		"  HAVING COUNT(resource_id) = "
		+ QString::number( resources.count() ) + ")";
#else
	// Now the join condition for each resource
	QStringList::ConstIterator rit;
	for( i = 0, rit = resources.begin(); rit != resources.end();
			++rit, ++i ) {
		queryText += "AND pr.focus_id = fhr" + QString::number(i)
			+ ".focus_id AND fhr" + QString::number(i)
			+ ".resource_id IN (" + *rit + ") ";
	}
#endif
#else
/* the original query before table changes for combined performance results */
/*	QString queryText =
	       	"SELECT pr.id AS result_id, pr.start_time AS start_time, "
		"pr.end_time AS end_time, "
		"pr.value AS value, pr.units AS units, riA.name AS metric, "
		"riB.name AS tool, riC.name AS application_name "
		"FROM performance_result pr, "
		"performance_result_has_focus prhf, "
		"resource_item riA, resource_item riB, resource_item riC "
		"WHERE pr.metric_id = riA.id "
		"AND pr.performance_tool_id = riB.id "
		"AND pr.application_id = riC.id "
		"AND pr.id = prhf.performance_result_id "
		"AND prhf.focus_id IN "
		"( SELECT "
		+ ociOrderedHint +
		" focus_id FROM "
		+ resourceTableName + " t, focus_has_resource_name fhrn "
		"  WHERE t.name = fhrn.resource_name "
		"  GROUP BY fhrn.focus_id HAVING COUNT(resource_name) = "
		   + QString::number( resources.count() ) + ")";
*/
	QString queryText =
	       	"SELECT pr.id AS result_id, pr.start_time AS start_time, "
		"pr.end_time AS end_time, "
		"pr.value AS value, pr.units AS units, riA.name AS metric "
		"FROM performance_result pr, "
		"performance_result_has_focus prhf, "
		"resource_item riA "
		"WHERE pr.metric_id = riA.id "
		"AND pr.id = prhf.performance_result_id "
		"AND prhf.focus_id IN "
		"( SELECT "
		+ ociOrderedHint +
		" focus_id FROM "
		+ resourceTableName + " t, focus_has_resource_name fhrn "
		"  WHERE t.name = fhrn.resource_name "
		"  GROUP BY fhrn.focus_id HAVING COUNT(resource_name) = "
		   + QString::number( resources.count() ) + ")";
#endif


	if( ! filter.isEmpty() ) {
		queryText += " AND " + filter;
	}

	//printf( "DataAccess::getResults query:\n%s\n", queryText.latin1() );
	
	fprintf( stderr, "submitting query %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );

	Q3SqlSelectCursor cursor( queryText );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to get performance results "
			+ curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				Qt::NoButton );
	   fprintf( stderr, "query error: %s\n",message.latin1());
		return;
	}

	fprintf( stderr, "query completed %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );
	emit resultsReady( cursor );
}
// this is the one that's being  used now...
void DataAccess::getResults( int typeCount, QString /*metricIds*/, QString filter, QStringList labels)
{
	//if( typeCount == 0 && resultsUsingMetrics <= 0 ) {
	if( typeCount == 0 && resultsUsingMetrics <= 0 && labels.isEmpty()) {
		QMessageBox::information( NULL, "Empty request",
				"No parameters were listed in your request.  "
				"Choose some parameters from the Resources "
				"lists, add them to the Selected Parameters, "
				"and try again.", QMessageBox::Ok );
		return;
	}

	// Clear out the results table
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( "DELETE FROM " + resultTableName ) ) {
		qWarning( "Failed to delete all rows from %s", qPrintable(resultTableName) );
	}

	// Get results in the result table
        /* the original query before changes for combined performance results */
	/*QString queryText =
		"INSERT INTO " + resultTableName +
		"(result_id, start_time, end_time, value, units, metric, "
		"tool, application) "
	       	"SELECT pr.id, pr.start_time, pr.end_time, "
		"pr.value, pr.units, riA.name, riB.name, riC.name "
	       	"SELECT pr.id, NULL, NULL, "
		"pr.value, pr.units, pr.metric_id, pr.performance_tool_id, "
		"pr.application_id "
		"FROM performance_result pr, resource_item riA, "
		"resource_item riB, resource_item riC ";
        */
	QString queryText =
		"INSERT INTO " + resultTableName +
//S sharma -- made changes to add 'chk' column to GUI for showing High, Low, Expected and Unknown values of performance result
//		"(saved, result_id, start_time, end_time, value, units, metric, label, combined) "
		"(saved, result_id, start_time, end_time, value, chk, units, metric, label, combined) "		
	       	//"SELECT pr.id, pr.start_time, pr.end_time, "
	       	"SELECT 1, pr.id, pr.start_time, pr.end_time, "
//		"pr.value, pr.units, riA.name, pr.label, pr.combined "
		"pr.value, pr.chk, pr.units, riA.name, pr.label, pr.combined "
		"FROM performance_result pr, resource_item riA ";
	if( typeCount > 0 ) {
		queryText += ", performance_result_has_focus prhf, "
			+ focusTableName + " foci ";
	}

	// Select on metrics if any were specified
	if( resultsUsingMetrics > 0 ) {
		queryText += ", " + metricTableName + " m ";
	}

	int wheredone = 0;

	if( typeCount > 0 ) {
		queryText +=
			"WHERE pr.id = prhf.performance_result_id "
			"AND prhf.focus_id = foci.focus_id "
			"AND prhf.focus_type = 'primary' ";
		++wheredone;
	}

	// Specify the join on the metrics table
	if( resultsUsingMetrics > 0 ) {
		queryText +=
			QString( wheredone ? "AND " : "WHERE " ) +
			"pr.metric_id = m.id ";
		++wheredone;
	}
        /* original query before changes for combined performance results */
	/*queryText += "AND riA.id = pr.metric_id "
		     "AND riB.id = pr.performance_tool_id "
		     "AND riC.id = pr.application_id ";
        */
	//queryText += "AND riA.id = pr.metric_id ";
	queryText += QString(wheredone? "AND " : "WHERE ") + "riA.id = pr.metric_id ";
        ++wheredone;

	if( ! filter.isEmpty() ) {
		queryText += " AND " + filter;
	}

        bool first = true;
        if (!labels.isEmpty())
            queryText += " AND (";
        for (QStringList::iterator it=labels.begin(); it != labels.end(); ++it){
            queryText += QString( first ? " " : "OR ") + "pr.label='" + (*it) + "' ";
            first = false;
        }
        if (!labels.isEmpty())
           queryText += ")";

	//printf( "DataAccess::getResults #2 query:\n%s\n", queryText.latin1() );

	fprintf( stderr, "submitting query %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );

	// Submit the query to get the result list
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message = "Failed to get performance results" 
			+ curDb.lastError().text() + "\nQuery: " + queryText;
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
	   fprintf( stderr, "query error: %s\n",message.latin1());
		return;
	}

	fprintf( stderr, "result table populated %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );

	// Read in the results table
	Q3SqlSelectCursor cursor( "SELECT * FROM " + resultTableName );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to read results table:" 
			+ curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return;
	}

	fprintf( stderr, "query completed %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );
	emit resultsReady( cursor );
}

perfResultList * DataAccess::getResultsForCombining(int typeCount, QString metricIds, QStringList labels){
	// returns a list of performance results for combining 
	// gets the needed information about the performance results from the 
	// performance result table for combining
	// this method is used when you combine performance results from the query window,
	// based on resource selection, types, labels
    perfResultList * perfReses = new perfResultList();
	if( typeCount == 0 && resultsUsingMetrics <= 0 && labels.isEmpty()) {
		QMessageBox::information( NULL, "Empty request",
	    	"No parameters were listed in your request.  "
	        "Choose some parameters from the Resources "
	        "lists, add them to the Selected Parameters, "
	        "and try again.", QMessageBox::Ok );
		return perfReses;
	}
	QString queryText = 
		"SELECT pr.id, pr.value, riA.name "
		"FROM performance_result pr, resource_item riA ";
	if( typeCount > 0 ) {
		queryText += ", performance_result_has_focus prhf, "
	    	+ focusTableName + " foci ";
	}

	// Select on metrics if any were specified
	if( resultsUsingMetrics > 0 ) {
	        queryText += ", " + metricTableName + " m ";
	}

	int wheredone = 0;

	if( typeCount > 0 ) {
		queryText +=
	    	"WHERE pr.id = prhf.performance_result_id "
	        "AND prhf.focus_id = foci.focus_id "
	        "AND prhf.focus_type = 'primary' ";
		++wheredone;
	}

	// Specify the join on the metrics table
	if( resultsUsingMetrics > 0 ) {
		queryText +=
	    	QString( wheredone ? "AND " : "WHERE " ) +
	        "pr.metric_id = m.id ";
		++wheredone;
	}
	queryText += QString(wheredone? "AND " : "WHERE ") + "riA.id = pr.metric_id ";
	++wheredone;
	bool first = true;
	if (!labels.isEmpty()){
	    queryText += " AND (";
	    QStringList::iterator it;
	    for (it=labels.begin(); it != labels.end(); ++it){
	        queryText += QString(first ? " ":"OR ") + "pr.label='" 
	               + (*it) + "' ";
	        first = false;
	    }
	    queryText += ")";
	}

	//printf( "DataAccess::getResultsForCombining query:\n%s\n", queryText.latin1() );

	fprintf( stderr, "submitting query %s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );

	// Submit the query to get the result list
	//debug
	fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

       // Bhagya Y:
       query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		QString message = "Failed to get performance results"
	    	+ curDb.lastError().text() + "\nQuery: " + queryText;
	    QMessageBox::warning( NULL, "Data Access Error",
	    	message, QMessageBox::Ok, QMessageBox::NoButton );
	   fprintf( stderr, "query error: %s\n",message.latin1());
       return NULL;
	}

	fprintf( stderr, "got results for combining%s\n",
		QTime::currentTime().toString("hh:mm:ss.zzz").latin1() );

	while(query.next()){
	   perfResult * pr = new perfResult();
	   pr->setResultId(query.value(0).toInt());
	   pr->setValue(query.value(1).toDouble());
	   pr->setMetric(query.value(2).toString());
	   perfReses->append(*pr);
    
	}
	fprintf(stderr, "got %d results for combining\n", perfReses->size());

	return perfReses;

}

bool DataAccess::addCombinedResultToDataSheet(perfResult * pr){
    //takes a performance result and adds it to a data sheet.
    //right now there is only one data sheet, so it adds it to that one
    //it updates the resultId field of the performance result if the result
    //has not already been saved to the database
    //returns true on success and false on failure

    QString queryText;
    int resId = -1;
    // if the result is not saved, then we will get a result id for it anyway, because otherwise we can't save it to the temp table
    if (!pr->isSaved()){
       QString driver = curDb.driverName();
       if( driver == "QOCI8" ) {
           queryText = "select seq_performance_result.nextval from dual";
       }
       else if ( driver == "QPSQL7" || driver == "QPSQL") {
			// smithm 2008-7-2
			// Updated so that queryText is the same for the QPSQL7 and
			// QPSQL driver.
           queryText = "select nextval('seq_performance_result')";
       }
       else if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
			QString updateText = "UPDATE sequence SET prev_value = @ri_value := prev_value + 1 where name = 'seq_resource_item'";
			QSqlQuery updateQuery(updateText);
			queryText = "SELECT @ri_value";
       }
       else{
            QString msg = "Can't add performance result because using an unsupported database type for this function: savePerformanceResult";
            QMessageBox::information(NULL, "Unknown database", msg);
            return false;
       }
   
       // Bhagya Y:
       //QSqlQuery query(queryText);
       QSqlQuery query;

       // Bhagya Y:
       query.setForwardOnly( true );	// optimize for simple traversal

       // Bhagya Y:
       query.exec( queryText );

       if (query.next()){
           resId = query.value(0).toInt();
       }
       if (resId == -1){
          QString msg = "Could not add performance result because could not get a new performance result id from the database.";
          QMessageBox::information(NULL,"Unknown database error",msg);
          return false;
       }
       fprintf(stderr, "in data access setting pr.resid:%d\n", resId);
       pr->setResultId(resId);
    }
    else{
       resId = pr->getResultId();
       if (resId == -1){
          QString msg = "Could not add performance result because perf result has invalid result_id.";
          QMessageBox::information(NULL,"Unknown error",msg);
          return false;
       }
    }


    queryText = "insert into " + resultTableName + " (saved, result_id, metric, value, start_time, end_time, units, label, combined) values (" + QString(pr->isSaved()? "1": "0") + "," +  QString::number(resId) + ",'" + pr->getMetric() + "'," + QString::number(pr->getValue(),'f',100) + "," ;
    if (pr->getStartTime() == QString::null)
        queryText += QString("''") + ",";
    else
        queryText += "'" + pr->getStartTime() + "',";
    if (pr->getEndTime() == QString::null)
        queryText += QString("''") + ",";
    else
        queryText += "'" + pr->getEndTime() + "',";
    if (pr->getUnits() == QString::null)
        queryText += QString("''") + ",";
    else
       queryText += "'" + pr->getUnits() + "',";
    if (pr->getLabel() == QString::null)
        queryText += QString("''") + ",";
    else
       queryText += "'" + pr->getLabel() + "',";
    queryText +=  "1)";  //is  a combined result

 
    fprintf(stderr, "add to data sheet query: %s\n", queryText.latin1());
    QSqlQuery query;

     // Bhagya Y:
     query.setForwardOnly( true );	// optimize for simple traversal

    if (!query.exec(queryText)){
       QMessageBox::information(NULL, "Error", "Add to data sheet failed. Error:" + query.lastError().text());
       return false;
    }
    // Read in the results table
    Q3SqlSelectCursor cursor( "SELECT * FROM " + resultTableName );
              cursor.setForwardOnly( true );
    if( ! cursor.select() ) {
            QString message = "Failed to read results table:"
                    + curDb.lastError().text() + cursor.lastQuery();
            QMessageBox::warning( NULL, "Data Access Error",
                            message, QMessageBox::Ok, QMessageBox::NoButton );
                return false;
    }
    emit resultsReady( cursor );
    return true;
    
}

bool DataAccess::removeResultFromSheet(perfResult * pr, int sheet){
    //this removes a result from a data sheet. since there is only one sheet now, it 
    //removes it from that one
    //the result is removed from the temporary table that has the data for this sheet
    
    int resId = pr->getResultId(); 
    fprintf(stderr, "removing result: %d\n", resId);
    QString queryText = "delete from " + resultTableName + " where result_id=" + QString::number(resId);
    QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

    if(!query.exec(queryText)){
      QMessageBox::information(NULL, "Unknown error", "Unable to remove result from data sheet: " + queryText);
      return false;
    }
    // Read in the results table
    Q3SqlSelectCursor cursor( "SELECT * FROM " + resultTableName );
              cursor.setForwardOnly( true );
    if( ! cursor.select() ) {
            QString message = "Failed to read results table:"
                    + curDb.lastError().text() + cursor.lastQuery();
            QMessageBox::warning( NULL, "Data Access Error",
                            message, QMessageBox::Ok, Qt::NoButton );
                return false;
    }
    emit resultsReady( cursor );
    return true;
}


// Not sure, but I don't think this is used currently
QStringList DataAccess::compareExecutions( QStringList eids )
{
	// Find all the resource types associated with
	// these executions for which there is more than one
	// resource name associated with a given type.
	
	QString eidList = eids.join(",");

	QString queryText = "SELECT type FROM resource_item "
		"WHERE id IN "
		"(SELECT DISTINCT rid FROM execution_has_resource "
			"WHERE eid in (" + eidList + ")) "
		"GROUP BY type HAVING COUNT( DISTINCT name ) > 1 ";

	return queryForStrings( queryText );
}

// Not used with new tables
QStringList DataAccess::comparePerformanceResults( QStringList prIds )
{
	// Find all the resource types associated with
	// these performance results for which there is more than one
	// resource name associated with a given type.
	
	QString idList = prIds.join(",");

	QString queryText = 
                "SELECT type FROM resource_item "
		"WHERE id IN "
		"(SELECT DISTINCT fhr.resource_id FROM focus_has_resource fhr, "
//			"performance_result_has_focus prhf "
//			"WHERE fhr.focus_id = prhf.focus_id "
//			"AND prhf.performance_result_id IN (" + idList + "))"
			"performance_result pr "
			"WHERE fhr.focus_id = pr.focus_id "
			"AND pr.id IN (" + idList + "))"
		"GROUP BY type HAVING COUNT( DISTINCT name ) > 1 ";
        fprintf(stderr, "executing comparePerformanceResults: %s\n", queryText.latin1());
	return queryForStrings( queryText );
}

QStringList DataAccess::comparePerformanceResults()
{
	// Find all the resource types associated with
	// the performance results in the results table for which there
	// is more than one resource name associated with a given type.
	QString queryText = "SELECT type FROM resource_item "
		"WHERE name IN "
		"(SELECT DISTINCT fhrn.resource_name "
			"FROM focus_has_resource_name fhrn, "
			"performance_result_has_focus prhf, "
			+ resultTableName + " r "
			"WHERE fhrn.focus_id = prhf.focus_id "
			"AND prhf.performance_result_id = r.result_id ) "
		"GROUP BY type HAVING COUNT( DISTINCT name ) > 1 ";
        fprintf(stderr, "executing comparePerformanceResults22: %s\n", queryText.latin1());
	return queryForStrings( queryText );
}

bool DataAccess::beginAdd()
{
	return curDb.transaction();
}

bool DataAccess::endAdd()
{
	return curDb.commit();
}

bool DataAccess::cancelAdd()
{
	return curDb.rollback();
}

int DataAccess::addAncestorsByName( QString type, QString name )
{
	QString queryText =
		"INSERT INTO " + addTableName + " "
		"SELECT ria.name FROM resource_item ria, resource_item rid, "
		"resource_has_descendant rhd "
		"WHERE rid.id = rhd.did AND ria.id = rhd.rid "
		"AND rid.name IN "
		" (SELECT name FROM resource_item WHERE type = '" + type + "' "
		"  AND name LIKE '%" + name + "')";

	QSqlQuery query;
 	//debug
       fprintf(stderr, "executing: %s\n", queryText.latin1());

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal


	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to add ancestors of %s", qPrintable(name)  );
		return -1;
	}

	// See how many results this would select
	int newItems = getResultCountSingle( addTableName );

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + resourceTableName + " "
		"SELECT * FROM " + addTableName;
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());

	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add ancestors of type \"" + type + "\"";
		if( ! name.isEmpty() )
			message += " and name \"" + name;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return -1;
	}
  
	query.exec( "DELETE FROM " + addTableName );
	return newItems;
}

int DataAccess::addDescendantsByName( QString type, QString name )
{
	QString queryText =
		"INSERT INTO " + addTableName + " "
		"SELECT rid.name FROM resource_item rid, resource_item ria, "
		"resource_has_ancestor rha "
		"WHERE ria.id = rha.aid AND rid.id = rha.rid "
		"AND ria.name IN "
		" (SELECT name FROM resource_item WHERE type = '" + type + "' "
		"  AND name LIKE '%" + name + "')";

	// fputs( queryText.latin1(), stderr );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to add descendants of %s", qPrintable(name)  );
		return -1;
	}

	// See how many results this would select
	int newItems = getResultCountSingle( addTableName );

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + resourceTableName + " "
		"SELECT * FROM " + addTableName;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add resources of type \"" + type + "\"";
		if( ! name.isEmpty() )
			message += " and name \"" + name;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return -1;
	}

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	query.exec( "DELETE FROM " + addTableName );

	return newItems;
}

int DataAccess::addAncestorsByAttribute( QString type, QString attr, QString value )
{
	QString queryText =
		"INSERT INTO " + addTableName + " "
		"SELECT ria.name FROM resource_item ria, resource_item rid, "
		"resource_has_descendant rhd "
		"WHERE rid.id = rhd.did AND ria.id = rhd.rid "
		"AND rid.name IN "
		" (SELECT ri.name FROM resource_item ri, resource_attribute ra "
		"  WHERE ri.type = '" + type + "' "
		"  AND ra.name = '" + attr + "' "
		"  AND ra.value = '" + value + "' "
		"  AND ra.resource_id = ri.id )";

    //debug
    fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to add ancestors of %s %s", qPrintable(attr), 
                                qPrintable(value)  );
		return -1;
	}

	// See how many results this would select
	int newItems = getResultCountSingle( addTableName );

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + resourceTableName + " "
		"SELECT * FROM " + addTableName;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add resources of type \"" + type + "\""
			" with " + attr + " = " + value;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return -1;
	}

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	query.exec( "DELETE FROM " + addTableName );

	return newItems;
}

int DataAccess::addDescendantsByAttribute( QString type, QString attr, QString value )
{
	QString queryText =
		"INSERT INTO " + addTableName + " "
		"SELECT rid.name FROM resource_item rid, resource_item ria, "
		"resource_has_ancestor rha "
		"WHERE ria.id = rha.aid AND rid.id = rha.rid "
		"AND ria.name IN "
		" (SELECT ri.name FROM resource_item ri, resource_attribute ra "
		"  WHERE ri.type = '" + type + "' "
		"  AND ra.name = '" + attr + "' "
		"  AND ra.value = '" + value + "' "
		"  AND ra.resource_id = ri.id )";

	// fputs( queryText.latin1(), stderr );
    //debug
    fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to add descendants of %s %s", qPrintable(attr),
                                qPrintable(value)  );
		return -1;
	}

	// See how many results this would select
	int newItems = getResultCountSingle( addTableName );

	// Now add the new items to the full list
	queryText =
		"INSERT INTO " + resourceTableName + " "
		"SELECT * FROM " + addTableName;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		QString message =
			"Failed to add descendants of type \"" + type + "\""
			" with " + attr + " = " + value;
		message += ".  Possibly these duplicate resources already "
			"in the list. (See command line for error details.)";
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return -1;
	}

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	query.exec( "DELETE FROM " + addTableName );

	return newItems;
}

void DataAccess::deleteAncestorsByName( QString type, QString name )
{
	QString queryText =
		"DELETE FROM " + resourceTableName + " WHERE name IN "
		"( SELECT ria.name FROM resource_item ria, resource_item rid, "
		"  resource_has_descendant rhd "
		"  WHERE rid.id = rhd.did AND ria.id = rhd.rid "
		"  AND rid.name IN "
		"  (SELECT name FROM resource_item WHERE type = '" + type + "' "
		"   AND name LIKE '%" + name + "') )";

	// fputs( queryText.latin1(), stderr );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete ancestors of %s", qPrintable(name)  );
	}
}

void DataAccess::deleteDescendantsByName( QString type, QString name )
{
	QString queryText =
		"DELETE FROM " + resourceTableName + " WHERE name IN "
		" (SELECT rid.name FROM resource_item rid, resource_item ria, "
		"  resource_has_ancestor rha "
		"  WHERE ria.id = rha.aid AND rid.id = rha.rid "
		"  AND ria.name IN "
		"   (SELECT name FROM resource_item "
		"    WHERE type = '" + type + "' "
		"    AND name LIKE '%" + name + "') )";

	// fputs( queryText.latin1(), stderr );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete descendants of %s", qPrintable(name)  );
	}
}

void DataAccess::deleteAncestorsByAttribute( QString type, QString attr, QString value )
{
	QString queryText =
		"DELETE FROM " + resourceTableName + " WHERE name IN "
		" (SELECT ria.name FROM resource_item ria, resource_item rid, "
		"  resource_has_descendant rhd "
		"  WHERE rid.id = rhd.did AND ria.id = rhd.rid "
		"  AND rid.name IN "
		"   (SELECT ri.name FROM resource_item ri, "
		"    resource_attribute ra "
		"    WHERE ri.type = '" + type + "' "
		"    AND ra.name = '" + attr + "' "
		"    AND ra.value = '" + value + "' "
		"    AND ra.resource_id = ri.id ) )";

	// fputs( queryText.latin1(), stderr );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete ancestors of %s %s", qPrintable(attr),
                                qPrintable(value) );
	}
}

void DataAccess::deleteDescendantsByAttribute( QString type, QString attr, QString value )
{
	QString queryText =
		"DELETE FROM " + resourceTableName + " WHERE name IN "
		" (SELECT rid.name FROM resource_item rid, resource_item ria, "
		"  resource_has_ancestor rha "
		"  WHERE ria.id = rha.aid AND rid.id = rha.rid "
		"  AND ria.name IN "
		"   (SELECT ri.name FROM resource_item ri, "
		"    resource_attribute ra "
		"    WHERE ri.type = '" + type + "' "
		"    AND ra.name = '" + attr + "' "
		"    AND ra.value = '" + value + "' "
		"    AND ra.resource_id = ri.id ) )";

	// fputs( queryText.latin1(), stderr );
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete descendants of %s %s", qPrintable(attr),
                                qPrintable(value) );
	}
}

QString DataAccess::getAncestorIds( QString resIds )
{
//	QString queryText =
//			"SELECT aid FROM resource_has_ancestor "
//			"WHERE rid IN (" + resIds + ") UNION ";
	// The ancestor and descendant tables are not symmetric.  An
	// entry is made in a table only if rid is part of a some focus
	// in the database.  Since performance results are linked to foci,
	// we don't need to bother looking up resource ids that aren't
	// part of any focus.  Therefore, while querying both tables
	// might give us more results, querying only for rids gives
	// us just the most useful results.
	QString queryText = "SELECT rid FROM resource_has_descendant "
			"WHERE did IN (" + resIds + ")";

	return queryForStrings( queryText ).join(",");
}

QString DataAccess::getDescendantIds( QString resIds )
{
//	QString queryText =
//			"SELECT did FROM resource_has_descendant "
//			"WHERE rid IN (" + resIds + ") UNION ";

	// See the comment in getAncestorIds about why we don't
	// query resource_has_descendant here too.
	QString queryText = "SELECT rid FROM resource_has_ancestor "
			"WHERE aid IN (" + resIds + ")";

	return queryForStrings( queryText ).join(",");
}

// Not used with new tables
void DataAccess::getResultResources( QStringList prIds, QString resType )
{

	QString idList = prIds.join(",");
	// Get the resource items that match resType and that appear
	// in this focus or are ancestors of items that appear in the focus
	// The UNION operator gives us both cases; trying to form a
	// single query was difficult without using DISTINCT, and that
	// seemed to make things very slow.
#if 0
	// Replaced by newer version below that doesn't use prhf
	QString queryText =
		"SELECT prhf.performance_result_id, ri.name "
		"FROM performance_result_has_focus prhf, "
			"focus_has_resource fhr, resource_item ri "
		"WHERE prhf.performance_result_id IN (" + idList + ") "
		"AND prhf.focus_id = fhr.focus_id "
		"AND fhr.resource_id = ri.id  "
		"AND ri.type = '" + resType + "' "
		"UNION "
		"SELECT prhf.performance_result_id, ri.name "
		"FROM performance_result_has_focus prhf, "
			"focus_has_resource fhr, resource_item ri, "
			"resource_has_ancestor rha "
		"WHERE prhf.performance_result_id IN (" + idList + ") "
		"AND prhf.focus_id = fhr.focus_id "
		"AND fhr.resource_id = rha.rid AND rha.aid = ri.id "
		"AND ri.type = '" + resType + "' "
		;
#endif
	QString queryText =
		"SELECT pr.id, ri.name "
		"FROM performance_result pr, "
			"focus_has_resource fhr, resource_item ri "
		"WHERE pr.id IN (" + idList + ") "
		"AND pr.focus_id = fhr.focus_id "
		"AND fhr.resource_id = ri.id  "
		"AND ri.type = '" + resType + "' "
		"UNION "
		"SELECT pr.id, ri.name "
		"FROM performance_result pr, "
			"focus_has_resource fhr, resource_item ri, "
			"resource_has_ancestor rha "
		"WHERE pr.id IN (" + idList + ") "
		"AND pr.focus_id = fhr.focus_id "
		"AND fhr.resource_id = rha.rid AND rha.aid = ri.id "
		"AND ri.type = '" + resType + "' "
		;
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	Q3SqlSelectCursor cursor( queryText );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to get data for resource "
			+ resType + ": " + curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				Qt::NoButton );
		return;
	}

	emit resultDetailsReady( resType, cursor );
}

// Not used with new tables
void DataAccess::getResultAttributes( QStringList prIds, QString attrName )
{

	QString idList = prIds.join(",");
#if 0
	// Replaced by a version that doesn't use prhf
	QString queryText =
		"SELECT prhf.performance_result_id, ra.value "
		"FROM performance_result_has_focus prhf, "
			"focus_has_resource fhr, resource_attribute ra "
		"WHERE prhf.performance_result_id IN (" + idList + ") "
		"AND prhf.focus_id = fhr.focus_id "
		"AND fhr.resource_id = ra.resource_id " 
		"AND ra.name = '" + attrName + "' "
		"UNION "
		"SELECT prhf.performance_result_id, ra.value "
		"FROM performance_result_has_focus prhf, "
			"focus_has_resource fhr, resource_attribute ra, "
			"resource_has_ancestor rha "
		"WHERE prhf.performance_result_id IN (" + idList + ") "
		"AND prhf.focus_id = fhr.focus_id "
		"AND fhr.resource_id = rha.rid AND rha.aid = ra.resource_id "
		"AND ra.name = '" + attrName + "'";
#endif
	QString queryText =
		"SELECT pr.id, ra.value "
		"FROM performance_result pr, "
			"focus_has_resource fhr, resource_attribute ra "
		"WHERE pr.id IN (" + idList + ") "
		"AND pr.focus_id = fhr.focus_id "
		"AND fhr.resource_id = ra.resource_id " 
		"AND ra.name = '" + attrName + "' "
		"UNION "
		"SELECT pr.id, ra.value "
		"FROM performance_result pr, "
			"focus_has_resource fhr, resource_attribute ra, "
			"resource_has_ancestor rha "
		"WHERE pr.id IN (" + idList + ") "
		"AND pr.focus_id = fhr.focus_id "
		"AND fhr.resource_id = rha.rid AND rha.aid = ra.resource_id "
		"AND ra.name = '" + attrName + "'";

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	Q3SqlSelectCursor cursor( queryText );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to get data for attribute "
			+ attrName + ": " + curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				Qt::NoButton );
		return;
	}

	emit resultDetailsReady( attrName, cursor );
}

void DataAccess::getResultResources( QString resType )
{
	// smithm 2008-7-28
	// There is a bug in MySQL that prevents using a temp table
	// multiple times in a querry.  The solution used here is to
	// duplicate the temp table, use the original and duplicate
	// in the query, then drop the duplicate when done.
	QString queryText;
	QString dupTableName = resultTableName + "_dup";
	QString driver = curDb.driverName();
	if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		duplicateTable(resultTableName, dupTableName);
		queryText =
			"SELECT r.result_id, ri.name "
			"FROM " + resultTableName + " r, "
		       		"performance_result_has_focus prhf, "
				"focus_has_resource_name fhrn, resource_item ri "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhrn.focus_id "
			"AND fhrn.resource_name = ri.name "
			"AND ri.type = '" + resType + "' "
			"UNION "
			"SELECT r.result_id, ri.name "
			"FROM " + dupTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_item ri, "
				"resource_has_ancestor rha "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = rha.rid AND rha.aid = ri.id "
			"AND ri.type = '" + resType + "' "
			;
		
	} else {
		queryText =
			"SELECT r.result_id, ri.name "
			"FROM " + resultTableName + " r, "
		       		"performance_result_has_focus prhf, "
				"focus_has_resource_name fhrn, resource_item ri "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhrn.focus_id "
			"AND fhrn.resource_name = ri.name "
			"AND ri.type = '" + resType + "' "
			"UNION "
			"SELECT r.result_id, ri.name "
			"FROM " + resultTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_item ri, "
				"resource_has_ancestor rha "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = rha.rid AND rha.aid = ri.id "
			"AND ri.type = '" + resType + "' "
			;	
	}
	
    //debug
    fprintf(stderr, "executing: %s\n", queryText.latin1());
	Q3SqlSelectCursor cursor( queryText );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to get data for resource "
			+ resType + ": " + curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return;
	}

	// Drop the duplicate table
	if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		dropTempTable(dupTableName);
	}
	
	emit resultDetailsReady( resType, cursor );
}

void DataAccess::getResultAttributes( QString attrName )
{
	// smithm 2008-7-28
	// There is a bug in MySQL that prevents using a temp table
	// multiple times in a querry.  The solution used here is to
	// duplicate the temp table, use the original and duplicate
	// in the query, then drop the duplicate when done.
	QString queryText;
	QString driver = curDb.driverName();
	QString dupTableName = resultTableName + "_dup";
	if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		duplicateTable(resultTableName, dupTableName);
		queryText =
			"SELECT r.result_id, ra.value "
			"FROM " + resultTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_attribute ra "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = ra.resource_id " 
			"AND ra.name = '" + attrName + "' "
			"UNION "
			"SELECT r.result_id, ra.value "
			"FROM " + dupTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_attribute ra, "
				"resource_has_ancestor rha "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = rha.rid AND rha.aid = ra.resource_id "
			"AND ra.name = '" + attrName + "'";
	} else {
		queryText =
			"SELECT r.result_id, ra.value "
			"FROM " + resultTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_attribute ra "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = ra.resource_id " 
			"AND ra.name = '" + attrName + "' "
			"UNION "
			"SELECT r.result_id, ra.value "
			"FROM " + resultTableName + " r, "
				"performance_result_has_focus prhf, "
				"focus_has_resource fhr, resource_attribute ra, "
				"resource_has_ancestor rha "
			"WHERE prhf.performance_result_id = r.result_id "
			"AND prhf.focus_id = fhr.focus_id "
			"AND fhr.resource_id = rha.rid AND rha.aid = ra.resource_id "
			"AND ra.name = '" + attrName + "'";	
	}
	

    //debug
    fprintf(stderr, "executing: %s\n", queryText.latin1());
	Q3SqlSelectCursor cursor( queryText );
	cursor.setForwardOnly( true );
	if( ! cursor.select() ) {
		QString message = "Failed to get data for attribute "
			+ attrName + ": " + curDb.lastError().text()
			+ cursor.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
				message, QMessageBox::Ok,
				QMessageBox::NoButton );
		return;
	}

	// drop duplicate table
	if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		dropTempTable(dupTableName);
	}
	
	emit resultDetailsReady( attrName, cursor );
}

void DataAccess::createTempTable( QString& name, QString type )
{
	// The name must be unique; if a resource name appears in this
	// list twice, it will match the same rows in focus_has_resource_name
	// table twice, and that will cause the focus matching logic to
	// fail (since it counts matched rows for a given focus without
	// looking at the resource names).  Thus, we set name as a
	// primary key.
	QString queryText =
		"CREATE " + tempTableFlag + " TABLE "
		+ name + " (" + type + " PRIMARY KEY)"
		+ tempTableSuffix;

	QSqlQuery query;
    //debug
    fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to create temporary table %s", qPrintable(name) );
		name = QString();
	}

}

void DataAccess::deleteAllResources()
{
	QString queryText =
		"DELETE FROM " + resourceTableName;

	QSqlQuery query;

        // Bhagya Y:
	query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete all rows from %s", 
				qPrintable(resourceTableName) );
	}

	queryText = "DELETE FROM " + metricTableName;
        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete all rows from %s", 
                                qPrintable(metricTableName) );
	}
        resultsUsingMetrics = 0;
	
	queryText = "DELETE FROM " + focusTableName;

        //debug
        fprintf(stderr, "executing: %s\n", queryText.latin1());
	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to delete all rows from %s", 
                                qPrintable(metricTableName) );
	}
	
	// No need to clear the adds table; any function that populates
	// it should also clear it. 
}

QStringList DataAccess::getAllMetricNames(){
    //get all the metric names from the database for display in GUI lists
        QStringList metNames;
        QString queryText = "select distinct name from resource_item  where type='metric'";
	fprintf(stderr,"query to get metric names: %s\n", queryText.latin1());

        // Bhagya Y:
	//QSqlQuery query( queryText );
        QSqlQuery query;

        // Bhagya Y:
        query.setForwardOnly( true );	// optimize for simple traversal

        // Bhagya Y:
        query.exec( queryText );
	while (query.next()){
            QString name = query.value(0).toString();
            metNames.append(name);
	}
	return metNames;
}

QStringList DataAccess::getAllLabelNames(){
    //get all the label names from the database for display in GUI lists
        QStringList labelNames;
        QString queryText = "select distinct label from performance_result where label != ''";
        // Bhagya Y:
	//QSqlQuery query( queryText );
        QSqlQuery query;

        // Bhagya Y:
        query.setForwardOnly( true );	// optimize for simple traversal

        // Bhagya Y:
        query.exec( queryText );
	while (query.next()){
            QString name = query.value(0).toString();
            labelNames.append(name);
	}
	qSort(labelNames);
	return labelNames;

}

QStringList DataAccess::getAllUnitsNames(){
    //get all the units names from the database for display in GUI lists
        QStringList unitsNames;
        QString queryText = "select distinct units from performance_result  where units != ''";
        // Bhagya Y:
	//QSqlQuery query( queryText );
        QSqlQuery query;

        // Bhagya Y:
        query.setForwardOnly( true );	// optimize for simple traversal

        // Bhagya Y:
        query.exec( queryText );
	while (query.next()){
            QString name = query.value(0).toString();
            unitsNames.append(name);
	}
	return unitsNames;

}

Context DataAccess::getContextFromResultId(int resId){
    //returns a context for a given performance result id
    //a context is a list of resources and their types, in alphabetical order by type, 
    //then by resource name
    Context context ;
    int fid;
    QString queryText = "select focus_id from performance_result_has_focus where performance_result_id=";
    queryText += QString::number(resId) ;
    queryText += " and focus_type='primary'";
    fprintf(stderr,"context query 1: %s\n",queryText.latin1());
    QSqlQuery query;

     // Bhagya Y:
     query.setForwardOnly( true );	// optimize for simple traversal

     query.exec(queryText);

    if( query.next())
       fid = query.value(0).toInt();
    else{
       fprintf(stderr, "no value returned for fid...\n");
       return context;
    }
    if (fid == 0){
	QString msg = "This performance result does not have a context! perfResult id:" + resId;
       QMessageBox::information((QWidget*)this, "Invalid Performance Result?", msg);
       return context;
    }
    queryText = "select type,name from focus_has_resource_name inner join resource_item on resource_name=resource_item.name where focus_id=" + QString::number(fid);
    fprintf(stderr,"context query 2: %s\n",queryText.latin1());
    query.prepare(queryText);
    query.exec();
    while(query.next()){
        context.append(ResourceTypeAndName(query.value(0).toString(),query.value(1).toString()));
	fprintf(stderr,"adding type:%s, name:%s to context\n", query.value(0).toString().latin1(),query.value(1).toString().latin1());
    }
    
    qSort(context);
    return context;
}

ContextList DataAccess::getContextsFromResultIds(Q3ValueList<int> resIds){
    //given a list of result ids, return a list of contexts
    ContextList contexts;
    Q3ValueList<int>::iterator it;
    for (it = resIds.begin(); it != resIds.end(); ++it){
       Context context;
       fprintf(stderr,"calling with resid: %d\n",(*it));
       context = getContextFromResultId((*it));
       contexts.append(context);
    }

    return contexts;

}

Context DataAccess::createCombinedContext(ContextList contexts){
    //take a list of contexts and create a combined context from them 
    //a combined context is the union of all the resources in the contexts
    //in alphabetical order by type, then by resource name
   Context newContext;
   ContextList::iterator it;
   Context::iterator it2;
   for (it = contexts.begin(); it != contexts.end(); ++it){
      for (it2 = (*it).begin(); it2 != (*it).end(); ++it2){
         if (newContext.findIndex((*it2)) == -1){ //not found
           newContext.append((*it2));
         }
      }

   }
   qSort(newContext);
   //for (it2 = newContext.begin(); it2 != newContext.end(); ++it2){
    ////   fprintf(stderr, "%s, %s\n",(*it2).first.latin1(),(*it2).second.latin1());
   //}
   return newContext;
   
}

int DataAccess::findResourceByName(QString resName){
    // looks for resource in resource_item table by name
    // returns the resource id if found
    // returns -1 if not found
    int resId = -1;

    if (resName == QString::null)
	return -1;
    QString queryText = "select id from resource_item where name='" + resName + "'";
    // Bhagya Y:
    // QSqlQuery query(queryText);
    QSqlQuery query;

    // Bhagya Y:
    query.setForwardOnly( true );	// optimize for simple traversal

    // Bhagya Y:
    query.exec( queryText );
    if (query.next()){
       resId = query.value(0).toInt();
    }
    else{
      //not found
      return -1;
    }
    return resId;
}

int DataAccess::getFocusFrameworkId(QString type){
    //returns the focus framework id on success
    //returns -1 on failure
    int fid = -1;

    QString queryText = "select id from focus_framework where type_string='" + type + "'";
    // Bhagya Y:
    // QSqlQuery query(queryText);
    QSqlQuery query;

    // Bhagya Y:
    query.setForwardOnly( true );	// optimize for simple traversal

    // Bhagya Y:
    query.exec( queryText );
    if (query.next())
       fid = query.value(0).toInt();
    return fid;
}

int DataAccess::insertResource(QString resName, QString resType){
    // inserts a resource with name resName into the resource_item table
    // returns the new id on success
    // returns -1 on error
    //
    // if resName is a hierarchical name (has more than one / in the name) then
    // look for parent resource in resource_item table 
    // if the parent doesn't exist, that's an error
    // all resource names start with /, so look for / after first character
    int index = resName.find(PTRESDELIM,1);
    int parentId = 0;
    if (index != -1){  //this means there is more than one /, and a parent
	index = resName.findRev(PTRESDELIM); //find the last /, sep parent from child
	QString parentName = resName.remove(index,resName.length()-1);
	fprintf(stderr, "have parent named: %s\n",parentName.latin1());
        parentId = findResourceByName(parentName);
        if (parentId == -1){
	    QString msg = "Can't enter resource: " + resName + " because parent resource: " + parentName + " is not in the database.";
           QMessageBox::information(NULL,"Missing Resource",msg);
	   return -1;
	}	    
    }
    //get the focus framework id for the type
    int ffid = getFocusFrameworkId(resType);
    if (ffid == -1){
          QString msg = "Can't enter resource: " + resName + " because type: " + resType + " is not defined in the database.";
	  QMessageBox::information(NULL, "Missing Type", msg);
	  return -1;
    }
    QString queryText;
    QString driver = curDb.driverName();
    if( driver == "QOCI8" ) {
        queryText = "select seq_resource_item.nextval from dual";
    } 
    else if ( driver == "QPSQL7" || driver == "QPSQL" ) {
		// smithm 2008-7-2
		// Updated so that queryText is the same for the QPSQL7 and QPSQL driver.
	queryText = "select nextval('seq_resource_item')";
    } else if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
		QString updateText = "UPDATE sequence SET prev_value = @ri_value := prev_value + 1 where name = 'seq_resource_item'";
		QSqlQuery updateQuery(updateText);
		queryText = "SELECT @ri_value";
   }
    else{
         QString msg = "Can't enter resource: " + resName + " because using an unsupported database type for this function: insertResource";
	 QMessageBox::information(NULL, "Unknown database", msg);
	 return -1;
    }
    QSqlQuery query;

     // Bhagya Y:
     query.setForwardOnly( true );	// optimize for simple traversal

     query.exec( queryText );

    int resId = -1;
    if (query.next()){
       resId = query.value(0).toInt();
    }
    if (resId == -1){
         QString msg = "Can't enter resource: " + resName + " because couldn't get new resource id from the database.";
	 QMessageBox::information(NULL, "Unknown error", msg);
	 return -1;
    }
    if (parentId){
        queryText = "insert into resource_item (id, name, type, parent_id, focus_framework_id, ff) values (" + QString::number(resId) + ",'" + resName + "','" + resType + "'," + QString::number(parentId) + "," + QString::number(ffid) + "," + QString::number(1) + ")";
    }
    else{
        queryText = "insert into resource_item (id, name, type, focus_framework_id, ff) values (" + QString::number(resId) + ",'" + resName + "','" + resType + "'," + QString::number(ffid) + "," + QString::number(1) + ")";
    }
    query.prepare(queryText);
    if (!query.exec()){
		QString msg = "Entering of resource: " + resName + " to the database failed. The query was: " + queryText; 
	QMessageBox::information(NULL,"Unknown Error", msg);
	return -1;
    }

    return resId;

}

int DataAccess::findContextByName(Context c){
    //looks up a context using the focusname field of the focus table
    //returns focus id on success
    //returns -1 on failure
    QString fname ; 
    bool first = true;
    int contextid = -1;
    //build up the focus string, a comma separated list of resources
    for (Context::iterator it = c.begin(); it != c.end(); ++it){
	if (first)
	   first = false;
	else
	    fname += ",";
        fname += (*it).second;
    }
    QString queryText = "select id from focus where focusName = '" + fname + "'";
     // Bhagya Y:
    QSqlQuery query;

     // Bhagya Y:
     query.setForwardOnly( true );	// optimize for simple traversal

     // Bhagya Y:
     query.exec( queryText );
    if (query.next()){
	contextid = query.value(0).toInt();
    }
    fprintf(stderr,"in findContextByName, returning: %d\n",contextid);
    return contextid;

}

int DataAccess::createContext(Context c){
    //creates a new context
    //returns the context id on success
    //returns -1 on failure
    int contextId = -1;
    //first get the resource ids
    Q3ValueList<int> resIds;
    for (Context::iterator it = c.begin(); it != c.end(); ++it){
	int resId = findResourceByName((*it).second);
	if (resId == -1){
           QString msg = "Could not create context because could not find resource: " + (*it).second;
	   QMessageBox::information(NULL,"Missing resource",msg);
	   return -1;
	}
	resIds.append(resId);
    }
    contextId = findContextByName(c);
    if (contextId == -1){  //not found, need to create
        fprintf(stderr,"in createContext, c not found, creating\n");
	QString focusName ; 
	bool first = true;
        for (Context::iterator it = c.begin(); it != c.end(); ++it){
            if (first)
    	       first = false;
    	    else
	       focusName += ",";
            focusName += (*it).second;
        }
	fprintf(stderr,"in createContext focusname is: %s\n",focusName.latin1());
        QString queryText;
        QString driver = curDb.driverName();
        if( driver == "QOCI8" ) {
            queryText = "select seq_focus.nextval from dual";
        } else if ( driver == "QPSQL7" || driver == "QPSQL" ) {
			// smithm 2008-7-2
			// Updated so that queryText is the same for the QPSQL7 and
			// QPSQL driver.
            queryText = "select nextval('seq_focus')";
        } else if ( driver == "QMYSQL3" || driver == "QMYSQL" ) {
			QString updateText = "UPDATE sequence SET prev_value = @f_value := prev_value + 1 where name = 'seq_focus'";
			QSqlQuery updateQuery(updateText);
			queryText = "SELECT @f_value";
       } else{
             QString msg = "Can't enter context because using an unsupported database type for this function: createContext";
             QMessageBox::information(NULL, "Unknown database", msg);
             return -1;
        }
        //QSqlQuery query(queryText);
        // Bhagya Y:
        QSqlQuery query;

        // Bhagya Y:
        query.setForwardOnly( true );	// optimize for simple traversal

        // Bhagya Y:
        query.exec( queryText );
        if (query.next()){
           contextId = query.value(0).toInt();
        }
        if (contextId == -1){
             QString msg = "Can't enter context because could not get a new context id from the database.";
             QMessageBox::information(NULL, "Unknown Error", msg);
             return -1;
        }
        queryText = "insert into focus (id, focusname) values (" + QString::number(contextId) + ",'" + focusName + "')"; 
	fprintf(stderr, "executing query: %s\n", queryText.latin1());
	query.prepare(queryText);
	if (!query.exec()){
            QString msg = "Entering context to the database failed. The query was: " + queryText; 
	    QMessageBox::information(NULL,"Unknown Error", msg);
	    return -1;
	}
	//enter resources in focus_has_resource table
	for(Q3ValueList<int>::iterator it = resIds.begin(); it != resIds.end(); ++it){
            queryText = "insert into focus_has_resource (focus_id, resource_id) values (" + QString::number(contextId) + "," + QString::number((*it)) + ")";
	    query.prepare(queryText);
	    if (!query.exec()){
		QString msg = "Could not create context because failed to make entry in focus_has_resource for resource:" + QString::number((*it));
		QMessageBox::information(NULL,"Unknown database error",msg);
		return -1;
	    }
	}
	//enter resources in focus_has_resource_name table
        for (Context::iterator it = c.begin(); it != c.end(); ++it){
            queryText = "insert into focus_has_resource_name (focus_id, resource_name) values (" + QString::number(contextId) + ",'" + (*it).second + "')";
	    query.prepare(queryText);
	    if (!query.exec()){
		QString msg = "Could not create context because failed to make entry in focus_has_resource for resource:" + (*it).second;
		QMessageBox::information(NULL,"Unknown database error",msg);
		return -1;
	    }
	}
    }

    return contextId;
}

void DataAccess::resultSaved(int sheet, perfResult * pr){
    // a result that is already in a data sheet has been saved by an outside agent (another window, another sheet) and we need to update it's status in this sheet.
    // this slot handles this

    int resid = pr->getResultId();
    if (resid == -1){
       QMessageBox::information(NULL, "Bad Performance Result", "The performance result does not have a valid id.");
       return;
    }
    QString queryText = "update " + resultTableName + " set saved=1 where result_id=" + QString::number(resid);
    fprintf(stderr, "resultSaved query:%s\n", queryText.latin1());
    QSqlQuery query;

    // Bhagya Y:
    query.setForwardOnly( true );	// optimize for simple traversal

    if(!query.exec(queryText)){
        QMessageBox::information(NULL, "Unknown Error", "Failed to update 'saved' status for performance result.");
	return;
    }
    // Read in the results table to update the screen
    Q3SqlSelectCursor cursor( "SELECT * FROM " + resultTableName );
              cursor.setForwardOnly( true );
    if( ! cursor.select() ) {
            QString message = "Failed to read results table:"
                    + curDb.lastError().text() + cursor.lastQuery();
            QMessageBox::warning( NULL, "Data Access Error",
                            message, QMessageBox::Ok, QMessageBox::NoButton );
                return ;
    }
    emit resultsReady( cursor );
}

bool DataAccess::savePerformanceResult(perfResult * pr, bool combined){
    //saves a performance result to the database
    //returns true on success
    //returns false on failure

    QString queryText;
    QSqlQuery query;

    // Bhagya Y:
    query.setForwardOnly( true );	// optimize for simple traversal

    //a safety check. if it's  a combined result, check to make sure it's parent results
    //are already saved in the database before continuing. 
    if (combined){
        Q3ValueList<int> parentIds = pr->getParentResultIds();
        QString parentList = "(";
        Q3ValueList<int>::iterator it;
        bool first = true;
        for (it = parentIds.begin(); it != parentIds.end(); ++it){
            parentList += QString(first? "":",") + QString::number((*it));
	    first = false;
        }
        parentList  += ")";
        queryText = "select count(*) from performance_result where id in " + parentList;
        if(!query.exec(queryText)){
             QMessageBox::information(NULL, "Unknown database error", "Query was: " + queryText);
	     return false;
        }
        int count = -1;
        query.next();
        count = query.value(0).toInt();
        if (count != parentIds.size()){
            QMessageBox::information(NULL, "Performance Result Save Error", "Not all of the parent results of this combined result have been saved to the database. First save the parent results. Then try again.");
	    return false;
        }
    }
    
    //look up metric, if it's not in db, add it to db
    int metricId = findResourceByName(pr->getMetric());
    if (metricId == -1){  //not found
        metricId = insertResource(pr->getMetric(), "metric");
	if (metricId == -1)
	    return false;
    }
    //go through the context:
    //	does it already exist? if so use that one
    int contextId = findContextByName(pr->getContext()); 
    if (contextId == -1){  //not found, need to create
	contextId = createContext(pr->getContext());
	if (contextId == -1)
	    return false;
    }
    // make entry in performance_result table
    
    int resId ;
    resId = pr->getResultId();
    fprintf(stderr, "in save, I think my result id is: %d\n", pr->getResultId());
    if (resId == -1){
	//it doesn't already have a result id, so we will get one for it
	//why would a non-saved result already have an id? well, it's because we give it
	//one when it's added to a data sheet. If it has been added to a data sheet, and 
	//therefore already has an id, then we just use that one.
        QString driver = curDb.driverName();
        if( driver == "QOCI8" ) {
            queryText = "select seq_performance_result.nextval from dual";
        }
        else if ( driver == "QPSQL7" || "QPSQL" ) {
			// smithm 2008-7-2
			// Updated so that queryText is the same for the QPSQL7 and
			// QPSQL driver.
            queryText = "select nextval('seq_performance_result')";
        }
        else{
             QString msg = "Can't enter performance result because using an unsupported database type for this function: savePerformanceResult";
             QMessageBox::information(NULL, "Unknown database", msg);
             return -1;
        }
      
        query.exec(queryText);
        if (query.next()){
	    resId = query.value(0).toInt();
        }
        if (resId == -1){
           QString msg = "Could not enter performance result because could not get a new performance result id from the database.";
           QMessageBox::information(NULL,"Unknown database error",msg);
           return false;
        }
        pr->setResultId(resId);
    }
    queryText = "insert into performance_result (id, metric_id, value, start_time, end_time, units, focus_id, label, combined) values (" + QString::number(resId) + "," + QString::number(metricId) + "," + QString::number(pr->getValue(),'f',100) + "," ;

    if (pr->getStartTime() == QString::null)
	queryText += QString("''") + ",";
    else
	queryText += "'" + pr->getStartTime() + "',";
    if (pr->getEndTime() == QString::null)
	queryText += QString("''") + ",";
    else
	queryText += "'" + pr->getEndTime() + "',";
    if (pr->getUnits() == QString::null)
	queryText += QString("''") + ",";
    else
       queryText += "'" + pr->getUnits() + "',";
    queryText += QString::number(contextId) + ",";
    if (pr->getLabel() == QString::null)
	queryText += QString("''") + ",";
    else
       queryText += "'" + pr->getLabel() + "',";
    queryText += (combined ? QString::number(1) : QString::number(0)) + ")";
    fprintf(stderr, "entering performance result: %s\n", queryText.latin1());
    if (!query.exec(queryText)){
	 QString msg = "Entering performance result failed. The query was: " + queryText;
	 QMessageBox::information(NULL, "Performance Result Error", msg);
	 return false;
    }


    // add entry in performance_result_has_focus for context
    // 	TODO: add support for multiple foci
    queryText = "insert into performance_result_has_focus (performance_result_id, focus_id) values (" + QString::number(resId) + "," + QString::number(contextId) + ")";

    if (!query.exec(queryText)){
	 QString msg = "Entering focus for performance result failed. The query was: " + queryText;
	 QMessageBox::information(NULL, "Performance Result Error", msg);
	 //TODO need to implement some sort of transaction control so that if this query fails, we undo the previous queries...
    }
    if (combined){
    // add parent res ids to  combined_perf_result_has_member table
         Q3ValueList<int> pRIds = pr->getParentResultIds();
	 for (Q3ValueList<int>::iterator it = pRIds.begin(); it != pRIds.end(); ++it){
             //queryText = "insert into combined_perf_result_members (c_pr_id, pr_id) values (" + QString::number(resId) + "," + QString::number((*it)) + ")";
             queryText = "insert into combined_perf_result__gen_members (c_pr_id, pr_id) values (" + QString::number(resId) + "," + QString::number((*it)) + ")";
	     if(!query.exec(queryText)){
                QString msg = "Entering parent results for combined performance result failed. The query was: " + queryText;
		QMessageBox::information(NULL, "Performance Result Error", msg);
	        //TODO need to implement some sort of transaction control so that if this query fails, we undo the previous queries...
	     }
	 }
    }

    return true;
}


QStringList DataAccess::getResultLabels(){
    //return a list of the labels for performance results in the database

    QStringList labels;
    QString queryText = "select distinct label from performance_result";
    QSqlQuery query( curDb );

    // Bhagya Y:
    query.setForwardOnly( true );	// optimize for simple traversal

    query.exec(queryText);
    while(query.next()){
       QString label = query.value(0).toString();
       labels.append(label);
    }
    qSort(labels);
    return labels;
}

bool DataAccess::isConnected() const
{
	if (curDb.isOpen())
		return true;
	else
		return false;
}

void DataAccess::dropTempTable( QString& name )
{
	// If we failed to create it, so don't drop it
	if( name.isEmpty() ) return;

	QString queryText =
		"DROP TABLE " + name;
	QSqlQuery query;

       // Bhagya Y:
       query.setForwardOnly( true );	// optimize for simple traversal

	if( ! query.exec( queryText ) ) {
		qWarning( "Failed to drop temporary table %s", qPrintable(name) );
	}
	name = QString();
}

bool DataAccess::duplicateTable (QString orig, QString dup)
{
	QString queryText;
	QString driver = curDb.driverName();
	queryText = "CREATE TEMPORARY TABLE " + dup + " SELECT * FROM " + orig;
	QSqlQuery query;

       // Bhagya Y:
       query.setForwardOnly( true );	// optimize for simple traversal

	if (!query.exec(queryText)) {
		QString message = "Failed to duplicate "
			+ orig + ": " + query.lastError().text()
			+ query.lastQuery();
		QMessageBox::warning( NULL, "Data Access Error",
			message, QMessageBox::Ok,
			QMessageBox::NoButton );
		return false;
	}
	return true;
}

/****************************************************************************
COPYRIGHT AND LICENSE
 
Copyright (c) 2005, Regents of the University of California and
Portland State University.  Produced at the Lawrence Livermore
National Laboratory and Portland State University.
UCRL-CODE-2005-155998
All rights reserved.
 
Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:
 
* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in
the documentation and/or other materials provided with the
distribution.
* Neither the name of the University of California
or Portland State Univeristy nor the names of its contributors
may be used to endorse or promote products derived from this
software without specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

ACKNOWLEDGMENT

1. This notice is required to be provided under our contract with the U.S.
Department of Energy (DOE).  This work was produced at the University
of California, Lawrence Livermore National Laboratory under Contract
No. W-7405-ENG-48 with the DOE.

2. Neither the United States Government nor the University of California
nor any of their employees, makes any warranty, express or implied, or
assumes any liability or responsibility for the accuracy, completeness, or
usefulness of any information, apparatus, product, or process disclosed, or
represents that its use would not infringe privately-owned rights.

3.  Also, reference herein to any specific commercial products, process, or
services by trade name, trademark, manufacturer or otherwise does not
necessarily constitute or imply its endorsement, recommendation, or
favoring by the United States Government or the University of California.
The views and opinions of authors expressed herein do not necessarily
state or reflect those of the United States Government or the University of
California, and shall not be used for advertising or product endorsement
purposes. 
****************************************************************************/

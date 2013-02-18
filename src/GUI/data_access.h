//! \file data_access.h

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

#ifndef DATA_ACCESS_H
#define DATA_ACCESS_H

#include <qmap.h>
#include <qobject.h>
#include <qpair.h>
#include <q3sqlcursor.h>
#include <qsqldatabase.h>
#include <qstring.h>
#include <qstringlist.h>
#include <q3valuelist.h>
//Added by qt3to4:
#include <QSqlQuery>

#include "db_connection_dialog.h"
#include "selection_list_item.h"
#include "resource_type_and_name.h"
#include "perfResult.h"

//! Class to handle interactions with the database and its interface to the GUI.

//! Inherits QObject so that
//! it can use signals and slots, but it does no GUI
//! work itself.
class DataAccess : public QObject {
	Q_OBJECT
public:
	DataAccess( QObject * parent = 0, const char * name = 0 );
	~DataAccess();

	//! Requests from the database the resources that fit into the
	//! focus framework.  The results are parsed into a list of
	//! string lists called "chains."  Each chain contains an
	//! ordered list of related resource types, from the top of
	//! the hierarchy to the bottom.
	Q3ValueList<QStringList> getResourceTypes();
	//get the names of all the metrics in the db
	QStringList getAllMetricNames();
	//get the labels for performances results 
	QStringList getAllLabelNames();
	// get all the different units types for performance results
	QStringList getAllUnitsNames();
	//get the context for a performance result
	Context getContextFromResultId(int);
	//get contexts from db given result ids
	ContextList getContextsFromResultIds(Q3ValueList<int>);
	//create a combined context from a list of contexts
	Context createCombinedContext(ContextList);
	//save a performance result to the database
	bool savePerformanceResult(perfResult*,bool combined);
	//lookup a resource by its name
	int findResourceByName(QString);
	//insert a resource to the database
	int insertResource(QString name, QString type);
	//lookup the focus framework id and return it
	int getFocusFrameworkId(QString type);
	//look up a context by its full name
	int findContextByName(Context);
	//create a context
	int createContext(Context);
	//get a list of all the labels in use
        QStringList getResultLabels();

	//! Returns true if there is a valid database connection, false 
	//! if not.
	bool isConnected() const;
	// smithm 2006-8-25
	// Since curDb is now a smart pointer to a QSqlDatabase it can no longer
	// be compared with NULL.  Moved implementation to DataAccess.cpp.
	//{	return curDb != NULL; }
	
	// Creates a duplicate of the orig table and names it dup
	bool duplicateTable(QString orig, QString dup);
	
public slots:
	//! Pops up a dialog to get information to create a connection
	//! to the database, and then establishes that connection, if
	//! possible.  Returns true if the request succeeds or false if not
	bool setupDBConnection();

	//! Requests a list of resources of the \a resourceType that
	//! match \a filter (where an empty string matches all
	//! such resources).  Once the list is available, a signal
	//! is emitted with the data.
	void findResourcesByType( QString resourceType, QString filter,
			void * requester );

	//! Requests a list of resources that are children of
	//! the ids stored in \a resourceIdList, filtered by \a filter.
	//! Once the list is available, a signal is emitted with the data.
	void findResourcesByParent( QString resourceIdList,
			QString filter, SelectionListItem * parentListItem );

	//! Requests a list of resources that are children of
	//! \a baseName, whose type is \a parentType, filtered by \a filter.
	//! Once the list is available, a signal is emitted with the data.
	void findResourcesByParent( QString parentType, QString baseName,
			QString filter, SelectionListItem * parentListItem );

	//! Requests a list of attribute names that apply to resources
	//! of type \a resourceType, and that match \a filter. 
	//! Once the list is available, a signal is emitted with the data.
	void findAttributesByType( QString resourceType, QString filter,
			void * requester );

	//! Requests a list of attributes/value pairs that match the
	//! attribute name given in \a attribute and that match
	//! \a filter.  Once the list is available, a signal is emitted
	//! with the data.
	void findAttributesByName( QString attribute,
			QString filter, SelectionListItem * parentListItem );

	//! Requests the attribute/value pairs for a specified resource \a id.
	//! Once the data is available, this function emits a signal
	//! with the data. OBSOLETE?
	void findAttributesById( QString id, SelectionListItem * sli );

	//! Requests the attribute/value pairs for a specified resource \a name,
	//! which may be just the end of name, so beginning will be wildcarded.
	//! Once the data is available, this function emits a signal
	//! with the data in a map that's indexed by the full resource name.
	void findAttributesByResourceName( QString name,
			SelectionListItem * sli );

	//! Requests the resource type/name pairs for a specified execution
	//! resource \a id.  This function doesn't try to verify that \a id
	//! is indeed a valid resource id of type "execution".
	//! Once the data is available, this function emits a signal
	//! with the data.
	void findExecutionResourcesById( QString id, SelectionListItem * sli );

	//! Requests the resource type/name pairs for a specified execution
	//! resource \a name.  This function doesn't try to verify that
	//! \a name is indeed a valid resource of type "execution".
	//! Once the data is available, this function emits a signal
	//! with the data.
	void findExecutionResourcesByName( QString name,
			SelectionListItem * sli );

	//! Requests a list of ids (returned as a comma-separated list)
	//! of all resources of type \a type.
	QString findResourceIdsByType( QString type );

	//! Initialize adding resources to the database's internal temporary
	//! list.  This is equivalent to beginning a transaction.  Returns
	//! success or failure of operation.
	bool beginAdd();
	
	//! Finish adding resources to the database's internal temporary
	//! list.  This is equivalent to committing a transaction.  Returns
	//! success or failure of operation.
	bool endAdd();
	
	//! Undo adding resources to the database's internal temporary
	//! list.  This is equivalent to rolling back a transaction.  Returns
	//! success or failure of operation.
	bool cancelAdd();
	
	//! Add specified resource names to database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	int addResourcesByName( QString type, QString name );

	//! Add specified resource names to database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	int addResourcesByAttribute( QString type, QString attr,
			QString value );

	//! Add specified resource ancestors to database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	int addAncestorsByName( QString type, QString name );

	//! Add specified resource ancestors to database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	int addAncestorsByAttribute( QString type, QString attr,
			QString value );

	//! Add specified resource descendants to database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	int addDescendantsByName( QString type, QString name );

	//! Add specified resource descendants to database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	int addDescendantsByAttribute( QString type, QString attr,
			QString value );

	//! Delete specified resource names from database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	void deleteResourcesByName( QString type, QString name );

	//! Delete specified resource names from database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	void deleteResourcesByAttribute( QString type, QString attr,
			QString value );

	//! Delete specified resource ancestors to database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	void deleteAncestorsByName( QString type, QString name );

	//! Delete specified resource ancestors to database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	void deleteAncestorsByAttribute( QString type, QString attr,
			QString value );

	//! Delete specified resource descendants to database's temporary table,
	//! based on matching resources that end in \a name whose type
	//! is \a type.
	void deleteDescendantsByName( QString type, QString name );

	//! Delete specified resource descendants to database's temporary table
	//! by finding resources of type \a type with \a attr =
	//! \a value.
	void deleteDescendantsByAttribute( QString type, QString attr,
			QString value );

	//! Remove all entries from the temporary table
	void deleteAllResources();

	//! Finds the number of performance results associated with
	//! executions that have resources in all of the given resource lists.
	//! See getResults() for more information on the format of 
	//! \a resources.
	int getResultCount( QStringList resources,
			QString metricIds = QString() );

	//! This is the current version.  It relies on temporary
	//! tables in the database, which are populated by calls
	//! to addResources and addAncestors functions.  It also
	//! populates the list of foci selected by the current
	//! set of resources, so that getResults() doesn't have
	//! to compute this list again.  Therefore, this function
	//! must always be called for the current set of resources
	//! before getResults() is called.  \a typeCount is the number
	//! of separate resource types in the temporary table.  \a metricIds
	//! is currently ignored and needs to be removed once all this
	//! code is stable.
	int getResultCount( int typeCount,
			QString metricIds = QString(), QStringList labels =QStringList());

	//! Finds the number of performance results associated with
	//! all the foci that have a resource in \a table, which is
	//! assumed to exist in the database.  \a table should have
	//! items from only one resource hierarchy.
	int getResultCountSingle( QString table );

	//! Finds the number of performance results associated with
	//! the list of metrics in \a table, which is
	//! assumed to exist in the database.
	int getResultCountMetrics( QString table,QStringList labels=QStringList() );
   
        int getResultCountLabels(QStringList labels);

	//! Returns a list of resource ids (comma-separated values)
	//! that is the set of all ancestors of the resources listed
	//! in \a resIds.
	QString getAncestorIds( QString resIds );

	//! Returns a list of resource ids (comma-separated values)
	//! that is the set of all descendants of the resources listed
	//! in \a resIds.
	QString getDescendantIds( QString resIds );


	//! Look up performance results based on the listed resource
	//! ids.  \a resources is a list of strings, and each string
	//! is a comma-separated list of numeric resource ids.  This
	//! function finds results that correspond to (at least) one
	//! resource from each list of ids.  In other words, there is
	//! an implicit OR over each list and an AND across the lists.
	//! The resource ids can appear in any order in the list, and
	//! the lists themselves can appear in any order.
	//! \a filter is an additional SQL clause added as an AND
	//! at the end of the SELECT statement.  Probably not useful
	//! unless the user knows the schema in detail.  When results
	//! are found, this function emits a dataReady() signal with
	//! a QSqlCursor (set to forward traversal only) over the
	//! results.
	void getResults( QStringList resources, QString metricIds,
			QString filter);

	//! This is the current version.  It relies on temporary
	//! tables of metrics and foci created by calls to getResultCount()
	//! and the addResources... functions.  \a typeCount is the number
	//! of separate resource types in the temporary table.  \a metricIds
	//! is currently ignored and needs to be removed once all this
	//! code is stable.
	void getResults( int typeCount, QString metricIds,
			QString filter, QStringList labels);

	//for use from the query window. returns a list of performance results for combining
	//based on resource types, metrics and labels
        perfResultList * getResultsForCombining(int typeCount, QString metricIds, QStringList labels);

	//adds a combined result to a data sheet
        bool addCombinedResultToDataSheet(perfResult*);
	//removes a result from a data sheet
	bool removeResultFromSheet(perfResult*, int);
	//notify that the result was saved outside of this sheet
	void resultSaved(int sheet, perfResult *);

	//! Looks up the value of the resource of type \a resType for
	//! each performance result id in \a prIds.  Emits the signal
	//! resultDetailsReady() if data is successfully retrieved.
	void getResultResources( QStringList prIds, QString resType );

	//! Looks up the value of the resource of type \a resType for
	//! each performance result id in the internal result list.
	//! Emits resultDetailsReady() if data is successfully retrieved.
	void getResultResources( QString resType );

	//! Looks up the value of the attribute \a attrName for
	//! each performance result id in \a prIds.  Emits the signal
	//! resultDetailsReady() if data is successfully retrieved.
	void getResultAttributes( QStringList prIds, QString attrName );

	//! Looks up the value of the attribute \a attrName for
	//! each performance result id in the internal result list.
	//! Emits resultDetailsReady() if data is successfully retrieved.
	void getResultAttributes( QString attrName );

	//! Determine which resources have different values for a given list
	//! of execution ids.  Returns a list of resource types.
	QStringList compareExecutions( QStringList execIds );

	//! Determine which resources have different values for a given list
	//! of performance result ides.  Returns a list of resource types.
	QStringList comparePerformanceResults( QStringList prIds );

	//! Determine which resources have different values for a the
	//! results of the last query.  Returns a list of resource types.
	QStringList comparePerformanceResults();

signals:
	//! Emitted when a request to connect to the database has
	//! either succeeded or failed.
	void databaseConnected( bool );

	//! Emitted when a query has been completed.
	void dataReady( Q3SqlCursor& );

	//! Emitted when a request for attributes has been completed.  The
	//! requested type and a list of attribute names are sent, along
	//! with a pointer allowing the receiver to determine whether it's
	//! the object that initiated ther request.
	void foundAttributesByType( QString, QStringList, void * );

	//! Emitted when a request for resources has been completed.  The
	//! requested type and a map of resource names and corresponding
	//! id lists are sent, along with a pointer allowing the
	//! receiver to determine whether it's
	//! the object that initiated ther request.
	void foundResourcesByType( QString,
			QMap<QString,QPair<QString,QString> >, void * );

	void foundResourcesByType( QString,
			QMap<QString,int>, void * );

	//! Emitted when a request for attributes has been completed.  The
	//! requested type, a map of attribute values and corresponding
	//! lists of resource ids, and the requesting list item are sent.
	void foundAttributesByName( QString,
			QMap<QString,QPair<QString,QString> >,
			SelectionListItem * );

	void foundAttributesByName( QString, QStringList,
			SelectionListItem * );

	//! Emitted when a request for resources has been completed.  The
	//! type of the children, a map of resource names and their
	//! corresponding idlists, and the requesting list item are sent.
	void foundResourcesByParent( QString,
			QMap<QString,QPair<QString,QString> >,
			SelectionListItem * );

	void foundResourcesByParent( QString, QMap<QString,int>,
			SelectionListItem * );

	//! Emitted when a request for attributes has been completed.  The
	//! attribute/value pairs are sent in a list of string pairs.
	//! We don't expect duplication, so no QMap is needed. (OBSOLETE?)
	void foundAttributesById( QString, Q3ValueList<QPair<QString,QString> >,
			SelectionListItem * );

	//! Emitted when a request for attributes has been completed.  The
	//! attribute/value pairs are sent in a list of string pairs, and
	//! the lists are stored in a map indexed by the full resource name.
	void foundAttributesByResourceName( AttrListMap, SelectionListItem * );

	//! Emitted when a request for execution resources has been completed.
	//! The resource type/name pairs are sent in a list of string pairs.
	//! Duplicate types (with different names) are possible, and we
	//! don't want to merge them (as we do with resource ids), so we can't
	//! use a map here.
	void foundExecutionResources( Q3ValueList<QPair<QString,QString> >,
			SelectionListItem * );

	//! Emitted when a query for results has completed.  The cursor
	//! sent can be used to get the data.
	void resultsReady( Q3SqlCursor );

	//! Emitted when a query for the resource or attributes
	//! corresponding to a list of performance results is ready.
	//! Sends a QSqlCursor (forward access only) containing the
	//! data, with the first column containing the performance
	//! result id and the second column containing the resource name.
	//! The requested resource or attribute type is passed in the
	//! first parameter.
	void resultDetailsReady( QString, Q3SqlCursor );

protected:
	//! Internal function that sends the \a queryText to the
	//! database and returns a list of the resulting stings.
	//! The query should be a full select statement that returns
	//! data for exactly one field.
	QStringList queryForStrings( QString queryText );

	//! Internal function that sends the \a queryText to the
	//! database and returns a single integer result.  The
	//! query should be a full select statement that returns
	//! one row with one integer field.
	int queryForInt( QString queryText );

	//! Transform text of resource types returned from database
	//! into the form needed for the GUI.  Specifically, groups
	//! of related resources are assembled into string lists,
	//! from most general to most specific, and these lists are
	//! assembled into a value list, ordered alphabetically by
	//! the first name in each list.
	Q3ValueList<QStringList> parseResourceTypes(
			QStringList fullResourceTypes );

	//! Merge strings from a query so that a value appears only
	//! once and is followed by a list of corresponding resource
	//! ids.  \a query must be the result of a query that
	//! returns a string with the value in the first position
	//! and an id in the second position.  If \a truncate is true
	//! only the part of the value after the last / character
	//! (or all of the string if there is no /) will be evaluated
	//! and put in the map as a key.  The value consists of a QPair,
	//! with the first string containing a comma-separated list of
	//! ids and the second string containing a comma-separated list
	//! of full value names (regardless of \a truncate.)
	QMap<QString,QPair<QString,QString> > buildResultMap( QSqlQuery& query,
			bool truncate );

	//! Initialize database-specific customization strings
	void initDBCustomizations();

	QMap<QString,int> buildResultMap( QSqlQuery& query );

	typedef Q3ValueList<QStringList> FocusResourceSet;

	//! Create a table to hold intermediate lists of resource names
	void createTempTable( QString& tablename, QString type );

	//! Remove the temporary table
	void dropTempTable( QString& tablename );

	// smithm 2008-6-25
	// According to the Qt documenation QSqlDatabase is now a smart pointer.
	// So, it should be passed by value.
	// See: http://doc.trolltech.com/4.4/porting4.html#qsqldatabase
	//QSqlDatabase * curDb;
	QSqlDatabase curDb;

	QString resourceTableName;
	QString addTableName;
	QString focusTableName;
	QString metricTableName;
	QString metricAddTableName;
	QString resultTableName;

	// Customization strings for different database drivers
	// These are empty or set to a default value if the specified
	// DBMS is not in use, otherwise they are initialized in
	// initDBCustomizations.
	QString ociOrderedHint;
	QString ociTempTableHint;
	QString tempTableFlag;
	QString tempTableSuffix;

	// Keep track of how many results use the metrics table.
	// This helps us determine whether to include the metrics
	// table in a results query.
	int resultsUsingMetrics;
};
#endif

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

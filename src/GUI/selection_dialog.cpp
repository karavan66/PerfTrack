// selection_dialog.cpp
// John May, 28 October 2004
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <math.h>

#include <qapplication.h>
#include <qmessagebox.h>
#include <qtimer.h>
#include <q3frame.h>
#include <q3groupbox.h>
#include <qlineedit.h>
#include <q3ptrvector.h>
#include <qpushbutton.h>
#include <qsplitter.h>
#include <q3listbox.h>
#include <q3vbox.h>
//Added by qt3to4:
#include <QShowEvent>
#include <Q3ValueList>

#include "selection_dialog.h"
#include "data_access.h"
#include "resource_type_and_name.h"
#include "constraint_list_item.h"

// For cout
#include <iostream>

// Work around the fact that metric ids are not stored in the focus
//#define METRIC_HACK

// For buildFocusList
//QStringList SelectionDialog:: focusTypes;

#include "selection_dialog.moc"

SelectionDialog:: SelectionDialog( DataAccess * da,
		QWidget * parent, const char * name,
		bool modal, Qt::WFlags fl )
	: SelectionDialogBase( parent, name, modal, fl ), dataSource( da )
{
	initConnections();
	initSelectors();
        //QStringList labels = dataSource -> getResultLabels();
        QStringList labels = dataSource -> getAllLabelNames();
        labelListBox->clear();
        labelListBox->insertStringList(labels);
}

SelectionDialog:: ~SelectionDialog()
{
}

void SelectionDialog:: showEvent( QShowEvent * e )
{
	// Query the database for the resource types
	// just before we show the dialog.  This
	// gets us the latest values (but is lower
	// overhead than querying each time the
	// menu pops up).
	setResourceTypes();

        //refresh the labels
        //QStringList labels = dataSource -> getResultLabels();
        QStringList labels = dataSource -> getAllLabelNames();
        labelListBox->clear();
        labelListBox->insertStringList(labels);

	// Now do the rest of the work
	SelectionDialogBase::showEvent( e );
}

void SelectionDialog:: setResourceTypes()
{
	resourceTypes = dataSource->getResourceTypes();
	resourceSelector->setResourceChoices( resourceTypes );
}

void SelectionDialog:: initConnections()
{
	// Connect the signals and slots
	connect( resetPushButton, SIGNAL( clicked() ), this,
			SLOT( resetLists() ) );

	connect( clearSelectionPushButton, SIGNAL( clicked() ),
			this, SLOT( deleteConstraints() ) );

	connect( constraintListView,
			SIGNAL( itemRenamed( Q3ListViewItem *, int ) ),
			this, SLOT( setRelatives( Q3ListViewItem *, int ) ) );

	// The "Get Data" pushbutton is connected to "accept()"
	// and "Cancel" is connected to "reject()" in the base
	// class, so there's no need to connect those buttons here.
}

void SelectionDialog:: initSelectors()
{
	connect( resourceSelector, SIGNAL( resourceSelected( QString,
					QString, QString, QString ) ),
			this, SLOT( addConstraint(QString,QString,
					QString,QString) ) );

	connect( resourceSelector, SIGNAL( resourceTypeSelected( QString ) ),
			this, SLOT( addResourceType( QString ) ) );

	// Connect requests for data from the resource selector to
	// the slots in the data server
	connect( resourceSelector, SIGNAL( needResourcesByType( QString,
					QString, void * ) ),
			dataSource, SLOT( findResourcesByType( QString,
					QString, void * ) ) );
	
	connect( resourceSelector, SIGNAL( needAttributesByType( QString,
					QString, void * ) ),
			dataSource, SLOT( findAttributesByType( QString,
					QString, void * ) ) );
	
	connect( resourceSelector, SIGNAL( needResourcesByParent( QString,
					QString, QString,
					SelectionListItem * ) ),
			dataSource, SLOT( findResourcesByParent( QString,
					QString, QString,
					SelectionListItem * ) ) );
	
	connect( resourceSelector, SIGNAL( needAttributesByName( QString,
					QString, SelectionListItem * ) ),
			dataSource, SLOT( findAttributesByName( QString,
					QString, SelectionListItem * ) ) );

	connect( resourceSelector, SIGNAL( needAttributesByResourceName(
					QString, SelectionListItem * ) ),
			dataSource, SLOT( findAttributesByResourceName(
					QString, SelectionListItem * ) ) );
	
	connect( resourceSelector, SIGNAL( needExecutionResourcesByName(
					QString, SelectionListItem * ) ),
			dataSource, SLOT( findExecutionResourcesByName(
					QString, SelectionListItem * ) ) );
	
	// Connect the data coming from the data server to the selector
	connect( dataSource, SIGNAL( foundAttributesByType( QString,
					QStringList, void * ) ),
			resourceSelector, SLOT( setAttributeList( QString,
					QStringList, void * ) ) );

	connect( dataSource, SIGNAL( foundResourcesByType( QString,
					QMap<QString,int>, void * ) ),
			resourceSelector, SLOT( setTopLevelResources( QString,
					QMap<QString,int>, void * ) ) );

	connect( dataSource, SIGNAL( foundResourcesByParent( QString,
					QMap<QString,int>,
					SelectionListItem * ) ),
			resourceSelector, SLOT( setChildResources( QString,
					QMap<QString,int>,
					SelectionListItem * ) ) );

	connect( dataSource, SIGNAL( foundAttributesByName( QString,
					QStringList, SelectionListItem * ) ),
			resourceSelector, SLOT( setAttributeValues( QString,
					QStringList, SelectionListItem * ) ) );

	connect( dataSource, SIGNAL( foundAttributesByResourceName( 
					AttrListMap, SelectionListItem * ) ),
			resourceSelector, SLOT( setItemAttributesMap( 
					AttrListMap, SelectionListItem * ) ) );

	connect( dataSource, SIGNAL( foundExecutionResources(
					Q3ValueList<QPair<QString,QString> >,
					SelectionListItem * ) ),
			resourceSelector, SLOT( setItemExecutionResources(
					Q3ValueList<QPair<QString,QString> >,
					SelectionListItem * ) ) );
}

void SelectionDialog:: deleteConstraints()
{
	Q3ListViewItemIterator items( constraintListView,
			Q3ListViewItemIterator::Selected );
	ConstraintListItem * selItem;

	// Do all the changes in one transaction
	dataSource->beginAdd();
	while( ( selItem = (ConstraintListItem*)(items.current()) ) != 0 ) {
		++items;
#ifdef METRIC_HACK
		if( selItem->text( TypeCol ) == "metric" ) {
			metricIds = QString();
		}
		else {
#endif
			// It's a resource-type entry (not a specific set 
			// of resources)
			if( selItem->text( ValueCol ) == "ANY" ) {
				dataSource->deleteResourcesByName(
					selItem->text( TypeCol ) , QString() );
			} else {
				deleteItemRelatives( selItem, Self | FromItem );
			}
#ifdef METRIC_HACK
		}
#endif

		delete selItem;
	}
	dataSource->endAdd();

	matchCountLabel->setText( "---" );
	qApp->processEvents();	// Keep things looking responsive while
				// we recompute the count
	matchCountLabel->setText( QString::number(
				dataSource->getResultCount(
					typeCount(),
					metricIds, labelList() ) ) );
}

// Convenience function to delete ancestors and descendants from
// the database internal list.
void SelectionDialog:: deleteItemRelatives( ConstraintListItem * item,
	       int rel )
{
	bool ancestors, descendants;

	if( rel & FromItem ) {
		QChar relatives = item->text( RelCol )[0];
		ancestors = ( relatives == 'B' || relatives == 'A' );
		descendants = ( relatives == 'B' || relatives == 'D' );
	} else {
		ancestors = rel & Ancestors;
		descendants = rel & Descendants;
	}

	QString type = item->text( TypeCol );
	QString value = item->text( ValueCol );
	QString resType = item->resourceType();
	if( type == resType ) {
		if( rel & Self )
			dataSource->deleteResourcesByName( type, value );
		if( ancestors )
			dataSource->deleteAncestorsByName( type, value );
		if( descendants )
			dataSource->deleteDescendantsByName( type, value );

	} else {
		if( rel & Self )
			dataSource->deleteResourcesByAttribute( resType,
					type, value );
		if( ancestors )
			dataSource->deleteAncestorsByAttribute(
					resType, type, value );
		if( descendants )
			dataSource ->deleteDescendantsByAttribute(
					resType, type, value );
	}
}

int SelectionDialog:: addItemRelatives( ConstraintListItem * item,
	       int rel )
{
	bool ancestors, descendants;
	int r = 0;	// results matching newly added resources

	if( rel & FromItem ) {
		QChar relatives = item->text( RelCol )[0];
		ancestors = ( relatives == 'B' || relatives == 'A' );
		descendants = ( relatives == 'B' || relatives == 'D' );
	} else {
		ancestors = rel & Ancestors;
		descendants = rel & Descendants;
	}

	QString type = item->text( TypeCol );
	QString value = item->text( ValueCol );
	QString resType = item->resourceType();
	if( type == resType ) {
		if( rel & Self )
			r += dataSource->addResourcesByName( type, value );
		if( ancestors )
			r += dataSource->addAncestorsByName( type, value );
		if( descendants )
			r += dataSource->addDescendantsByName( type, value );

	} else {
		if( rel & Self )
			r += dataSource->addResourcesByAttribute( resType,
					type, value );
		if( ancestors )
			r += dataSource->addAncestorsByAttribute(
					resType, type, value );
		if( descendants )
			r += dataSource ->addDescendantsByAttribute(
					resType, type, value );
	}

	return r;
}

void SelectionDialog:: addConstraint( QString type, QString value,
		QString resources, QString resourceType )
{
	// Before we add an item, make sure it's not a duplicate
	// of an exisiting item, since that's not useful and hard
	// to recover from later.
	Q3ListViewItemIterator it( constraintListView );
	while( it.current() ) {
		ConstraintListItem * item = (ConstraintListItem *)it.current();
		if( item->text( ValueCol ) == value
				&& item->resourceType() == resourceType ) {
			// Show the duplicate by selecting it
			constraintListView->setSelected( item, true );
			return;
		}
		++it;
	}

	// Add the new constraint to the list
	ConstraintListItem * item = new ConstraintListItem( constraintListView,
			"D", type, value, "---", resourceType, resources );
	

#ifdef METRIC_HACK 
	// Ugly hack to handle metrics specially
	if( type == "metric" ) {
		item->setResources( QString() );	// Blank out res list
		item->setText( RelCol, "N" );
		item->setRenameEnabled( RelCol, false );
		metricIds = resources;
		return;
	}
#endif

	// Allow user to set the value in RelCol (types of relatives to get)
	item->setRenameEnabled( RelCol, true );

	// Put resources in the db list according to the specifications in
	// this item. 
	dataSource->beginAdd();
	int results = addItemRelatives( item, Self | FromItem );

	// Check for success; rollback and remove item if there was an error
	if( results < 0 ) {
		dataSource->cancelAdd();
		delete item;
	} else {
		dataSource->endAdd();
		setCounts( item, results );
	}

}

void SelectionDialog:: addResourceType( QString type )
{
	// Add the new constraint to the list; value is "any", and no
	// relatives are included by default.  First, look up all the
	// resource ids for this type.
	QString resources;

	ConstraintListItem * item = new ConstraintListItem( constraintListView,
			"N", type, "ANY", "---", type, resources );

	// Don't let user set the value in RelCol (types of relatives to get)
	// The purpose of a resource-type-only entry is to limit the search to
	// include entries at a specific level, and searching for all
	// relatives of all resources of a given type (as we do for other
	// constraints) would be expensive.
	item->setRenameEnabled( RelCol, false );

	// Put all resources of this type in the database's temporary table
	// The blank value string means "find all values"
	dataSource->beginAdd();
	int results = dataSource->addResourcesByName( type, QString() );
	if( results < 0 ) {
		dataSource->cancelAdd();
		delete item;
	} else {
		setCounts( item, results );
		dataSource->endAdd();
	}

}	

void SelectionDialog:: setRelatives( Q3ListViewItem * item, int col )
{
	// Sanity check; the only column that should have been changed
	// is the Relatives List 
	if( col != RelCol ) return;

	// Cast to the right type
	ConstraintListItem * it = (ConstraintListItem*) item;

	// Make the following changes atomically
	dataSource->beginAdd();

	// We don't know the what relatives were included previously,
	// so we'll delete any ancestors and descendants and then
	// add whatever was requested.
	deleteItemRelatives( it, Both );

	// Get the count for the remaining resources (no relatives) in this item
	int results = dataSource->getResultCount( 1, QString(),labelList() );
	if( results < 0 ) {
		dataSource->cancelAdd();
		return;
	}

	// Now add back the items as specfied in the RelCol
	int count = addItemRelatives( it, FromItem );
	
	// Be sure the changes succeeded
	if( count < 0 ) {
		dataSource->cancelAdd();
		return;
	}

	// Update OK; commit it and count the results
	dataSource->endAdd();
	results += count;

	// Update the item count for this item and the whole set
	setCounts( it, results );
}

void SelectionDialog:: setItemCount( Q3ListViewItem * item, int col )
{
	// Update the item count based on a change to the selected
	// relatives.
	if( col != RelCol ) return;

	// Cast to the right type
	ConstraintListItem * it = (ConstraintListItem*) item;

	// Get the count and set the appropriate column
	QChar relatives = ( it->text( RelCol ) )[0];
	bool ancestors = ( relatives == 'B' || relatives == 'A' );
	bool descendants = ( relatives == 'B' || relatives == 'D' );
	QString resources = it->resources( ancestors, descendants );

    // 2008-6-25 smithm
    // This conditional operator appears to be attempting to set resList to a
    // new QStringList if resources is empty else set resList to resources.
    // However, resList is of type QStringList and resources is of type
    // QString.  Changed so that resources is added to the resList instead.
    // QStringList resList = resources.isEmpty() ? QStringList() : resources;
    QStringList resList;
    if (resources.isEmpty())
        resList = QStringList();
    else
        resList += resources;

	// Get data for just the metric or just the resource list
	QString resultCount;
#ifdef METRIC_HACK
	if( it->text( TypeCol ) == "metric" ) {
		resultCount = QString::number( dataSource->getResultCount(
					QStringList(), metricIds ) );
		it->setText( CountCol, resultCount );
	} else {
#endif
		resultCount = QString::number( dataSource->getResultCount(
					1, QString(), labelList() ) );
		it->setText( CountCol, resultCount );
#ifdef METRIC_HACK
	}
#endif
	// If this is the only item, the total count will be the
	// same as resultCount, which we just computed; otherwise,
	// we need to get the overall count now.
	if( constraintListView->childCount() > 1 ) {
		// Let the user know we're pondering this one...
		matchCountLabel->setText( "---" );
		// To keep the gui responsive, we'll process some events
		// before we do the next query.
		qApp->processEvents();

		// Get the overall count
		resultCount = QString::number( dataSource->getResultCount(
					typeCount(), metricIds, labelList() ) );
	}

	// Update the overall count
	matchCountLabel->setText( resultCount );
}


void SelectionDialog:: setCounts( ConstraintListItem * it, int count )
{
	it->setText( CountCol, QString::number( count ) );

	QString resultCount;

	// If this is the only item, the total count will be the
	// same as resultCount, which we already know; however,
	// getResultCount() has the side effect of populating a
	// cache table in the database with the list of selected
	// foci, so we call it even when we already know the count.
	
	// Let the user know we're pondering this one...
	matchCountLabel->setText( "---" );

	// To keep the gui responsive, we'll process some events
	// before we do the next query.
	qApp->processEvents();

	// Get the overall count
	resultCount = QString::number( dataSource->getResultCount( typeCount(),
				metricIds, labelList() ) );

	// Update the overall count
	matchCountLabel->setText( resultCount );
}

Q3ValueList<ResourceTypeAndName> SelectionDialog:: buildConstraintList()
{
	Q3ValueList<ResourceTypeAndName> constraints;
	Q3ListViewItemIterator items( constraintListView );
	Q3ListViewItem * cur;
	while( ( cur = items.current() ) != 0 ) {
		++items;
		constraints += ResourceTypeAndName( cur->text(TypeCol),
				cur->text(ValueCol) );
	}

	return constraints;
}

QStringList SelectionDialog:: buildResourceIdList()
{
	// Build a list of strings containing resource ids
	QStringList resourceSet;
	QString resources;
	Q3ListViewItemIterator items( constraintListView );
	ConstraintListItem * cur;
	while( ( cur = (ConstraintListItem*)(items.current()) ) != 0 ) {
		++items;

#ifdef METRIC_HACK
		// Skip if this resource type is "metric"
		if( cur->text( TypeCol ) == "metric" ) continue;
#endif

		// Get the set of resources, including the requested
		// relatives
		QChar relatives = ( cur->text( RelCol ) )[0];
		bool ancestors = ( relatives == 'B' || relatives == 'A' );
		bool descendants = ( relatives == 'B' || relatives == 'D' );
		resources = cur->resources( ancestors, descendants);

		resourceSet += resources;
	}

	return resourceSet;
}

int SelectionDialog:: typeCount() const
{
	// Count the distinct type hierarchies by building a list
	// of distinct resource hierarchies and then counting them.  
	// Each hierarchy is identified by its first element.
	// This is an O(n^2) algorithm, but n should be pretty small
	// (almost always less than 5).
	Q3ListViewItemIterator items( constraintListView );
	ConstraintListItem * cur;
	QStringList names;
	while( ( cur = (ConstraintListItem*)(items.current()) ) != 0 ) {
		++items;
		QString hierarchy = cur->resourceType().section( PTRESDELIM, 0, 1 );

		// Don't count metric resources, since they aren't part of
		// the focus
		if( hierarchy == "metric" ) continue;

		// Look for match in existing list
		QStringList::Iterator it;
		for( it = names.begin(); it != names.end(); ++it ) {
			if( *it == hierarchy ) break;	// matched existing
		}

		if( it == names.end() ) {	// no match found
			names.append( hierarchy );
		}
	}

	return names.count();
}

void SelectionDialog:: resetLists()
{
	resourceSelector->reset();
	constraintListView->clear();
	matchCountLabel->setText( QString::null );
	//selectionFilterLineEdit->setText( QString::null );
	dataSource->deleteAllResources();
        
        labelListBox->selectAll(false);
}

QStringList SelectionDialog:: labelList(){
     //returns the list of selected labels in the list box
     QStringList labels;
     //for (int i = 0; i < labelListBox->count(); ++i){
     for (int i = 0; i < labelListBox->numRows(); ++i){
         bool selected = labelListBox->isSelected(i);
         if (selected){
            QString label = labelListBox->text(i);
            labels.append(label);
         }
     }
     return labels;
}


void SelectionDialog::labelSelected(){
      // want to update the number of results matching the query when a label is chosen
       QString resultCount;
       resultCount = QString::number( dataSource->getResultCount(
                                        typeCount(), metricIds , labelList()) );
        // Update the overall count
        matchCountLabel->setText( resultCount );
}

void SelectionDialog::combineResultsSelected(){
      emit(combineResults(false));
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


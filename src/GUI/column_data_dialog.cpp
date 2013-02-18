// column_data_dialog.cpp
// John May, 17 February 2005

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/
#include <qpushbutton.h>
#include <q3listbox.h>
#include <q3listview.h>
#include <qmessagebox.h>
//Added by qt3to4:
#include <QCloseEvent>

#include "column_data_dialog.h"
#include "static_check_list_item.h"

#include "column_data_dialog.moc"

ColumnDataDialog:: ColumnDataDialog( QWidget * parent, const char * name )
	: ColumnDataDialogBase( parent, name )
{
	connect( addResourcesPushButton, SIGNAL( clicked() ),
			this, SLOT( handleAddResources() ) );

	connect( addAttributesPushButton, SIGNAL( clicked() ),
			this, SLOT( handleAddAttributes() ) );

	connect( clearPushButton, SIGNAL( clicked() ),
			this, SLOT( handleRemoveColumns() ) );

	connect( getDataPushButton, SIGNAL( clicked() ),
			this, SLOT( handleGetData() ) );

	connect( resourceListBox, SIGNAL( highlighted( const QString& ) ),
			this,
			SLOT( handleHighlightedResource( const QString& ) ) );

}

// This is not a member function; it's just a utility used for this class
// Returns all the items in a list box or, optionally, just those that
// have been selected.
QStringList getListItems( const Q3ListBox * listBox, bool selectedOnly )
{
	QStringList items;

	Q3ListBoxItem * item;
	for( item = listBox->firstItem(); item != 0; item = item->next() ) {
		if( !selectedOnly || item->isSelected() ) {
			items += item->text();
		}
	}

	return items;
}

void ColumnDataDialog:: setAvailableResources( QStringList res,
		void * requester )
{
	if( requester != this ) return;

	resourceListBox->clear();
	resourceListBox->insertStringList( res );
}

void ColumnDataDialog:: setAvailableAttributes( QString, QStringList attrs,
		void * requester )
{
	if( requester != this ) return;

	attributeListBox->insertStringList( attrs );
}

void ColumnDataDialog:: handleGetData()
{
	// Get the data for columns that we haven't already filled in
	QStringList resources, attributes;

	// Get each unchecked item, store its value, and set its
	// state to checked
	Q3ListViewItemIterator itr( selectedResourceListView,
			Q3ListViewItemIterator::NotChecked );
	StaticCheckListItem * item;
	while( ( item = (StaticCheckListItem*)(itr.current()) ) != 0 ) {
		resources += item->text();
		item->setOn( true );
		++itr;
	}

	Q3ListViewItemIterator ita( selectedAttributeListView,
			Q3ListViewItemIterator::NotChecked );
	while( ( item = (StaticCheckListItem*)(ita.current()) ) != 0 ) {
		attributes += item->text();
		item->setOn( true );
		++ita;
	}

	emit dataRequested( resources, attributes );
}
	
void ColumnDataDialog:: handleAddResources()
{
	QStringList resources = getListItems( resourceListBox, true );
	QStringList::Iterator it;
	for( it = resources.begin(); it != resources.end(); ++it ) {
		new StaticCheckListItem( selectedResourceListView, *it );
	}
	emit columnsRequested( resources );
}

void ColumnDataDialog:: handleAddAttributes()
{
	QStringList attributes  = getListItems( attributeListBox, true );
	QStringList::Iterator it;
	for( it = attributes.begin(); it != attributes.end(); ++it ) {
		new StaticCheckListItem( selectedAttributeListView, *it );
	}
	emit columnsRequested( attributes );
}

void ColumnDataDialog:: handleRemoveColumns()
{
#if 0
	// Should only issue this warning if there are checked items
	// (i.e., data has already been retrieved)
	int reply =
		QMessageBox:: question( this, "Remove Columns",
			"Removing these columns will also remove them from "
			"the data table, along with any data they contain. "
			"Are you sure you want to do this?",
			QMessageBox::Cancel | QMessageBox::Escape,
			QMessageBox::Ok | QMessageBox::Default );

	if( reply == QMessageBox::Cancel ) return;
#endif
	
	// Remove each selected item from the two lists.
	QStringList columns;
	Q3ListViewItemIterator itr( selectedResourceListView,
			Q3ListViewItemIterator::Selected );
	StaticCheckListItem * item;
	while( ( item = (StaticCheckListItem*)(itr.current()) ) != 0 ) {
		columns += item->text();
		++itr;
		delete item;
	}

	Q3ListViewItemIterator ita( selectedAttributeListView,
			Q3ListViewItemIterator::Selected );
	while( ( item = (StaticCheckListItem*)(ita.current()) ) != 0 ) {
		columns += item->text();
		++ita;
		delete item;
	}

	emit removeColumnsRequested( columns );
}

void ColumnDataDialog:: handleHighlightedResource( const QString& resName )
{
	attributeListBox->clear();
	emit attributesRequested( resName, QString(), this );
}

void ColumnDataDialog:: closeEvent( QCloseEvent * e )
{
	// Emit a closing() signal, then do whatever the
	// base class version would do.  
	emit closing();

	ColumnDataDialogBase::closeEvent( e );
}

void ColumnDataDialog:: reset()
{
	resourceListBox->clear();
	attributeListBox->clear();
	selectedResourceListView->clear();
	selectedAttributeListView->clear();
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

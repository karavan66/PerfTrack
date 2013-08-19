// resource_selector.cpp
// John May, 29 October 2004

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <qcombobox.h>
#include <qcursor.h>
#include <qlabel.h>
#include <qstringlist.h>
#include <qtoolbutton.h>
#include <q3widgetstack.h>
//Added by qt3to4:
#include <QShowEvent>
#include <Q3ValueList>
#include <Q3PopupMenu>
#include <QHideEvent>

#include "attributedialog.h"
#include "resource_selector.h"

#include "resource_selector.moc"

ResourceSelector:: ResourceSelector( QWidget * parent,
		const char * name, Qt::WFlags fl )
	: ResourceSelectorBase( parent, name, fl )
{
	initSelector();
}

ResourceSelector:: ResourceSelector( Q3ValueList<QStringList> types,
		QWidget * parent, const char * name, Qt::WFlags fl )
	: ResourceSelectorBase( parent, name, fl )
{
	initSelector();
	setResourceChoices( types );
}

void ResourceSelector:: initSelector()
{
	// Create a popup menu to show the resource types
	typePopupMenu = new Q3PopupMenu();
	connect( typePopupMenu, SIGNAL( activated(int) ),
			this, SLOT( getResourceItems(int) ) );

	// Create a dialog to show item info when requested
	attributeDialog = new AttributeDialog( this );
	attributeDialog->hide();

	// Show the menu when the menu button is clicked
	menuPushButton->setPopup( typePopupMenu );

	connect( selectButton, SIGNAL( clicked() ),
			this, SLOT( getSelectedResource() ) );

	connect( selectTypeButton, SIGNAL( clicked() ),
			this, SLOT( getSelectedResourceTypes() ) );

	connect( resourceListView, SIGNAL( expanded( Q3ListViewItem * ) ),
			this, SLOT( itemExpanded( Q3ListViewItem * ) ) );

	connect( attributeListView, SIGNAL( expanded( Q3ListViewItem * ) ),
			this, SLOT( itemExpanded( Q3ListViewItem * ) ) );

	connect( resourceListView, SIGNAL( clicked( Q3ListViewItem * ) ),
			this, SLOT( requestItemInfo( Q3ListViewItem * ) ) );

	connect( showInfoButton, SIGNAL( toggled( bool ) ),
			this, SLOT( setItemInfoDialog( bool ) ) );

	connect( attributeDialog->itemComboBox, SIGNAL( activated(
					const QString &) ),
			this, SLOT( showItemInfo( const QString & ) ) );
	connect( resourceListView, SIGNAL( selectionChanged() ),
			this, SLOT( clearAttributeSelections() ) );
	connect( attributeListView, SIGNAL( selectionChanged() ),
			this, SLOT( clearResourceSelections() ) );
//	connect( resourceListView, SIGNAL( clicked( QListViewItem * ) ),
//			this, SLOT( getItemCount( QListViewItem * ) ) );
}


void ResourceSelector:: getSelectedResource()
{
	// Iterate through the selected items in the resource list view
	Q3ListViewItemIterator resourceItems( resourceListView,
			Q3ListViewItemIterator::Selected );
	SelectionListItem * sli;
	
	while( ( sli = (SelectionListItem *)resourceItems.current() )
			!= 0 ) { 
		emit resourceSelected(
				sli->text( SelectionListItem::ResTypeCol ),
				qualifiedResourceName( sli ),
				sli->resourceList(),
				sli->text( SelectionListItem::ResTypeCol )
				);
		++resourceItems;
	}

	// Iterate through the selected items in the attribute list view
	// The current resource type (for all displayed attributes) is
	// in the menu button label.
	Q3ListViewItemIterator attributeItems( attributeListView,
			Q3ListViewItemIterator::Selected );
	while( ( sli = (SelectionListItem *)attributeItems.current() )
			!= 0 ) { 
		emit resourceSelected(
				sli->text( SelectionListItem::AttrNameCol ),
				sli->text( SelectionListItem::AttrValueCol ),
				sli->resourceList(),
				menuPushButton->text() );
		++attributeItems;
	}
}

void ResourceSelector:: getSelectedResourceTypes()
{
	// It's possible to have multiple resource types in one
	// list view (because child items may be open), so we need to
	// add each one that has been selected, but only once.
	// Ideally, we could collect all the resource ids here too,
	// rather than getting them from the database, but if a child
	// item is selected, we don't have the ids for other chidren
	// of the same type under different parents.
	Q3ListViewItemIterator resourceItems( resourceListView,
			Q3ListViewItemIterator::Selected );
	SelectionListItem * sli;
	QStringList resTypes;
	QStringList::Iterator it;
	while( ( sli = (SelectionListItem *)resourceItems.current() ) != 0 ) {

		// If the resource type isn't already in the list,
		// add it to the end
		QString resourceType
			= sli->text( SelectionListItem::ResTypeCol );
		if( ( it = resTypes.find( resourceType ) ) == resTypes.end() ) {
			resTypes.insert( it, resourceType );
		}
		++resourceItems;
	}
	
	// Now we have a list of unique selected resource types;
	// emit a signal for each one.
	for( it = resTypes.begin(); it != resTypes.end(); ++it ) {
		emit resourceTypeSelected( *it );
	}

	// For now, we're not doing attributes this way
}


void ResourceSelector:: setResourceChoices( Q3ValueList<QStringList> types )
{
	typePopupMenu->clear();

	// Create a list of resources in the menu, and initialize
	// a counter so we can identify them later.
	resNameList.clear();
	resNameCount = 0;

	// Add resource types to the popup menu.  Also add them to
	// the resNameList and associate the list index with
	// the menu item so we can look up the value when the list
	// item is selected.
	Q3ValueList<QStringList>::ConstIterator slit;
	for( slit = types.begin(); slit != types.end(); ++slit ) {
		// Nonhierarchical resource
		if( (*slit).count() == 1 ) {
			QString resName = (*slit).first();
			resNameList.append( resName );
			typePopupMenu->insertItem( resName, resNameCount++ );
		} else {
			// Create a submenu for hierarchical resources
			Q3PopupMenu * submenu =
				new Q3PopupMenu( typePopupMenu );
			connect( submenu, SIGNAL( activated(int) ),
					this, SLOT( getResourceItems(int) ) );

			// Populate the submenu
			QStringList::ConstIterator sit;
			for( sit = (*slit).begin();
					sit != (*slit).end(); ++sit ) {
				resNameList.append( *sit );
				submenu->insertItem( *sit, resNameCount++ );
			}

			// Add the submenu to the main menu; use the first
			// item in the hierarchy to name the submenu
			typePopupMenu->insertItem( (*slit).first(),
					submenu );
		}
	}
}

void ResourceSelector:: getResourceItems( int item )
{
	QString resourceType;

	// Get the type of the resource
	resourceType = resNameList[item];

	// Set the name of the button to reflect the selected resource
	// (so it behaves like a combo box)
	menuPushButton->setText( resourceType);

	// Clear out our display
	reset();

	// Get both resource and attribute data.  
	emit needResourcesByType( resourceType, QString(), this );
	emit needAttributesByType( resourceType, QString(), this );
}

void ResourceSelector:: itemExpanded( Q3ListViewItem * item )
{
	// This pointer is really to the specialized version of the class
	SelectionListItem * sli = (SelectionListItem *)item;

	// Nothing to do if children already fetched
	if( sli->childrenFetched() ) return;

	// Get the data and insert it as a child of this item,
	// according to the requested view
	if( sli->listView() == resourceListView ) {
		emit needResourcesByParent(
				sli->text( SelectionListItem::ResTypeCol ),
				qualifiedResourceName( sli ),
				QString(), sli );
	} else {
		emit needAttributesByName(
				sli->text( SelectionListItem::AttrNameCol ),
				QString(), sli );
	}

	// Don't need to do this again
	sli->setChildrenFetched( TRUE );
}

void ResourceSelector:: reset()
{
	// Clear out all data 
	resourceListView->clear();
	attributeListView->clear();

	// No current item displayed in the attribute dialog
	displayedSLI = NULL;

	// Clear out the attribute display dialog, and hide the
	// combo box, if there is one
	attributeDialog->attributeListView->clear();
	attributeDialog->executionResourceExtension
		->executionResourceListView->clear();
	attributeDialog->labelStack->raiseWidget(
			attributeDialog->labelPage );
	attributeDialog->itemLabel->setText( QString() );
//	resourceNameDict.clear();
//	attributeNameDict.clear();
}

void ResourceSelector:: getSelections( QStringList& sl, int column )
{
	// Iterate through the selected items in this view
	Q3ListViewItemIterator items( resourceListView,
			Q3ListViewItemIterator::Selected );
	Q3ListViewItem * sli;
	
	while( ( sli = items.current() ) != 0 ) { 
		sl += sli->text( column );
		++items;
	}
}

// This version used when we stored resource lists explicitly
void ResourceSelector:: setTopLevelResources( QString type,
		QMap<QString,QPair<QString,QString> > resources,
		void * requester )
{
	// Only respond if the data was intended for this object
	if( requester != this ) return;

	QMap<QString,QPair<QString,QString> >::ConstIterator it;
	for( it = resources.begin(); it != resources.end(); ++it ) {
		// Create a new list item, store the resource id list,
		// and set the item to be expandable and selectable
		new SelectionListItem( resourceListView,
			it.key(), type, it.data().first, it.data().second,
			true, true );
	}
}

// This version used when we build tables of selected resources in the db
void ResourceSelector:: setTopLevelResources( QString type,
		QMap<QString,int> resources,
		void * requester )
{
	// Only respond if the data was intended for this object
	if( requester != this ) return;

	QMap<QString,int>::ConstIterator it;
	for( it = resources.begin(); it != resources.end(); ++it ) {
		// Create a new list item
		// and set the item to be expandable and selectable
		new SelectionListItem( resourceListView,
			it.key(), type, QString(), QString(),
			true, true );
	}
}

void ResourceSelector:: setAttributeList( QString, QStringList attributes,
		void * requester )
{
	// Only respond if the data was intended for this object
	if( requester != this ) return;

	// Attribute type is ignored for now

	QStringList::ConstIterator it;
	for( it = attributes.begin(); it != attributes.end(); ++it ) {
		// Create a new list item and set it to be expandable
		// but not selectable.  Leave the second column and
		// the resource id list blank
		new SelectionListItem( attributeListView,
			*it, QString(), QString(), QString(), true, false );
	}
}

// This version used when we stored resource lists explicitly
void ResourceSelector:: setChildResources( QString type,
		QMap<QString,QPair<QString,QString> > resources,
		SelectionListItem * parent )
{
	QMap<QString,QPair<QString,QString> >::ConstIterator it;
	for( it = resources.begin(); it != resources.end(); ++it ) {
		// Create a child list item, store the resource id list,
		// and set the item to be expandable and selectable
		new SelectionListItem( parent, it.key(), type, it.data().first,
				it.data().second, true, true );
	}
}

// This version used when we build tables of selected resources in the db
void ResourceSelector:: setChildResources( QString type,
		QMap<QString,int> resources,
		SelectionListItem * parent )
{
	QMap<QString,int>::ConstIterator it;
	for( it = resources.begin(); it != resources.end(); ++it ) {
		// Create a child list item
		// and set the item to be expandable and selectable
		new SelectionListItem( parent, it.key(), type, QString(),
				QString(), true, true );
	}
}

// This version used when we stored resource lists explicitly
void ResourceSelector:: setAttributeValues( QString name,
		QMap<QString,QPair<QString,QString> > attributes,
		SelectionListItem * parent )
{
	QMap<QString,QPair<QString,QString> >::ConstIterator it;
	for( it = attributes.begin(); it != attributes.end(); ++it ) {
		// Create a child list item, store the resource id list,
		// and set the item to be not expandable but selectable
		new SelectionListItem( parent, name, it.key(), it.data().first,
			it.data().second, false, true );
	}
}

// This version used when we build tables of selected resources in the db
void ResourceSelector:: setAttributeValues( QString name,
		QStringList attributes,
		SelectionListItem * parent )
{
	QStringList::ConstIterator it;
	for( it = attributes.begin(); it != attributes.end(); ++it ) {
		// Create a child list item
		// and set the item to be not expandable but selectable
		new SelectionListItem( parent, name, *it, QString(),
			QString(), false, true );
	}
}

// This version used when info is requested by attribute name
void ResourceSelector:: requestItemInfo( Q3ListViewItem * lvi )
{
	// Show info on the current item, if the "Show Info" button
	// is pressed.
	if( ! showInfoButton->isOn() ) return;

	// We know this is really a selection list item
	SelectionListItem * sli = (SelectionListItem *)lvi;

	// Be sure it's valid
	if( sli == NULL ) return;

	// Get the data if it's not already cached
	if( ! sli->attributesFetched() ) {
		emit needAttributesByResourceName(
				qualifiedResourceName( sli ),
				sli );
		// Once we get here, the data should be cached
	}

	// Keep track of which item's attributes are on display.
	// This is useful when showItemInfo() is called as a slot;
	// it needs this context that wouldn't be availabel otherwise.
	displayedSLI = sli;

	// Single item or no items: display its name and show the list
	// (or nothing)
	int count = sli->attributeMap().count();
	if( count <= 1 ) {
		attributeDialog->labelStack->raiseWidget(
				attributeDialog->labelPage );

		// Use full resource name returned database query, if available
		QString resName
			= ( count == 1 ) ? sli->attributeMap().keys().first()
			: qualifiedResourceName( sli );
		attributeDialog->itemLabel->setText( resName );
		showItemInfo( resName );
	} else  {
	// Multiple items; put the names in a combo box, 
	// and show the data for the first resource right away
		attributeDialog->labelStack->raiseWidget(
				attributeDialog->comboBoxPage );

		// Populate the combo box with the new set of resource
		// names, and keep a mapping of resource names to ids.
		attributeDialog->itemComboBox->clear();
		QStringList resList = sli->attributeMap().keys();
		attributeDialog->itemComboBox->insertStringList( resList );
		showItemInfo( resList.first() );
	}
}

// This version used when we request attributes by resource name
void ResourceSelector:: showItemInfo( const QString& name )
{

	// See which resources we're looking at.
	SelectionListItem * sli = displayedSLI;

	if( sli == NULL ) return;

	// Be sure the window is open (user could have closed it w/o
	// changing the showInfoButton state)
	attributeDialog->show();

	// Display the data; sli->attributeList handles an invalid
	// name (including and empty one) by returning and empty list.
	showItemAttributes( sli->attributeList( name ) );

	// For the special case that this is an execution resource,
	// also look up and display the resources associated with this
	// execution.
	
	if( sli->text( SelectionListItem::ResTypeCol ) == "execution" ) {
		// First, be sure the extension is open
		attributeDialog->showExecutionExtension( true );

		// Now get the data, either cached or from the database
		if( ! sli->executionResourcesFetched() ) {
			emit needExecutionResourcesByName( name, sli );
			// We should now have the data cached
		}
		showItemExecutionResources( sli->executionResourcesList() );
	} else {
		// Not the special case; be sure the extension is closed
		attributeDialog->showExecutionExtension( false );
	}
}

// This version used when we ask for attributes based on resource string
void ResourceSelector:: setItemAttributesMap(
		AttrListMap attr_map, 
		SelectionListItem * sli )
{
	sli->setAttributeMap( attr_map );
	sli->setAttributesFetched( true );
}

// This version was used when we ask for attributes based on ids
void ResourceSelector:: setItemAttributes( QString key,
		Q3ValueList<QPair<QString,QString> > attrs,
		SelectionListItem * sli )
{
	sli->setAttributeList( key, attrs );

	// Assume this data is coming in as a result of a pending request
	// to pop up a window, so go ahead and do that.
	showItemAttributes( attrs );
}

void ResourceSelector:: setItemExecutionResources(
		Q3ValueList<QPair<QString,QString> > res,
		SelectionListItem * sli )
{
	sli->setExecutionResourceList( res );

	sli->setExecutionResourcesFetched( true );

}

void ResourceSelector:: setItemInfoDialog( bool state )
{
	if( state ) {
		// We want to put the dialog just to the
		// right of the toplevel window.  So we
		// calculate the width of the dialog and
		// the position of the top level parent of
		// this widet, do the math, and set the
		// location.
		QPoint p = topLevelWidget()->pos();
		int newX = p.x() - attributeDialog->width();
		if( newX < 0 ) newX = 0;
		p.setX( newX );
		attributeDialog->move( p );
		attributeDialog->show();

		// Display the current item, if there is one and it's
		// selected.  This extra check prevents display of
		// data for a default current item when the list is
		// first generated.  However, it doesn't seem to
		// prevent display of a current item that has just
		// been deselected.
		Q3ListViewItem * lvi = resourceListView->currentItem();
		if( lvi && ! lvi->isSelected() ) lvi = 0;
		requestItemInfo( lvi );

		// Use a special cursor in the resource list view
		// so the user knows the behavior is different
		resourceListView->setCursor( Qt::WhatsThisCursor );
	} else {
		attributeDialog->hide();
		// Restore the normal cursor to the list view
		resourceListView->unsetCursor();
	}
}

void ResourceSelector:: showItemAttributes( 
		const Q3ValueList< QPair<QString,QString> >& attributes )
{
	attributeDialog->attributeListView->clear();

	if( attributes.count() == 0 ) {
		new Q3ListViewItem( attributeDialog->attributeListView,
				"(None found)" );
		return;
	}

	// Fill in the list view
	Q3ValueList<QPair<QString,QString> >::ConstIterator it;
	for( it = attributes.begin(); it != attributes.end(); ++it ) {
		new Q3ListViewItem( attributeDialog->attributeListView,
				(*it).first, (*it).second );
	}
}

void ResourceSelector:: showItemExecutionResources( 
		const Q3ValueList<QPair<QString,QString> >& res )
{

	attributeDialog->executionResourceExtension
		->executionResourceListView->clear();

	if( res.count() == 0 ) {
		new Q3ListViewItem( attributeDialog->executionResourceExtension
				->executionResourceListView,
				"(None found)" );
		return;
	}

	// Fill in the list view
	Q3ValueList<QPair<QString,QString> >::ConstIterator it;
	for( it = res.begin(); it != res.end(); ++it ) {
		new Q3ListViewItem( attributeDialog->executionResourceExtension
				->executionResourceListView,
				(*it).first, (*it).second );
	}
}

QString ResourceSelector:: qualifiedResourceName( SelectionListItem * sli )
{
	// Walk up the list of this item's parents, adding their names
	// to form a fuller name.  This might not necessarily be the
	// fully qualified name, depending on where the top-level display
	// parent is in the hierarchy.  Should work correctly even when
	// sli is initially null.
	QString qualname;
	Q3ListViewItem * p;

	for( p = sli; p != 0; p = p->parent() ) {
                if (p->parent() != 0)
		    qualname.prepend(PTRESDELIM 
				+ p->text( SelectionListItem::ResNameCol ) );
                else
		    qualname.prepend(p->text( SelectionListItem::ResNameCol ));
	}

	return qualname;
}

void ResourceSelector:: hideEvent( QHideEvent * e )
{
	// Be sure the attribute dialog gets hidden
	attributeDialog->hide();

	// Do all the default processing
	ResourceSelectorBase::hideEvent( e );
}

void ResourceSelector:: showEvent( QShowEvent * e )
{
	// Be sure the state of the attribute dialog
	// matches the state of the checkbox
	setItemInfoDialog( showInfoButton->isOn() );
	ResourceSelectorBase::showEvent( e );
}

void ResourceSelector:: clearResourceSelections()
{
	resourceListView->clearSelection();
}


void ResourceSelector:: clearAttributeSelections()
{
	attributeListView->clearSelection();
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


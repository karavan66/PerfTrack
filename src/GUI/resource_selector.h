//! \file resource_selector.h
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

#ifndef RESOURCE_SELECTOR_H
#define RESOURCE_SELECTOR_H

#include <qpushbutton.h>
#include <q3dict.h>
#include <qpair.h>
#include <q3popupmenu.h>
#include <qstring.h>
#include <qstringlist.h>
#include <q3valuelist.h>
#include <q3valuevector.h>
//Added by qt3to4:
#include <QShowEvent>
#include <QHideEvent>

#include "attributedialog.h"
#include "resource_selector_base.h"
#include "selection_list_item.h"

//! A widget that contains the controls for selecting resource values

class ResourceSelector : public ResourceSelectorBase {
	Q_OBJECT
public:
	typedef enum { ResourceName, AttributeName } EntryType;

	//! Create a column in the selection dialog for a set
	//! of resources.  \a types is a list of resource types,
	//! to be displayed in a menu.
	ResourceSelector( Q3ValueList<QStringList> types, 
			QWidget * parent = NULL, const char * name = 0,
			Qt::WFlags fl = 0 );

	//! Create a column in the selection dialog for a set
	//! of resources.  setResourceChoices() must be called after
	//! this version of the constructor to list the resource types,
	//! to be displayed in a menu.  
	ResourceSelector( QWidget * parent = NULL, const char * name = 0,
			Qt::WFlags fl = 0 );

	~ResourceSelector() { }

	//! Creates a list of entries in the list view 
	//! at the top level.  \a entries is a list of
	//! (resource_type,value) pairs.  \a expandable specifies
	//! whether children can be added to these entries.
	void addTreeEntries(
			Q3ValueList<QPair<QPair<QString,QString>,int> > entries,
			bool expandable );
	
	//! Creates a list of entries in the list view as
	//! children of \a parent.  \a entries is a list of
	//! (resource_type,value) pairs.
	//! This function is static because it doesn't need to access
	//! any state in this class, but it naturally fits together
	//! with the version above.  \a expandable specifies
	//! whether children can be added to these entries.
	static void addTreeEntries( SelectionListItem * parent,
		Q3ValueList<QPair<QPair<QString,QString>,int> > entries,
		bool expandable );


	//! Puts an entry in the tree view, with the column text \a s1
	//! and \a s2. \a resources is a comma-delimited string containing
	//! the matching resource ids.  It is hidden in the display and
	//! passed in the resourceSelected() signal.  \a expandable
	//! specifies whether the item should be displayed as able
	//! be expanded, and \a selectable specifies whether the item
	//! can be selected for inclusion in the resource list.
	void addTreeEntry( EntryType t, QString s1, QString s2,
			QString resources,
			bool expandable = TRUE, bool selectable = TRUE );

	//! Like the member-function version of addTreeEntry(), but
	//! searches the exisitng list view for
	//! items that match \a s1 in column 0 and \a s2 in column 1.
	//! When the first such item is found, the \a resources are
	//! appended to the text in column 2, separated by a comma.
	void addTreeEntryMerge( EntryType t, QString s1, QString s2,
			QString resources,
			bool expandable = TRUE, bool selectable = TRUE );

	//! Puts an entry in the tree view, as a child of the list
	//! item \a parent.  The column text is \a s1
	//! and \a s2. \a resources is a comma-delimited string containing
	//! the matching resource ids.  It is hidden in the display and
	//! passed in the resourceSelected() signal.  \a expandable
	//! specifies whether the item should be displayed as able
	//! be expanded, and \a selectable specifies whether the item
	//! can be selected for inclusion in the resource list.
	void addTreeEntry( SelectionListItem * parent,
			QString s1, QString s2, QString resources,
			bool expandable = TRUE, bool selectable = TRUE );

	//! Like addTreeEntry(), but searches children
	//! of \a parent for items that match \a s1 in column 0 and
	//! \a s2 in column 1.  When the first such item is found, the
	//! \a resources are appended to the text in column 2, separated
	//! by a comma.
	void addTreeEntryMerge( SelectionListItem * parent,
			QString s1, QString s2, QString resources,
			bool expandable = TRUE, bool selectable = TRUE );

	//! Removes all list items, clears filter specifications,
	//! unchecks all menu items.
	void reset();

	//! Add the selected strings from this selector to
	//! \a selectionList.
	void getSelections( QStringList& selectionList,
			int column );

	//! Sets the list of choices in the menu.  Items in \a types
	//! that are null QStrings create a separator in the menu.
	void setResourceChoices( Q3ValueList<QStringList> types );

public slots:
	//! Populate the list of top-level resources.  If \a requester !=
	//! this, the call does nothing.  This ensures that the slot
	//! responds only to requests that it initiated.
	void setTopLevelResources( QString type,
			QMap<QString,QPair<QString,QString> > resources,
			void * requester );

	void setTopLevelResources( QString type,
			QMap<QString,int> resources,
			void * requester );

	//! Populate a list of child resources
	void setChildResources( QString type,
			QMap<QString,QPair<QString,QString> > resources,
			SelectionListItem * parent );

	void setChildResources( QString type,
			QMap<QString,int> resources,
			SelectionListItem * parent );

	//! Populate the list of attributes.  If \a requester !=
	//! this, the call does nothing.  This ensures that the slot
	void setAttributeList( QString type, QStringList attributes,
			void * requester );

	//! Populate a list of values for an attribute
	void setAttributeValues( QString type, QMap<QString,
			QPair<QString,QString> > attributes,
			SelectionListItem * parent );

	void setAttributeValues( QString type, QStringList attributes,
			SelectionListItem * parent );

	//! Populate the list of attributes for an item
	void setItemAttributes( QString key,
			Q3ValueList<QPair<QString,QString> > attrs,
			SelectionListItem * sli );

	//! Replace the list of attributes for an item
	void setItemAttributesMap(
		AttrListMap attr_map, 
		SelectionListItem * sli );

	//! Populate the list of execution resources for an item
	void setItemExecutionResources( Q3ValueList<QPair<QString,QString> > res,
			SelectionListItem * sli );
protected slots:
	//! Runs through all items selected and emits resourceSelected()
	//! signal for each one.
	void getSelectedResource();

	//! Emits resourceTypeSelected() for each unique selected
	//! resource type.
	void getSelectedResourceTypes();

	//! Populates the list of resources or attributes based on
	//! \a index, an item in the resource menu.
	void getResourceItems( int index );

	//! Handles getting children (if necessary) when list items
	//! are expended.
	void itemExpanded( Q3ListViewItem * );

	//! Handle request to display item information for the new
	//! current resource item (which could refer to multiple resources)
	void requestItemInfo( Q3ListViewItem * );

	//! Get the attribute information for the dialog for a
	//! particular resource
	void showItemInfo( const QString& name );

	//! Show or hide the item info dialog
	void setItemInfoDialog( bool state );

	//! Clear selections in the resource list view
	void clearResourceSelections();

	//! Clear selections in the attribute list view
	void clearAttributeSelections();

	//! Arranges for selection by resource name (if id == 0) or
	//! attribute (if id != 0).
	//void setSelectionMethod( int );

//	void getItemCount( QListViewItem * );
	
signals:
	//! Transmits type, value, resource id string, and a string
	//! giving the resource type (which may be different from the
	//! first parameter if the selection represents an
	//! attribute/value pair.)
	void resourceSelected( QString type, QString value, QString res_ids,
			QString res_type );

	//! Transmits resource type with no ids
	void resourceTypeSelected( QString type );

	//! Requests a set of resources based a specified resource type
	void needResourcesByType( QString type, QString filter,
			void * requester );

	//! Requests a set of attributes based a specified resource type
	void needAttributesByType( QString type, QString filter,
			void * requester );

	//! Requests a set of resources based a their parent resource
	void needResourcesByParent( QString resourceIdList, QString filter,
		       SelectionListItem * parent );

	void needResourcesByParent( QString type, QString baseName,
			QString filter, SelectionListItem * parent );

	//! Requests a set of attribute values based on the attribute name
	void needAttributesByName( QString attribute, QString filter,
		       SelectionListItem * parent );

	//! Requests the attributes for a resource with a given id
	void needAttributesById( QString id, SelectionListItem * item );

	//! Requests the attributes for a resource with a given name (which
	//! can be just the last element(s) of the name)
	void needAttributesByResourceName( QString name,
			SelectionListItem * item );

	//! Requests the execution resources for a resource with a given id
	void needExecutionResourcesById( QString id, SelectionListItem * item );
	
	//! Requests the execution resources for a resource with a given name
	void needExecutionResourcesByName( QString name,
			SelectionListItem * item );

protected:
	//! Put attribute information in the attribute dialog
	void showItemAttributes( 
			const Q3ValueList<QPair<QString,QString> >& attributes );

	//! Put execution resource information in the attribute dialog
	void showItemExecutionResources(
			const Q3ValueList<QPair<QString,QString> >& res );

	//! Handle attribute dialog correctly when this widget is shown
	//! or hidden
	virtual void showEvent( QShowEvent * e );
	virtual void hideEvent( QHideEvent * e );

	//! Do all the constructor stuff
	void initSelector();

	//! Helper function to create qualifed resource names from
	//! SelectionListItems by prepending the parent names
	QString qualifiedResourceName( SelectionListItem * sli );

	int resNameCount;
	Q3ValueVector<QString> resNameList;
	Q3PopupMenu * typePopupMenu;
	QMap<QString,QString> resNameToId;
//	QDict<SelectionListItem> attributeNameDict;
//	QDict<SelectionListItem> resourceNameDict;
	AttributeDialog * attributeDialog;
	// SLI whose attributes are being shown.  This is needed when
	// multiple resources from one SLI are presented in a combo box.
	// When the user selects an item from this box, we need to know
	// which SLI to query for the attribute list.
	SelectionListItem * displayedSLI;	
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


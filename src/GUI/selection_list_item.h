//! \file selection_list_item.h
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

#ifndef SELECTION_LIST_ITEM_H
#define SELECTION_LIST_ITEM_H

#include <q3listview.h>
#include <qmap.h>
#include <qpair.h>
#include <qstring.h>
#include <q3valuelist.h>


// MOC doesn't like this spelled-out type in a signal or slot
typedef QMap<QString,Q3ValueList<QPair<QString,QString> > > AttrListMap;

//! Subclass of QListViewItem for use in SelectionDialog.

//! Supports on-the-fly determination of an item's children when
//! an item is opened.
class SelectionListItem : public Q3ListViewItem {
public:
	//! Names of the columns
	enum { ResNameCol = 0, AttrNameCol = 0,
		ResTypeCol = 1, AttrValueCol = 1 };

	//! Create a top-level resource entry; \a expandable states whether
	//! the user can click the item to see children.  
	SelectionListItem( Q3ListView * parent, QString value, QString type,
			QString resources, QString resNames,
			bool expandable = TRUE, bool selectable = TRUE );

	//! Create a child of another resource entry; \a expandable states
	//! whether children can be added to this item.  
	SelectionListItem( SelectionListItem * parent, QString value,
			QString type, QString resources, QString resNames,
			bool expanadable = TRUE,
			bool selectable = TRUE );

	//! Returns TRUE if an attempt has already been made to
	//! fetch the children of this item.  This is only
	//! determined by whether setChildrenFetched() has been
	//! called with TRUE.
	bool childrenFetched() const
	{	return children_fetched;	}

	//! Sets a flag to note that an attempt has been made to
	//! fetch the chilren of this item.
	void setChildrenFetched( bool state )
	{	children_fetched = state; }

	//! Returns TRUE if an attempt has already been made to
	//! fetch the attributes of this item.  This is only
	//! determined by whether setAttributesFetched() has been
	//! called with TRUE.
	bool attributesFetched() const
	{	return attributes_fetched;	}

	//! Sets a flag to note that an attempt has been made to
	//! fetch the attributes of this item.
	void setAttributesFetched( bool state )
	{	attributes_fetched = state; }

	//! Set the internal resources string (data is stored but
	//! not displayed)
	void setResourceList( QString  reslist )
	{
		resources = reslist;
	}

	//! Set the internal list of full resource names.  Data is
	//! stored but not displayed.
	void setResourceNameList( QString  resNames )
	{
		resourceNames = resNames;
	}

	//! Returns TRUE if an attempt has already been made to
	//! fetch the execution resources of this item.  This is only
	//! determined by whether setExecutionResourcesFetched() has been
	//! called with TRUE.
	bool executionResourcesFetched() const
	{	return execution_resources_fetched;	}

	//! Sets a flag to note that an attempt has been made to
	//! fetch the attributes of this item.
	void setExecutionResourcesFetched( bool state )
	{	execution_resources_fetched = state; }

	//! Append resources to the internal resource string.  A
	//! comma is automatically used to separate the new
	//! string from the existing one, if the existing string
	//! isn't empty.
	void appendResourceList( QString reslist )
	{
		if( resources.isEmpty() ) {
			setResourceList( reslist );
		} else {
			resources.append( "," + reslist );
		}
	}

	//! Append resource names to the internal resource string.  A
	//! comma is automatically used to separate the new
	//! string from the existing one, if the existing string
	//! isn't empty.
	void appendResourceNameList( QString resNames )
	{
		if( resourceNames.isEmpty() ) {
			setResourceNameList( resNames );
		} else {
			resourceNames.append( "," + resNames );
		}
	}

	//! Return the resource string.
	QString resourceList() const
	{
		return resources;
	}

	//! Return the resource name string.
	QString resourceNameList() const
	{
		return resourceNames;
	}

	//! Set the attributes list, which is displayed
	//! when the user requests this info for the item.
	//! In this list, the keys are attributes and the data entries
	//! are values.
	void setAttributeList( QString key,
			Q3ValueList<QPair<QString,QString> >  attrlist )
	{
		attributes[key] = attrlist;
	}


	//! Sets the full map of resource names to lists of attribute-value
	//! pairs for this item.  Any existing map is replaced.
	void setAttributeMap( AttrListMap attrmap )
	{
		attributes = attrmap;
	}

	//! Return the attributes list for the specified key
	Q3ValueList<QPair<QString,QString> > attributeList( QString key ) const
	{
		// Verify that there's a matching item and return it
		AttrListMap::const_iterator it;
		if( ( it = attributes.find( key ) ) != attributes.end() ) {
			return *it;
		}

		// Not matching entry; return blank list
		return Q3ValueList<QPair<QString,QString> >();
	}

	//! Returns a copy of the attribute map stored with this
	//! list item.
	AttrListMap attributeMap() const
	{
		return attributes;
	}

	//! Set the execution resources list, which is displayed
	//! when the user requests this info for the item.
	//! In this list, the keys are resources and the data entries
	//! are values.
	void setExecutionResourceList(
			Q3ValueList<QPair<QString,QString> > reslist )
	{
		execution_resources = reslist;
	}

	//! Return the execution resources list.  Unlike the attributes
	//! list, there can only be one set of execution resources per
	//! list item, because an execution is a top level resource.
	Q3ValueList<QPair<QString,QString> > executionResourcesList() const
	{
		return execution_resources;
	}

protected:
	bool children_fetched;
	bool attributes_fetched;
	bool execution_resources_fetched;
	QString resources;
	QString resourceNames;
	AttrListMap attributes;
	Q3ValueList<QPair<QString,QString> > execution_resources;
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


//! \file column_data_dialog.h

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
#ifndef COLUMN_DATA_DIALOG_H
#define COLUMN_DATA_DIALOG_H

#include <qstring.h>
#include <qstringlist.h>
//Added by qt3to4:
#include <QCloseEvent>

#include "column_data_dialog_base.h"

//! Allows users to select or remove  data columns in the display table.

//! The intent is that
//! columns are added to the table (but not populated)
//! as soon as they are selected.  Columns that were added
//! through this dialog can also be removed.
class ColumnDataDialog : public ColumnDataDialogBase {
	Q_OBJECT
public:
	ColumnDataDialog( QWidget * parent = 0, const char * name = 0 );

public slots:
	//! Accepts a list of resources for the available resource list.
	//! If \a requester != this, the slot does nothing, so we don't
	//! respond to data we didn't request.
	void setAvailableResources( QStringList res, void * requester );

	//! Accepts a list of attributes for the available attribute list.
	//! \a resType is ignored, but is needed for compatibility
	//! with the signal that sends this data.
	//! If \a requester != this, the slot does nothing, so we don't
	//! respond to data we didn't request.
	void setAvailableAttributes( QString resType, QStringList attrs,
			void * requester );

	//! Clear all the list boxes.  Usually called when a new table
	//! is created.
	void reset();
signals:
	//! Emitted when the user asks for data to fill in the columns
	//! specified columns.
	void dataRequested( QStringList resources, QStringList attributes );

	//! Emitted when the user requests columns to be added to the table
	void columnsRequested( QStringList columnNames );

	//! Emitted when the user asks for columns to be removed from
	//! the table.  By the time this signal has been emitted,
	//! the user has been warned that this could cause data in the
	//! table to be discarded.
	void removeColumnsRequested( QStringList columnNames );

	//! Emitted when the user asks for the attribute list for
	//! \a resourceType.  Second parameter is always an empty
	//! string; it corresponds to the filter, used by other
	//! signals.  The third paramater is "this", so we can
	//! match responses from the data source to this request.
	void attributesRequested( QString resourceType, QString, void * );

	//! Emitted when the dialog is closing (not necessarily being
	//! destroyed)
	void closing();

protected slots:
	//! Handle a click on the get data button by marshalling
	//! the list of columns to populate and emitting the
	//! dataRequested() signal.
	void handleGetData();
	
	//! Handle a click on the Add Resources button by getting
	//! the highlighted items from the list, putting them in the
	//! Selected Resources list, and emitting a columnsRequested()
	//! signal.
	void handleAddResources();

	//! Handle a click on the Add Attributes button by getting
	//! the highlighted items from the list, putting them in the
	//! Selected Attributes list, and emitting a columnsRequested()
	//! signal.
	void handleAddAttributes();

	//! Handle a click on the Remove Highlighted Columns button by
	//! warning the user of the consequences and then, if accepted,
	//! emitting a list of highlighted columns and then clearing
	//! them from the lists.
	void handleRemoveColumns();

	//! Handle highlighting of an item in the available resource
	//! list by requesting a list of the corresponding attributes.
	void handleHighlightedResource( const QString&  resName );

protected:
	//! Reimplement so we can emit a closing() signal
	virtual void closeEvent( QCloseEvent * e );
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

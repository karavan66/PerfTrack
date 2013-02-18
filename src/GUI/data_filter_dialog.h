//! \file data_filter_dialog.h
// John May, 24 January 2005

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#ifndef DATA_FILTER_DIALOG_H
#define DATA_FILTER_DIALOG_H

#include <qstring.h>
#include <qstringlist.h>
//Added by qt3to4:
#include <QCloseEvent>

#include "data_filter_dialog_base.h"
#include "filter_op.h"

//! Defines a dialog for setting up and manipulating data filters.
class DataFilterDialog : public DataFilterDialogBase {
	Q_OBJECT
public:
	DataFilterDialog( QWidget * parent = 0, const char * name = 0 );
	~DataFilterDialog() {}

public slots:
       	//! Set the list of available parameters.  This should be called
	//! before the dialog is first displayed.  It can also be called
	//! whenever the list changes.
	void setParameterList( QStringList parameters );
	
signals:
	//! Request to apply the filter named in the strings to the data
	void applyFilter( QString parameter, FilterOp op, QString value );

	//! Request to drop the filter named from the set of active filters
	void dropFilter( QString parameter, FilterOp op, QString value );

	//! Emitted when the dialog is closing (not necessarily being
	//! destroyed)
	void closing();

protected slots:
	//! Internal slot to handle new filters
	void createNewFilter();

	//! Internal slot that processes a request to remove a filter
	//! from the active list
	void removeSelectedFilters();

	//! See if any items are selected and enable or disable the
	//! remove button accordingly
	void checkSelection();

	//! See if there's valid text in the value box (making a
	//! fully valid filter), and set the Apply button accordingly
	void checkValueText( const QString& text );

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

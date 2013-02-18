// data_filter_dialog.cpp
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

#include <qcombobox.h>
#include <qlineedit.h>
#include <q3listbox.h>
#include <qpushbutton.h>
//Added by qt3to4:
#include <QCloseEvent>

#include "data_filter_dialog.h"
#include "filter_list_box_item.h"

#include "data_filter_dialog.moc"

DataFilterDialog:: DataFilterDialog( QWidget * parent, const char * name )
	: DataFilterDialogBase( parent, name )
{
	// Populate the list of relations
	for( int i = 0; i < NumFilterOps; ++i ) {
		relationComboBox->insertItem( filterOpString[i], i );
	}

	connect( applyFilterPushButton, SIGNAL( clicked() ),
			this, SLOT( createNewFilter() ) );
	connect( removeFilterPushButton, SIGNAL( clicked() ),
			this, SLOT( removeSelectedFilters() ) );
	connect( valueLineEdit, SIGNAL( textChanged( const QString& ) ),
			this, SLOT( checkValueText( const QString& ) ) );
	connect( filterListBox, SIGNAL( selectionChanged() ),
			this, SLOT( checkSelection() ) );

	// Pressing return in the line edit will automatically
	// trigger the Apply button and create a filter, because
	// the Apply button is the default for the dialog.  So
	// no need to connect it here.
}

#include <q3listbox.h>
void DataFilterDialog:: setParameterList( QStringList parameters )
{
	parameterComboBox->clear();
	parameterComboBox->insertStringList( parameters );
}

void DataFilterDialog:: createNewFilter()
{
	// Get the strings and build a filter for the list box
	QString parameter = parameterComboBox->currentText();
	FilterOp relation = (FilterOp)(relationComboBox->currentItem());
	QString value = valueLineEdit->text();

	// Put the item in our list
	filterListBox->insertItem( new FilterListBoxItem( parameter, relation,
				value ) );

	// Tell whoever is listening to apply this filter
	emit applyFilter( parameter, relation, value );
}

void DataFilterDialog:: removeSelectedFilters()
{
	// Loop over the items in reverse order an remove them.
	// Reverse ordering keeps the numbering straight as
	// items are removed.  It also removes filters in 
	// reverse order from how they were applies, which may
	// or may not matter.
	for( int i = (int)(filterListBox->count()); i >= 0; --i ) {
		if( filterListBox->isSelected( i ) ) {
			
			// Get the data for this filter and request it to
			// be dropped
			FilterListBoxItem * lbi
				= (FilterListBoxItem *)
				(filterListBox->item( i ) );
			emit dropFilter( lbi->param(), lbi->op(),
					lbi->value() );

			// Remove the item from our list
			filterListBox->removeItem( i );
		}
	}
}

void DataFilterDialog:: closeEvent( QCloseEvent * e )
{
	// Emit a closing() signal, then do whatever the
	// base class version would do.  
	emit closing();

	DataFilterDialogBase::closeEvent( e );
}

void DataFilterDialog:: checkValueText( const QString& text )
{
	applyFilterPushButton->setEnabled( ! text.isEmpty() );
}

void DataFilterDialog:: checkSelection()
{
	// See if any items are currently selected.  If so,
	// activate the remove button and return.
	for( unsigned i = 0; i < filterListBox->count(); ++i ) {
		if( filterListBox->isSelected( i ) ) {
			removeFilterPushButton->setEnabled( true );
			return;
		}
	}

	// Nothing selected; deactivate the remove button.
	removeFilterPushButton->setEnabled( false );
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


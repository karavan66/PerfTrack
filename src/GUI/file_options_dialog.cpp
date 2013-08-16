// file_options_dialog.cpp
// John May, 27 January 2005

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <q3buttongroup.h>
#include <qcheckbox.h>
#include <qlineedit.h>
#include <qpushbutton.h>
#include <qradiobutton.h>
#include <QAbstractButton>

#include "file_options_dialog.h"

#include "file_options_dialog.moc"

FileOptionsDialog:: FileOptionsDialog( QWidget * parent, const char * name )
	: FileOptionsDialogBase( parent, name )
{
	connect( colSepButtonGroup, SIGNAL( clicked( int ) ),
			this, SLOT( setDefaultExtension( int ) ) );

	connect( rowSepButtonGroup, SIGNAL( clicked( int ) ),
			this, SLOT( setDefaultExtension( int ) ) );

	connect( otherRowLineEdit, SIGNAL( textChanged( const QString& ) ),
			this, SLOT( setRowOtherButton( const QString& ) ) );

	connect( otherColLineEdit, SIGNAL( textChanged( const QString& ) ),
			this, SLOT( setColOtherButton( const QString& ) ) );

	fileExtensionLineEdit->setText( ".csv" );
}

QString FileOptionsDialog:: rowSep() const
{   
	QAbstractButton * b = rowSepButtonGroup->selected();
	
	if( b == nlRowRadioButton )
		return QString( "\n" );
    else
		return otherRowLineEdit->text();
}       
        
QString FileOptionsDialog:: colSep() const
{       
	QAbstractButton * b = colSepButtonGroup->selected();
	if( b == commaColRadioButton ) 
        	return QString( "," );
	if( b == tabColRadioButton ) 
        	return QString( "\t" );
	return otherColLineEdit->text();
}

bool FileOptionsDialog:: includeHidden() const
{
        return includeHiddenCheckBox->isChecked();
}

QString FileOptionsDialog:: fileExtension() const
{
	return fileExtensionLineEdit->text();
}

void FileOptionsDialog:: setRowSep( QString sep )
{
	// Set the button programmatically.  Don't
	// change the default extension in this case,
	// since the user will probably set it directly,
	// if desired.
	if( sep == "\n" ) {
		nlRowRadioButton->setChecked( true );
	} else {
		otherRowRadioButton->setChecked( true );
	}
}

void FileOptionsDialog:: setColSep( QString sep )
{
	// Set the button programmatically.  Don't
	// change the default extension in this case,
	// since the user will probably set it directly,
	// if desired.
	if( sep == "," ) {
		commaColRadioButton->setChecked( true );
	} else if( sep == "\t" ) {
		tabColRadioButton->setChecked( true );
	} else {
		otherColRadioButton->setChecked( true );
		otherColLineEdit->setText( sep );
	}
}
void FileOptionsDialog:: setIncludeHidden( bool flag )
{
	includeHiddenCheckBox->setChecked( flag );
}

void FileOptionsDialog:: setFileExtension( QString ext )
{
	fileExtensionLineEdit->setText( ext );
}

void FileOptionsDialog:: setDefaultExtension( int )
{
	// If we're not using newlines to separate lines, this is
	// some weird format, call it .txt
        if( rowSepButtonGroup->selected() != nlRowRadioButton ) {
		fileExtensionLineEdit->setText( ".txt" );
	} else {
		// Row separator is newlines; set extension based on
		// column separator
		QAbstractButton * b = colSepButtonGroup->selected();
		if( b == commaColRadioButton ) {
			fileExtensionLineEdit->setText( ".csv" );
		} else if( b == tabColRadioButton ) {
			fileExtensionLineEdit->setText( ".tsv" );
		} else {
			fileExtensionLineEdit->setText( ".txt" );
		}
	}
}

void FileOptionsDialog:: setColOtherButton( const QString& text )
{
	if( ! text.isEmpty() ) {
		otherColRadioButton->setChecked( true );
		setDefaultExtension( 0 );
	}

	// Do nothing if the text is blank
}

void FileOptionsDialog:: setRowOtherButton( const QString& text )
{
	if( ! text.isEmpty() ) {
		otherRowRadioButton->setChecked( true );
		setDefaultExtension( 0 );
	}

	// Do nothing if the text is blank
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


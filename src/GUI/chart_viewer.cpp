// chart_viewer.cpp
// John May, 18 October 2004

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
#include <qlayout.h>
#include <qlineedit.h>
#include <qpushbutton.h>
#include <qvalidator.h>
//Added by qt3to4:
#include <QCloseEvent>
#include "chart_viewer.h"
#include "tg_barchart.h"

#include "chart_viewer.moc"

ChartViewer:: ChartViewer( QWidget * parent,
		const char * name, Qt::WFlags fl )
	: ChartViewerBase( parent, name, fl )
{
	// Set validators on the input boxes that constrains
	// them to take only doubles; these validators will be
	// destroyed automatically when the line edits are.
	xMinLineEdit->setValidator( new QDoubleValidator( xMinLineEdit ) );
	xMaxLineEdit->setValidator( new QDoubleValidator( xMaxLineEdit ) );
	yMinLineEdit->setValidator( new QDoubleValidator( yMinLineEdit ) );
	yMaxLineEdit->setValidator( new QDoubleValidator( yMaxLineEdit ) );

	// Connect the appropriate signals and slots
	connect( xSetScaleButton, SIGNAL( clicked() ), 
			this, SLOT( resetXScale() ) );
	connect( ySetScaleButton, SIGNAL( clicked() ), 
			this, SLOT( resetYScale() ) );

	connect( xTypeGroup, SIGNAL( clicked(int) ),
			this, SLOT( resetXType( int ) ) );
	connect( yTypeGroup, SIGNAL( clicked(int) ),
			this, SLOT( resetYType( int ) ) );
	
	connect( xLogCheckBox, SIGNAL( toggled( bool ) ),
			c, SLOT( setXLogScale( bool ) ) );
	connect( yLogCheckBox, SIGNAL( toggled( bool ) ),
			c, SLOT( setYLogScale( bool ) ) );

	connect( c, SIGNAL( XScaleChanged( double, double ) ),
			this, SLOT( resetXScaleSettings( double, double ) ) );
	connect( c, SIGNAL( YScaleChanged( double, double ) ),
			this, SLOT( resetYScaleSettings( double, double ) ) );

	// Set the controls to agree with the current state
	QString label;
	label.setNum( c->xmin() );
	xMinLineEdit->setText( label );
	label.setNum( c->xmax() );
	xMaxLineEdit->setText( label );
	label.setNum( c->ymin() );
	yMinLineEdit->setText( label );
	label.setNum( c->ymax() );
	yMaxLineEdit->setText( label );

	xLogCheckBox->setChecked( c->XLogScale() );
	yLogCheckBox->setChecked( c->YLogScale() );

	// Assume that button 0 means ticks, button 1 means lines
	xTypeGroup->setButton( (c->XType() == ChartGrid::ticks) ? 0 : 1 );
	yTypeGroup->setButton( (c->YType() == ChartGrid::ticks) ? 0 : 1 );
}

ChartViewer:: ~ChartViewer()
{
}

void ChartViewer:: resetXScale()
{
	c->setXScale( xMinLineEdit->text().toDouble(),
			xMaxLineEdit->text().toDouble() );
}


void ChartViewer:: resetYScale()
{
	c->setYScale( yMinLineEdit->text().toDouble(),
			yMaxLineEdit->text().toDouble() );
}

void ChartViewer:: resetXType( int buttonId )
{
	// First button (should be id 0) is tick marks, second is grid lines
	if( buttonId == 0 ) {
		c->setXType( ChartGrid::ticks );
	} else {
		c->setXType( ChartGrid::lines );
	}
}

void ChartViewer:: resetYType( int buttonId )
{
	// First button (should be id 0) is tick marks, second is grid lines
	if( buttonId == 0 ) {
		c->setYType( ChartGrid::ticks );
	} else {
		c->setYType( ChartGrid::lines );
	}
}

void ChartViewer:: resetXScaleSettings( double min, double max )
{
	QString label;
	label.setNum( min );
	xMinLineEdit->setText( label );
	label.setNum( max );
	xMaxLineEdit->setText( label );
}

void ChartViewer:: resetYScaleSettings( double min, double max )
{
	QString label;
	label.setNum( min );
	yMinLineEdit->setText( label );
	label.setNum( max );
	yMaxLineEdit->setText( label );
}

void ChartViewer:: closeEvent( QCloseEvent * e )
{
	emit closing( this );

	// Call the base event handler
	QWidget::closeEvent( e );
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

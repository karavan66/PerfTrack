//! \file tg_barchart.h

//John May, 24 September 2004
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#ifndef TG_BARCHART_H
#define TG_BARCHART_H

#include <q3dict.h>
#include <qpainter.h>
#include <qpixmap.h>
#include <qprinter.h>
#include <qrect.h>
#include <qstring.h>
#include <q3valuevector.h>
#include <qwidget.h>
#include <qmatrix.h>
//Added by qt3to4:
#include <QPaintEvent>
#include <QResizeEvent>
#include <Q3ValueList>

#include "dataset.h"

//! Defines and draws the grid lines and tick marks for a graph.
class ChartGrid {
public:
	enum Type { ticks, lines };

	ChartGrid( double xmin, double xmax, double ymin, double ymax,
		bool logx = FALSE, bool logy = FALSE,
		Type xtype = ticks, Type ytype = lines );
	ChartGrid( double xmin, double xmax, double ymin, double ymax,
		QStringList xlabels,
		bool logx = FALSE, bool logy = FALSE,
		Type xtype = ticks, Type ytype = lines );
	~ChartGrid() {}
	void drawGrid( QPainter * painter, QRect& boundary );
	void setXScale( double min, double max );
	void setYScale( double min, double max );
	void setXTextLabels( const QStringList& labels );
	void setYTextLabels( const QStringList& labels );
	double xmin() const { return x_min; }
	double xmax() const { return x_max; }
	double ymin() const { return y_min; }
	double ymax() const { return y_max; }
	QStringList XLabels() const { return x_labels; }
	QStringList YLabels() const { return y_labels; }
	int maxXLabelChars() const { return max_x_label_chars; }
	int maxYLabelChars() const { return max_y_label_chars; }
	void setXType( ChartGrid::Type xtype ) { x_type = xtype; }
	void setYType( ChartGrid::Type ytype ) { y_type = ytype; }
	ChartGrid::Type XType() const { return x_type; }
	ChartGrid::Type YType() const { return y_type; }
	void setXLogScale( bool logx = TRUE );
	void setYLogScale( bool logy = TRUE );
	bool XLogScale() const { return log_x; }
	bool YLogScale() const { return log_y; }
	void setXLabelOffset( int pixels ) { x_label_offset = pixels; }
	void setYLabelOffset( int pixels ) { y_label_offset = pixels; }
	int XLabelOffset() const { return x_label_offset; }
	int YLabelOffset() const { return y_label_offset; }
	int XTickPixels() const { return x_tick_pixels; }
	int YTickPixels() const { return x_tick_pixels; }
	void setXTickPixels( int pixels ) { x_tick_pixels = pixels; }
	void setYTickPixels( int pixels ) { y_tick_pixels = pixels; }

protected:
	static int computeLabels( double min, double max, bool log_scale,
			QStringList& labels, int& max_label_chars );
	double x_min, x_max, y_min, y_max;
	double log_x_min, log_x_max, log_y_min, log_y_max;
	QRect boundary;
	bool log_x, log_y;
	Type x_type, y_type;
	int num_x_div, num_y_div;
	int x_tick_pixels, y_tick_pixels;
	QStringList x_labels;
	QStringList y_labels;
	int max_x_label_chars;
	int max_y_label_chars;
	int x_label_offset;
	int y_label_offset;
	bool use_x_text_labels;
	bool use_y_text_labels;
};

//! Bar chart widget, with user-settable scaling and labeling.
class TGBarChart : public QWidget {
	Q_OBJECT
public:
	TGBarChart( QWidget * parent = 0, const char * name = 0,
			Qt::WFlags f = 0 );
	~TGBarChart();

	void addDataset( const QString& setLabel, Dataset * dataset );
	void removeDataset( const QString& setLabel );
	bool hasLabel( const QString& setLabel ) const
	{	if( setLabel.isNull() ) return false;
		else return ( datasets.find( setLabel ) != 0 );
	}

	void setAutoDeleteData( bool auto_delete )
	{
		datasets.setAutoDelete( auto_delete );
	}

	bool autoDeleteData() const
	{
		return datasets.autoDelete();
	}
	
	const QStringList & getBarLabels() { return barLabels; }

	double xmin() const { return x_min; };
	double xmax() const { return x_max; };
	double ymin() const { return y_min; };
	double ymax() const { return y_max; };
	bool XLogScale() const { return log_x; }
	bool YLogScale() const { return log_y; }
	ChartGrid::Type XType() const { return grid.XType(); }
	ChartGrid::Type YType() const { return grid.YType(); }

public slots:
	void setXLogScale( bool logx = TRUE );
	void setYLogScale( bool logy = TRUE );
	void setXType( ChartGrid::Type xtype );
	void setYType( ChartGrid::Type ytype );
	void setXScale( double min, double max );
	void setYScale( double min, double max );
	bool printChart( QPrinter * printer );
signals:
	void XScaleChanged( double min, double max );
	void YScaleChanged( double min, double max );

protected:

	// Using a QPaintDevice as a parameter will let us draw the
	// chart onto a printer or other device, as well as the screen
	void drawChart( QPainter * paint );
	void clearChart( void );

	virtual void paintEvent( QPaintEvent * );
	virtual void resizeEvent( QResizeEvent * );

	QRect graphArea;
	QPixmap buffer;

	// Defines scale in data (not widget) units
	double x_min, x_max;
	double y_min, y_max;

	// Logs of limits, rounded to lower or upper power of 10
	double log_x_min, log_x_max, log_y_min, log_y_max;

	bool log_x, log_y;
	
	bool needs_redraw;
	
	unsigned max_legend_len;

	// Defines a transformation matrix that lets us define
	// a graph area in which increasing Y values go up
	// instead of down
	QMatrix xformMatrix;

	ChartGrid grid;
	
	Q3Dict<Dataset> datasets;
	QStringList viewOrder;
	QStringList barLabels;
	Q3ValueList<QColor> colorList;
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


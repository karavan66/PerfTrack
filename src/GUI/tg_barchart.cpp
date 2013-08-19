// tg_barchart.cpp
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <math.h>
#include <iostream>
#include <q3paintdevicemetrics.h>
//Added by qt3to4:
#include <Q3PointArray>
#include <QPaintEvent>
#include <QResizeEvent>
#include <Q3ValueList>
#include <QDebug>

#include "tg_barchart.h"

#include "tg_barchart.moc"

//#define DOUBLE_BUFFER
//#define TEXT_LABEL_ANGLE_DEG (22.5)
#define TEXT_LABEL_ANGLE_DEG (5)
#define TEXT_LABEL_ANGLE_RAD ( TEXT_LABEL_ANGLE_DEG * M_PI / 180.0 )

// This utility function is used by both classes.  It's
// static to this file but not a member of either class.
static void setLogLimits( double min, double max,
		double& log_min, double& log_max )
{

	// Check for values that don't have valid logs
	if( max <= 0 && min <= 0 ) {
		// Pick an arbitrary range
		max = 10;
		min = 0.1;		
	}

	if( min > 0 ) {
		// Round down the log of the minimum
		log_min = floor( log10( min ) );
	}
	if( max > 0 ) {
		// Round up the log of the maximum
		log_max = ceil( log10( max ) );
	}

	// If one or the other endpoint is invalid, pick a
	// value two orders of magnitude away from the other
	if( max <= 0 ) {
		log_max = log_min + 2;
	}
	if( min <= 0 ) {
		log_min = log_max - 2;
	}
}

TGBarChart::TGBarChart( QWidget * parent, const char * name, Qt::WFlags f )
	: QWidget( parent, name, f ),
	graphArea( 0, 0, 10000, 10000 ),
	x_min( 0 ), x_max( 1 ), y_min( 0 ), y_max( 1 ),
	log_x( false ), log_y( false ),
	needs_redraw( true ),
	max_legend_len( 0 ),
	xformMatrix( 1, 0, 0, -1, 0, 0 ),
	grid( x_min, x_max, y_min, y_max )

{
	// Pick a series of colors to use; define them now so
	// we pay the cost of contacting the window server only once
	colorList.append( QColor("red") );
	colorList.append( QColor("yellow") );
	colorList.append( QColor("blue") );
	colorList.append( QColor("green") );
	colorList.append( QColor("orange") );
	colorList.append( QColor("cyan") );
	colorList.append( QColor("violet") );

	// Use the text background color instead of the regular
	// widget background for better contrast
	setBackgroundMode( Qt::PaletteBase );
}

TGBarChart:: ~TGBarChart()
{
}

void TGBarChart::addDataset( const QString& setLabel, Dataset * dataset )
{
	// Can't use null string for label; empty string is OK
	QString label = ( setLabel.isNull() ) ? QString("") : setLabel;

	// Store a pointer to the dataset
	datasets.insert( label, dataset );

	// Add this dataset to the end of the list of items
	// to draw
	viewOrder.append( label );

	// Keep track of the longest dataset label seen
	if( label.length() > max_legend_len )
		max_legend_len = label.length();

	// Update the list of bar labels.  This list should
	// be the union of all labels in the all datasets.  The
	// order of items in this list determines the order in
	// which the bars will be displayed.  The first dataset
	// added determines the general order, and if new items
	// appear in subsequent datasets, they are added before
	// the position in the current list where the next matching
	// item in the new list appears.  Any items that appear in
	// both the current list an a new list must be in the same
	// order.  This should be the common case, and anything
	// else would require a relatively slow algorithm to find
	// all the matches decide on an order to insert the new
	// items.  If the current list is A B C D, and the new
	// list is Z Y A X D W, then the merged list should be
	// Z Y A B C X D W
	
	QStringList::iterator cur;
	Dataset::iterator new_data = dataset->begin(), next_add = new_data;
	int num_bar_labels = barLabels.size();
	// Go through the current list and look for matching items
	// in the new list.  Also keep track of longest label seen.
	for( cur = barLabels.begin(); num_bar_labels > 0; ++cur, --num_bar_labels ) {
		// Find the next item in the new list that matches
		// the current item in the old list
		while( new_data != dataset->end() &&
				(*new_data).x != *cur ) 
			++new_data;
		// No match; look at next item in new list
		if( new_data == dataset->end() ) {
			new_data = next_add;
			continue;
		}

		// Add items from the new list to this one
		while( next_add != new_data ) {
			barLabels.insert( cur, (*next_add).x );
//			if( longest_label.length() < (*next_add).x.length() ) {
//				longest_label = (*next_add).x;
//			}
			++next_add;
		}
		++next_add;
		++new_data;	// Move past matching item in current list
		if( new_data == dataset->end() ) break;
	}

	// If there are new any items left, add them to the end of the
	// old list
	while( next_add != dataset->end() ) {
		barLabels.append( (*next_add).x );
//		if( longest_label.length() < (*next_add).x.length() ) {
//			longest_label = (*next_add).x;
//		}
		++next_add;
	}

	// Use these labels for the graph
	grid.setXTextLabels( barLabels );

	needs_redraw = TRUE;
	update();
}

void TGBarChart::removeDataset( const QString& setLabel )
{
	// We changed null set labels to empty strings when they were added
	QString label = ( setLabel.isNull() ) ? QString("") : setLabel;
	// Remove the item from our list; it will be deleted if
	// chart has been set to take ownership of its data.
	datasets.remove( label );

	// Take this item out of the list of datasets to view
	viewOrder.remove( label );

	// NOTE: we don't try to remove labels that appear only in
	// this list from barLabels; that would be very expensive
	// with current data structures.
	needs_redraw = TRUE;
	update();
}

void TGBarChart::setXScale( double min, double max )
{
	if( min >= max ) return;
	x_min = min;
	x_max = max;
	setLogLimits( min, max, log_x_min, log_x_max );
	grid.setXScale( min, max );

	needs_redraw = TRUE;
	update();
	emit XScaleChanged( min, max );
}

void TGBarChart::setYScale( double min, double max )
{
	if( min >= max ) return;
	y_min = min;
	y_max = max;
	setLogLimits( min, max, log_y_min, log_y_max );
	grid.setYScale( min, max );

	needs_redraw = TRUE;
	update();
	emit YScaleChanged( min, max );
}

void TGBarChart::setXLogScale( bool logx )
{
	log_x = logx;
	grid.setXLogScale( log_x );
	needs_redraw = TRUE;
	update();
}

void TGBarChart::setYLogScale( bool logy )
{
	log_y = logy;
	grid.setYLogScale( log_y );
	needs_redraw = TRUE;
	update();
}

void TGBarChart::setXType( ChartGrid::Type xtype )
{
	grid.setXType( xtype );
	needs_redraw = TRUE;
	update();
}

void TGBarChart::setYType( ChartGrid::Type ytype )
{
	grid.setYType( ytype );
	needs_redraw = TRUE;
	update();
}

void TGBarChart::drawChart( QPainter * paint )
{
	// Sanity check
	if( ! paint->isActive() ) {
		qWarning( "drawChart called with inactive painter!" );
		return;
	}

	// Get the dimensions of the paint device.  This may
	// not be the best approach, since the device metrics
	// might not be available for a printer.  Can we work
	// only in "model" coordinates?  FIX
	Q3PaintDeviceMetrics dev( paint->device() );

	// Define a logical drawing area with the origin at
	// the lower-left corner.  graphArea defines the coordinate
	// system we want to use for the graphing area itself
	// (excluding margins).  Our transformation matrix flips
	// the direction of the axis, and the window shifts it down.
	// We need to compute the overall width (in graph area units)
	// of the window so we can shift it down to get the origin
	// in the right place.  The size of the margins depends on
	// the size of the labels, which are computed in widget 
	// (i.e, device) units.  chartArea is the overall size of the
	// chart (including the graph and the margins) in graphArea
	// unit.
	// chartArea.width = graphArea.width + left_margin + right_margin
	// left_margin  = chartArea.width * label_width / widget_width
	// right_margin = 0.05 * chartArea.width
	// so chartArea.width = 1.05 * graphArea.width
	// 			/ (1 - label_width / widget_width)
	// The 0.05 margin is increased if the rightmost label would
	// be too wide for the page.
	// There's a similar calcuation to get the height, except
	// that the top margin depends contains a legend, so its
	// height also depends on the text parameters:
	// chartArea.height = graphArea.height
	// 	/ ( 1 - ( label_height + legend_height ) / widget_height )

	// Compute the width of the y axis labels in window units
	// We use a string made of M's (a wide letter) as long as
	// the longest label.  We don't compute the width of the
	// label itself because labels with the same number of
	// characters may have different widths, and it would be
	// expensive to compute the pixel width of each label here.
	// The offsets added are the distance from the label to
	// the gridline (in device units)
	QFontMetrics fm = paint->fontMetrics();
	int em_width = fm.width( QChar('M') );
	int text_height = fm.height();
	int left_label_width = em_width * grid.maxYLabelChars()
		+ 2 * grid.YLabelOffset();	// add offset for both sides

	// Now do the x axis labels.  Since they are tilted, we need
	// to consider the width as well as the height of the label in
	// computing the vertical space they occupy.  
	int bottom_label_height = int(
			sin( TEXT_LABEL_ANGLE_RAD )
				* grid.maxXLabelChars() * em_width
			+ cos( TEXT_LABEL_ANGLE_RAD ) * text_height
			) + 2 * grid.XLabelOffset();

	// The rightmost legend can extend into the right margin.
	// We need to make sure there is enough room for it.  We can
	// look at the actual label and not a mockup with Ms because
	// we didn't have to precompute the longest label.

	// Box pivots from top left corner, so height doesn't affect
	// projection to right
	int right_label_width = int( cos( TEXT_LABEL_ANGLE_RAD )
			* fm.width( grid.XLabels().last() ) )
			+ grid.YLabelOffset();
	
	// Test to see whether the label would extend past the
	// standard margin of 0.05 * graph width.  We assume the
	// label starts 1/N in from the right side of the graph,
	// where N is the number of divisions.  Normally, in device
	// units, graph_width = (dev.width - label_width) / 1.05.
	// The test is whether
	// right_label_width > graph_width/N + 0.05*graph_width,
	// so we compute the test as
	// right_label_width > ((dev.width - label_width)/1.05) * (0.05 + 1/N)
	// If the label extends past the right margin, we compute
	// the overall width as follows:
	// chartArea.width = graphArea.width * ( 1 - 1/N )
	// 	/ ( 1 - ( label_width + right_label_width ) / device_width )
	// This computation fails for N = 1, but in that case the label
	// doesn't fit in the window anyway.
	int plot_width;
	int label_count = grid.XLabels().count();
	if( label_count > 1 &&
			right_label_width > ( ( dev.width() - left_label_width )
			/  1.05 ) * ( 0.05 + 1 / double(label_count) ) ) {
		// Label would go past right margin
		plot_width
			= graphArea.width() * ( 1 - 1 / double(label_count ) )
			/ ( 1 - ( left_label_width + right_label_width )
					/ double( dev.width() ) );
	} else {
		// Normal calculation
		plot_width =  int( 1.05 * graphArea.width()
			/ ( 1 - double( left_label_width ) / dev.width() ) );
	}
	int left_margin = ( left_label_width * plot_width ) / dev.width();
	

	// Compute the space needed for the legends.
	// The boxes for the colors will be the height of a text
	// box and twice the width of an M.  So the legend will
	// be laid out horizontally as:
	// em-space legend box em-space text label em-space ...
	// So a legend width is the em-width * (label-chars + 5)
	// The legend will be centered in a vertical box two
	// textboxes high.
	// We then figure out how many labels fit across
	// the margin by computing the length of the longest legend
	// (in device units) and seeing how many times it will fit
	// in the width of the widget.  Then we allocate enough rows
	// of legends to hold all we have.
	int legend_textbox_width = em_width * (max_legend_len + 5 );
	int leg_across = dev.width() / legend_textbox_width;
	if( leg_across == 0 ) leg_across = 1;	// make room for at least 1
	int leg_down = int( ceil( double( datasets.count() ) / leg_across ) );
	int legend_height = 2 * leg_down * text_height;

	// Now we can get the height of the plot
	int plot_height = int( graphArea.height()
			/ ( 1 - double( bottom_label_height + legend_height )
					/ dev.height() ) );
	int top_margin = ( legend_height * plot_height ) / dev.height();

	// Set the position of the origin in the widget and the area
	// to be displayed
	paint->setWindow( -left_margin, -( graphArea.bottom() + top_margin ),
			plot_width, plot_height );

	// Set the direction of the axes
	paint->setWorldMatrix( xformMatrix, FALSE );
	
	// Draw the grid
	grid.drawGrid( paint, graphArea );

	// Set up locations to draw legends; these are in device coordinates
	// because that's how we have to draw the text
	int legend_box_width = em_width * 2;
	int legend_box_height = text_height;
	int next_legend_x = legend_box_width / 2; //legend_box.width() / 2;
	int next_legend_y = legend_box_height / 2; //legend_box.height() / 2;

	// Iterate over all our datasets, in the order
	// given by viewOrder
	int setCount;
	int nSets = datasets.count();
	// Extra factor of 0.8 makes bars a little narrower, so
	// there will be some space between groups of bars
	int barWidth = int( graphArea.width() * 0.8 / (x_max - x_min) )
		/ nSets;
	double x_pix_scale = double( graphArea.width())
				/ (log_x ?  ( log_x_max - log_x_min )
					: ( x_max - x_min ) );
	double y_pix_scale = double( graphArea.height())
				/ (log_y ?  ( log_y_max - log_y_min )
					: ( y_max - y_min ) );
	QStringList::Iterator it;
	Q3ValueList<QColor>::iterator cit;
	for( it = viewOrder.begin(), cit = colorList.begin(), setCount = 0;
			it != viewOrder.end(); ++it, ++cit, ++setCount ) {
		// Get the next dataset by looking it up based on the label
		Dataset * curdata = datasets[*it];

		// Get the next color; cycle through the list as
		// often as needed.  Then set the brush using that color
		if( cit == colorList.end() ) {
			cit = colorList.begin();
		}
		QBrush brush( *cit );

		// Now iterate over the known labels and draw the bars
		int barcount;
		QStringList::Iterator lit;
		Dataset::iterator dit;
		
		for( lit = barLabels.begin(), dit = curdata->begin(),
				barcount = 0;
				lit != barLabels.end() && dit != curdata->end();
				++lit, ++barcount ) {

			// Verify that this label appears in the current
			// dataset.  Only advance this dataset if the
			// label is there; otherwise, go to the next label
			if( (*dit).x != *lit ) continue;

			// Look up the corresponding y value
			double y = (*dit).y;
			++dit;

			// Compute x position in pixels; make room for all
			// data series
			int x_pix;
			if( log_x ) {

				// Recompute the bar width for this position
				//
				// Item 0 is a special case, equivalent to
				// setting barcount to x_min and
				// barcount+1 = 1
				if( barcount == 0 ) {
					barWidth = int( -log_x_min * x_pix_scale
							* 0.8 / nSets );
					x_pix = setCount * barWidth;
				} else {
					barWidth = int(
						log10( double( barcount + 1 )
								/ barcount )
							* 0.8 * x_pix_scale
						/ nSets );
					x_pix = int( ( log10( double(barcount) )
								- log_x_min )
							* x_pix_scale )
						+ setCount * barWidth;
				}

			} else {
				x_pix = int( ( barcount - x_min )
							* x_pix_scale )
					+ setCount * barWidth;
			}

			// Compute y position in pixels.  Note that
			// count goes from top to bottom, so we
			// subtract from the lower boundary of the
			// graph area.
			int y_pix;
			if( log_y ) {
				y_pix = int( ( log10( y ) - log_y_min )
						* y_pix_scale );
			} else {
				y_pix =  int( ( y - y_min ) * y_pix_scale );
			}

			// Draw the rectangle in the buffer
			paint->setBrush( brush );
			// Do we need to clip?
			if( x_pix < 0 ) {
				int narrowBarWidth = barWidth + x_pix;
				if( narrowBarWidth <= 0 ) continue;
				paint->drawRect( 0, 0, narrowBarWidth, y_pix );
			} else if( x_pix + barWidth > graphArea.right() ) {
				if( x_pix > graphArea.right() ) continue;
				int narrowBarWidth = graphArea.right() - x_pix; 
				if( narrowBarWidth <= 0 ) continue;
				paint->drawRect( x_pix, 0,
						narrowBarWidth, y_pix );
			} else {
				// No clip; draw as computed
				paint->drawRect( x_pix, 0, barWidth, y_pix );
			}
			
		}
		// Draw the legend at the top of the graph; need to use
		// untransformed coordinates to get text right
		paint->save();
		paint->resetXForm();
		paint->drawRect( next_legend_x, next_legend_y,
				legend_box_width, legend_box_height );
		paint->drawText( next_legend_x + 3 * legend_box_width / 2,
				next_legend_y, legend_textbox_width,
				text_height, 
				Qt::AlignAuto | Qt::AlignVCenter, *it );

		next_legend_x += legend_textbox_width;

		// If the next legend won't fit on this row, start on
		// the next row
//		if( next_legend_x + legend_textbox_width > dev.width() ) {
		if( ( setCount + 1 ) % leg_across == 0 ) {
			next_legend_x = legend_box_width / 2;
			next_legend_y += legend_box_height * 2;
		}
		
		paint->restore();
	}

	needs_redraw = FALSE;
}

bool TGBarChart::printChart( QPrinter * printer )
{
	// Create a painter to use with this printer
	// and then call drawChart to do the painting.
	QPainter paint;
	if( paint.begin( printer ) == false ) {
		return false;
	}
	drawChart( &paint );
	paint.end();

	return true;
}

void TGBarChart::clearChart( void )
{
	// Use the background color designed for text
	buffer.fill( colorGroup().base() );
}

void TGBarChart::paintEvent( QPaintEvent * )
{
	// Create a new painter to handle this event
	// If the chart has been modified, need to repaint it completely
	// and draw the whole thing into the widget
	QPainter paint;
// Need to test this on something other than a Mac, because even
// using X there, no repaint events get generated when objects are
// covered and then exposed.  We might be able to forego the 
// needs_redraw flag if other systems behave the same way.
// If we do need this flag, we have to add some code to generate
// a redraw on window activation/deactivation events because the
// colors can change on some systems.
//	if( needs_redraw ) {
#ifdef DOUBLE_BUFFER
		buffer.fill( colorGroup().base() );
		paint.begin( &buffer, this );
		drawChart( &paint );
		paint.end();
		bitBlt( this, 0, 0, &buffer );
#else
		paint.begin( this );
		drawChart( &paint );
		paint.end();
#endif
//		fprintf( stderr, "repainting everything\n" );
//	} else {
		// If nothing has changed, just copy the relevant
		// parts of the buffer into the widget
//		QRect r = event->rect();
//		bitBlt( this, r.topLeft(), &buffer, r );
//		fprintf( stderr, "painting %d x %d box at %d,%d\n",
//				r.width(), r.height(), r.x(), r.y() );
//	}

}

void TGBarChart::resizeEvent( QResizeEvent * event )
{
	// Resize the working buffer and paint it the base color
	buffer.resize( event->size() );

	// Since the scale is changing, we have to redraw everything
	needs_redraw = TRUE;
	update();
}

ChartGrid::ChartGrid( double xmin, double xmax, double ymin, double ymax,
		bool logx, bool logy, Type xtype, Type ytype )
	: x_min( xmin ), x_max( xmax ), y_min( ymin ), y_max( ymax ),
	log_x( logx ), log_y( logy ),
	x_type( xtype ), y_type( ytype ),
	x_tick_pixels( 5 ), y_tick_pixels( 5 ),
	x_label_offset( 5 ), y_label_offset( 5 ),
	use_x_text_labels( false ), use_y_text_labels( false )
{
	setLogLimits( xmin, xmin, log_x_min, log_x_max );
	setLogLimits( ymin, ymin, log_y_min, log_y_max );

	num_x_div = computeLabels( xmin, xmax, logx, x_labels,
			max_x_label_chars );
	num_y_div = computeLabels( ymin, ymax, logy, y_labels,
			max_y_label_chars );
}

int ChartGrid::computeLabels( double min, double max, bool log_scale,
		QStringList& labels, int& max_label_chars )
{
	double label_min, label_max;

	// Compute the number of divisions.
	// For linear scale, we made up this heuristic to
	// give us a number of divisions between about 2 and 20, regardless
	// of the absolute difference between min and max
	int num_div;
	double diff;
	if( !log_scale ) {
		diff = max - min;
		double scale = pow( 10, floor( log10( diff ) - 0.3 ) );
		num_div = int( diff / scale );
		label_min = min;
		label_max = max;
	} else {
		num_div = int( max - min );
		label_min = pow( 10, min );
		label_max = pow( 10, max );
	}

	// Precompute the text labels for the axis so we don't
	// have to do it on the fly while painting the screen.
	QString label;
	labels.clear();
	int i;
	max_label_chars = 0;
	if( log_scale ) {
		label.sprintf( "%0.0lg", pow( 10, min ) );
		labels.append( label );
		for( i = 1; i <= num_div; ++i ) {
			label.sprintf( "%0.0lg",
					pow( 10, (min + i ) ) );
			labels.append( label );
			int width = label.length();
			if( width > max_label_chars ) {
				max_label_chars = width;
			}
		}
	} else {
		label.sprintf( "%0.1lf", label_min );
		labels.append( label );
		for( i = 1; i <= num_div; ++i ) {
			label.sprintf( "%0.1lf",
					label_min +  diff * double(i)
							/ num_div );
			labels.append( label );
			int width = label.length();
			if( width > max_label_chars ) {
				max_label_chars = width;
			}
		}
	}

	return num_div;
}

void ChartGrid::drawGrid( QPainter * paint, QRect& boundary )
{
	// Save the current state of the painter (which we assume
	// has been properly inialized to the paint device)
	// Also assume that the painter has set the transformations
	// it wants already.
	paint->save();

	// Draw the axes; we have to refer to the origin as if it were
	// at the top left corner, even though it may have been
	// transformed visually
	paint->drawLine( boundary.topLeft(), boundary.bottomLeft() );
	paint->drawLine( boundary.topLeft(), boundary.topRight() );

	// Tick lengths are given in screen pixels units (so they'll
	// be the same length regardless of scaling); translate
	// these to our scaled coordinates.
	int x_ticks_scaled = x_tick_pixels * paint->window().width()
					/ paint->viewport().width();
	int y_ticks_scaled = y_tick_pixels * paint->window().height()
					/ paint->viewport().height();
	Q3PointArray x_points;
	// Draw the x axis, and save the list of points where the
	// ticks go, so we can use them for the labels.
	int y_end = ( x_type == ticks ) ? boundary.top() - y_ticks_scaled
		: boundary.bottom();
	int x_pix;
	int i;
	if( ! use_x_text_labels ) {
		int x_interval = boundary.width() / num_x_div;
		x_points.resize( num_x_div + 1 );
		x_points.setPoint( 0, boundary.topLeft() );	// origin
		for( x_pix = boundary.left() + x_interval, i = 1;
				i <= num_x_div;
				x_pix += x_interval, ++i ) {
			paint->drawLine( x_pix, boundary.top(), x_pix, y_end );
			x_points.setPoint( i, x_pix, boundary.top() );

			// Add subdivisions for log scale axis; these go
			// *before* the line we just drew, since we need to
			// fill in the interval whose end this line marks.
			if( log_x ) {
				int subdiv;
				for( subdiv = 2; subdiv < 10; ++subdiv ) {
					int sub_pix = x_pix - x_interval +
						int( log10( double(subdiv) )
								* x_interval );
					paint->drawLine( sub_pix,
							boundary.top(),
							sub_pix, y_end );
				}
			}
		}

		// Add the axis point, which lie just outside the graph area
		if( i <=  num_x_div ) {
			x_points.setPoint( num_x_div, boundary.right(),
					boundary.top () );
		}
	} else {
		// Computing position for each item, regardless of
		// number of divisions computed
		int num_intervals = int( ceil( x_max ) - floor( x_min ) );
		x_points.resize( num_intervals );
		double x_pix_scale = double( boundary.width() )
			/ (log_x ? ( log_x_max - log_x_min )
					: ( x_max - x_min ) );
		double loc;
		i = 0;
		// Add an extra label location at the left end if
		// x_min isn't a whole number.
		if( floor( x_min ) != x_min )
			x_points.setPoint( i++, 0, boundary.top() );
		for( loc = ceil( x_min ); loc < ceil( x_max ); ++loc, ++i ) {
			if( log_x ) {
				x_pix = int( ( log10( loc ) - log_x_min )
						* x_pix_scale );
			} else {
				x_pix = int( ( loc - x_min ) * x_pix_scale );
			}
			paint->drawLine( x_pix, boundary.top(), x_pix, y_end );
			x_points.setPoint( i, x_pix, boundary.top() );
		}
	}

	// Draw the y axis
	int y_interval = boundary.height() / num_y_div;
	int x_end = ( y_type == ticks ) ? boundary.left() - x_ticks_scaled
		: boundary.right();
	int y_pix;
	Q3PointArray y_points( num_y_div + 1);
	y_points.setPoint( 0, boundary.topLeft() );	// origin
	for( y_pix = boundary.top() + y_interval, i = 1;
			i <= num_y_div;
			y_pix += y_interval, ++i ) {
		paint->drawLine( boundary.left(), y_pix, x_end, y_pix );
		y_points.setPoint( i, boundary.left(), y_pix );
		// Add subdivisions for log scale axis
		if( log_y ) {
			int subdiv;
			for( subdiv = 2; subdiv < 10; ++subdiv ) {
				int sub_pix = y_pix - y_interval +
					int( log10( double(subdiv) )
							* y_interval );
				paint->drawLine( boundary.left(), sub_pix,
						x_end, sub_pix );
			}
		}
	}

	// Add the axis point, which may lie just outside the graph area
	if( i <=  num_y_div ) {
		y_points.setPoint( num_y_div, boundary.left(),
				boundary.bottom() );
	}

	// Draw the axis labels; do this separately from above because
	// the view is transformed, and we need to put it back into its
	// regular orientation so we can draw the text in the correct
	// direction.  Also, if we're using text labels instead of
	// numeric labels, they are drawn differently.
	
	QFontMetrics fm = paint->fontMetrics();
	
	// Put the points in device coordinates
	Q3PointArray x_dev_points = paint->xForm( x_points );
	Q3PointArray y_dev_points = paint->xForm( y_points );

	// Now move all the points a few pixels outide the axis
	x_dev_points.translate( 0, x_label_offset );
	y_dev_points.translate( -y_label_offset, 0 );

	// Disable transformations
	paint->resetXForm();
	QStringList::Iterator sit;
	Q3PointArray::Iterator pit;
	if( use_x_text_labels ) {
		// Find the label for the leftmost point.  This item
		// may not appear at the far left of the chart if
		// x_min is negative.

		sit = x_labels.begin();
		while ((*sit).toDouble() < 0.0 && sit != x_labels.end()) {
			sit++;
		}
		unsigned pindex = ( x_min >= 0 ) ? 0 : -int( floor( x_min ) ); 
		for( ; pindex < x_dev_points.count() && sit != x_labels.end();
				++pindex, ++sit ) {
			paint->save();
			// Move origin to where we want to start writing
			// (add 5 pixel fudge to keep tilted text under
			// the area of interest)
			paint->translate( x_dev_points[pindex].x() + 5,
					x_dev_points[pindex].y() );
			paint->rotate( TEXT_LABEL_ANGLE_DEG );
			QRect text_box = fm.boundingRect( *sit );
			paint->drawText( 0, text_box.height(), *sit );
			paint->restore();
		}
	} else {
		// Using numeric labels
		for( pit = x_dev_points.begin(), sit = x_labels.begin();
			pit != x_dev_points.end() && sit != x_labels.end();
				++pit, ++sit) {
			QRect text_box = fm.boundingRect( *sit );
			paint->drawText( (*pit).x() - text_box.width() / 2,
					(*pit).y() + text_box.height(),
					*sit );
		}
	}

	for( pit = y_dev_points.begin(), sit = y_labels.begin();
			pit != y_dev_points.end() && sit != y_labels.end();
			++pit, ++sit) {
		QRect text_box = fm.boundingRect( *sit );
		paint->drawText( (*pit).x() - text_box.width(),
				(*pit).y() + text_box.height() / 3,
				*sit );
	}

	// Restore the previous state of the painter
	paint->restore();
}

void ChartGrid::setXScale( double min, double max )
{
	if( min >= max ) return;
	x_min = min;
	x_max = max;
	setLogLimits( min, max, log_x_min, log_x_max );
	if( use_x_text_labels ) return;
	if( log_x ) {
		num_x_div = computeLabels( log_x_min, log_x_max, log_x,
				x_labels, max_x_label_chars );
	} else {
		num_x_div = computeLabels( min, max, log_x, x_labels,
				max_x_label_chars );
	}
}

void ChartGrid::setYScale( double min, double max )
{
	if( min >= max ) return;
	y_min = min;
	y_max = max;
	setLogLimits( min, max, log_y_min, log_y_max );
	if( use_y_text_labels ) return;
	if( log_y ) {
		num_y_div = computeLabels( log_y_min, log_y_max, log_y,
				y_labels, max_y_label_chars );
	} else {
		num_y_div = computeLabels( min, max, log_y, y_labels,
				max_y_label_chars);
	}
}

void ChartGrid::setXLogScale( bool logx )
{
	log_x = logx;
	if( use_x_text_labels ) return;
	if( log_x ) {
		num_x_div
			= computeLabels( log_x_min, log_x_max, logx, x_labels,
					max_x_label_chars );
	} else {
		num_x_div = computeLabels( x_min, x_max, logx, x_labels,
				max_x_label_chars );
	}
}

void ChartGrid::setYLogScale( bool logy )
{
	log_y = logy;
	if( use_y_text_labels ) return;
	if( log_y ) {
		num_y_div
			= computeLabels( log_y_min, log_y_max, logy,
					y_labels, max_y_label_chars );
	} else {
		num_y_div = computeLabels( y_min, y_max, logy, y_labels,
				max_y_label_chars );
	}
}

void ChartGrid::setXTextLabels( const QStringList& labels )
{
	x_labels = labels;
	
	// Determine the widest label
	QStringList::const_iterator it;
	max_x_label_chars = 0;
	for( it = labels.begin(); it != labels.end(); ++it ) {
		int width = (*it).length();
		if( width > max_x_label_chars ) {
			max_x_label_chars = width;
		}
	}

	use_x_text_labels = true;
}

void ChartGrid::setYTextLabels( const QStringList& labels )
{
	y_labels = labels;

	// Determine the widest label
	QStringList::const_iterator it;
	max_y_label_chars = 0;
	for( it = labels.begin(); it != labels.end(); ++it ) {
		int width = (*it).length();
		if( width > max_y_label_chars ) {
			max_y_label_chars = width;
		}
	}

	use_y_text_labels = true;
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


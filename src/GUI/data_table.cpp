// data_table.cpp
// John May, 21 January 2005

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <qpainter.h>
#include <q3simplerichtext.h>
#include <qstyle.h>

// For performance tuning only
#include <qdatetime.h>	
//Added by qt3to4:
#include <Q3TextStream>
#include <Q3SqlCursor>
#include <Q3MemArray>

#include "data_table.h"

#include "data_table.moc"

#define INDEX_HEADING QString("RESULT_ID")

void DataTable:: populateTable( Q3SqlCursor cursor )
{
	// Remove existing data
	clearAll();

	// Initialize the index column to an impossible value
	index_col = cursor.count();

	// Create the columns.  Also, find the special "index"
	// column.  It holds key values that will be used for
	// assigning data to the right rows when we add new
	// new columns later.  We store these values in 
	// a map so we can quickly find the corresponding rows.
	insertColumns( 0, cursor.count() );
	for( unsigned i = 0; i < cursor.count(); ++i ) {
		horizontalHeader()->setLabel( i, cursor.fieldName( i ) );

		// Look for the index column and hide it
		if( cursor.fieldName( i ).upper() == INDEX_HEADING ) {
			index_col = i;
			hideColumn( i );
		}

	}

	// Initialize the column types; assume numbers until
	// we see a string
	colType.resize( cursor.count(), TwoDTable<QString>::Numeric );

	fprintf( stderr, "starting to read data %s\n",
		qPrintable(QTime::currentTime().toString("hh:mm:ss.zzz")) );

#if 0
	// Add the data, row by row.
	int row = 0;
	while( cursor.next() ) {
//		insertRows( row, 1 );
		for( unsigned field = 0; field < cursor.count(); ++field ) {
			QString text = cursor.value( field ).toString();
//			setText( row, field, text );
			// Save the key value in the map
//			if( field == index_col ) {
//				indexRow[text] = row;
//			}
		}
		++row;
	}
#endif
	// Populate the internal table
	int row = 0;
	while( cursor.next() ) {
		// Create a vector for this row
		std::vector<QString> vec( cursor.count() );
		for( unsigned field = 0; field < cursor.count(); ++field ) {
			QString val = cursor.value( field ).toString();
			vec[field] = val;
			// Save the key value in the map
			if( field == index_col ) {
				indexRow[val] = row;
			}

			// See if this col has any non-numbers in it
			bool isDouble;
			if( colType[field] == TwoDTable<QString>::Numeric
					&& ! val.isEmpty() ) {
				(void) val.toDouble( &isDouble );
				if( !isDouble ) {
					colType[field]
						= TwoDTable<QString>::String;
				}
			}
		}

		// Append the vector to tableData
		tableData.push_back( vec );
		++row;
	}
	
	insertRows( 0, row );

	fprintf( stderr, "done reading data %s\n",
		qPrintable(QTime::currentTime().toString("hh:mm:ss.zzz")) );

#if 0
	for( unsigned i = 0; i < cursor.count(); i++ ) {
		printf( "Column %d (%s) is a %s\n",
				i, cursor.fieldName( i ).latin1(),
				(colType[i] == TwoDTable<QString>::String)
				? "String" : "Number" );
	}
#endif

	// Apply any existing filters to the table
	Filter * f;
	for( f = filters.first(); f != 0; f = filters.next() ) {
		applyFilter( f );
	}
}

void DataTable:: populateTable( Q3TextStream& ts, QString colSep,
		QString rowSep )
{
	// Remove existing data
	clearAll();

	// Get the text and split it into lines
	QStringList lines = QStringList::split( rowSep, ts.read() );

	// Get the first line and extract the column headers
	QStringList::const_iterator rit = lines.begin();
	QStringList headers = QStringList::split( colSep, *rit );

	// Initialize the column types
	colType.resize( headers.count(), TwoDTable<QString>::Numeric );

	// Initialize the index column to an impossible value
	index_col = headers.count();

	addColumns( headers );

	// Now go through the rest of the lines and add the data to the table
	insertRows( 0, lines.count() - 1 );
	QStringList::const_iterator cit;
	unsigned r, c;
	for( ++rit, r = 0; rit != lines.end(); ++rit, ++r ) {
		// Split the current line into fields; empty entries are OK here
		QStringList fields = QStringList::split( colSep, *rit, true );

		// Put each field entry in a vector
		std::vector<QString> vec( fields.count() );
		for( cit = fields.begin(), c = 0; cit != fields.end();
				++cit, ++c ) {
			vec[c] = *cit;
			// Save the key value in the map
			if( c == index_col ) {
				indexRow[*cit] = r;
			}
		}

		// Append the vector to tableData
		tableData.push_back( vec );
	}
	
	// Apply any existing filters to the table
	Filter * f;
	for( f = filters.first(); f != 0; f = filters.next() ) {
		applyFilter( f );
	}
}

void DataTable:: addColumnData( QString name, Q3SqlCursor cursor )
{
	// Find the relevant column; if it doesn't exists, silently return
	int c;
	for( c = 0; c < numCols(); ++c ) {
		if( horizontalHeader()->label( c ) == name ) break;
	}

	if( c >= numCols() ) return;

	// Put each value in the row that corresponds with the index
	// value given in the first field of the cursor.  ASSUMES
	// THAT addColumns has been called already to reserve space
	// in tableData.
	QMap<QString,int>::iterator row_it;
	while( cursor.next() ) {
		// Index value is always in field number 0
		row_it = indexRow.find( cursor.value(0).toString() );

		// Skip this entry if no matching item is in the table
		if( row_it == indexRow.end() ) continue;

		// Data value is in field 1
		QString val = cursor.value(1).toString();
		tableData[*row_it][c] = val;

		// See if this col has any non-numbers in it
		bool isDouble;
		if( colType[c] == TwoDTable<QString>::Numeric
				&& ! val.isEmpty() ) {
			(void) val.toDouble( &isDouble );
			if( !isDouble ) {
				colType[c] = TwoDTable<QString>::String;
			}
		}
	}

	updateContents();
}

void DataTable:: addColumns( QStringList headers )
{
	int current_cols = numCols();
	insertColumns( current_cols, headers.count() );

	// Make these new columns numeric until we learn otherwise
	colType.resize( current_cols + headers.count(),
			TwoDTable<QString>::Numeric );

	// Make sure there's room in the table for the new data.  This
	// has to happen before the column labels are set, because
	// that can cause cells in that column to be repainted, which
	// in turn will request data from the corresponding rows of
	// this table.
	tableData.resize( tableData.rows(), numCols() );

	QStringList::const_iterator cit;
	int c;
	for( cit = headers.begin(), c = current_cols; cit != headers.end();
			++cit, ++c ) {
		horizontalHeader()->setLabel( c, *cit );

		// Look for the index column and hide it
		// (but it might not exist in the new columns)
		if( (*cit).upper() == INDEX_HEADING ) {
			index_col = c;
			hideColumn( c );
		}
	}

}

void DataTable:: removeColumn( int col )
{
	// Need to remove both the visible column from the table
	// and the underlying data in tableData.
	Q3Table::removeColumn( col );

	tableData.eraseCol( col );

	// Update the list of column types by moving all
	// items after the dropped column back one position.
	// Since we've already removed the last column
	// from the table, we have to add 1 to get the right
	// length of the vector.
	for( int i = col + 1; i < numCols() + 1; ++i ) {
		colType[i - 1] = colType[i];
	}
	colType.resize( numCols() );

	updateContents();
}
#if 0
void DataTable:: deleteColumns( QStringList dropnames )
{
	// Loop over the headers and then each column in the table.
	// Since we're likely to get the headers in order, optimize
	// this case by looking for the next column right after
	// the last one we found, instead of starting over at column
	// 0 each time we find a new header.  If no matching column
	// is found among those that remain, start again at column 0.
	QStringList::iterator nit;
	Q3Header * head = horizontalHeader();
	int c = 0;
	for( nit = dropnames.begin(); nit != dropnames.end(); ++nit ) {
		for( cols_not_checked = numCols(); cols_not_checked > 0;
				--cols_not_checked ) {
			// Found a match; remove it and get ready to 
			// look at the next column for the next name to drop.
			if( head->label( c ) == *nit ) {
				removeColumn( c );
				// No need to advance c, since this column will
				// be removed, but don't let it point past end
				if( c >= numCols() ) c = 0;
				break;
			}
			// No match, look at next column
			if( ++c == numCols() ) c = 0;
		}
	}
	// I THINK THIS IS DONE BUT I HAVEN'T CREATED CALLS TO IT OR TESTED
}
#endif

void DataTable:: clearAll()
{
	// Clear the data table.  Specifying all the rows
	// and columns in a QMemArray is much faster than
	// deleting them one by one.
	Q3MemArray<int> colList( numCols() );
	for( int c = 0; c < numCols(); ++c ) {
		colList[c] = c;
	}
	removeColumns( colList );

	Q3MemArray<int> rowList( numRows() );
	for( int r = 0; r < numRows(); ++r ) {
		rowList[r] = r;
	}
	removeRows( rowList );

	// Clear the data
	tableData.clear();

	// Clear the index map
	indexRow.clear();

	// Clear the column type information
	colType.clear();
	
	// Clear the hidden row list and the filter count
	// (but not the filters)
	activeFilterCount.clear();

	// Look at each active filter, clear its list of hidden rows
	Filter * f;
	for( f = filters.first(); f != 0; f = filters.next() ) {
		f->hiddenRows.clear();
	}
}


void DataTable:: addFilter( QString parameter, FilterOp op, QString value )
{
	// Find the column
	int col;
	Q3Header * header = horizontalHeader();
	QString paramAsUpper = parameter.upper();
	for( col = 0; col < numCols(); ++col ) {
		if( paramAsUpper == header->label(col).upper() ) break;
	}

	if( col == numCols() ) {
		qDebug( "Couldn't find column %s", qPrintable(parameter) );
		return;
	}

	// See if the comparison is numeric; if so, convert the value
	// We assume that anything that looks like a number should
	// be treated as a number and not as text.
	double numVal;
	bool numeric;
	numVal = value.toDouble( &numeric );

	// Add this filter to our active list
	Filter * f;
	filters.append( (f = new Filter( col, op, value, numVal, numeric ) ) );

	// Apply the filter to the table
	applyFilter( f );
}

void DataTable:: removeFilter( QString parameter, FilterOp op, QString value )
{
	// Find the matching filter; first, find the column
	int col;
	Q3Header * header = horizontalHeader();
	QString paramAsUpper = parameter.upper();
	for( col = 0; col < numCols(); ++col ) {
		if( paramAsUpper == header->label(col).upper() ) break;
	}

	if( col == numCols() ) {
		qDebug( "Couldn't find column %s", qPrintable(parameter) );
		return;
	}

	// Compare each filter in the list to our specification; stop
	// when we find a match
	Filter * f;
	for( f = filters.first(); f != 0; f = filters.next() ) {
		if( f->column == col && f->op == op && f->value == value ) {
			break;
		}
	}

	if( f == 0 ) {
		qDebug( "No filter found with col = %d op = %d value = %s",
				col, op, qPrintable(value) );
		return;
	}

	// Now look through this filter's list of hidden rows, decrement 
	// its filter count, and unhide rows that have no active filters.
	// The idea here is to avoid recomputing which rows are hidden
	// by reapplying all the active filters.  Instead, we have kept
	// track of the rows that a given filter hides, and when that
	// filter is removed, we traverse only those rows and unhide the
	// ones that have no more active filters on them.
	Q3ValueVector<unsigned>::iterator it;
	for( it = f->hiddenRows.begin(); it != f->hiddenRows.end(); ++it ) {
		QMap<unsigned,unsigned>::iterator mit
			= activeFilterCount.find( *it );
		int count = *mit;

		// No filters left on this row; unhide and remove map entry
		if( count <= 1 ) {
			showRow( *it );
			activeFilterCount.remove( mit );
		} else {
			// Decrement the filter count
			*mit = count - 1;
		}
	}

	// Done with this (current) filter; remove it from our list
	filters.remove();
}

void DataTable:: applyFilter( Filter * f )
{
	int col = f->column;
	FilterOp op = f->op;
	bool numeric = f->numeric;
	QString value = f->value;
	double numVal = f->numVal;

	// Go through the table and hide rows that don't match the filter.
	for( int row = 0; row < numRows(); ++row ) {
		QString t = text( row, col );
		if( ! matchFilter( t, numeric, op, numVal, value ) ) {
			hideRow( row );
			// Add to the filter count for this row, and
			// note the row in the filter's list
			activeFilterCount[row] += 1;
			f->hiddenRows.append( row );
		}
	}
}

bool DataTable:: matchFilter( QString text, bool numeric,
		FilterOp op, double numVal, QString pattern )
{
	if( numeric ) {
		switch( op ) {
			case FilterLT:
				return text.toDouble() < numVal;
			case FilterLE:
				return text.toDouble() <= numVal;
			case FilterEQ:
				return text.toDouble() == numVal;
			case FilterNE:
				return text.toDouble() != numVal;
			case FilterGE:
				return text.toDouble() >= numVal;
			case FilterGT:
				return text.toDouble() > numVal;
			default:
				return true;
		}
	} else {
		switch( op ) {
			case FilterLT:
				return text < pattern;
			case FilterLE:
				return text <= pattern;
			case FilterEQ:
				return text == pattern;
			case FilterNE:
				return text != pattern;
			case FilterGE:
				return text >= pattern;
			case FilterGT:
				return text > pattern;
			default:
				return true;
		}
	}

	// Should not be reached
	return true;
}

void DataTable:: sortColumn( int col, bool ascending, bool )
{
	// We need to unhide rows and reapply the filters, since
	// the values in the hidden rows will change as a result
	// of the sort, resulting in the wrong rows being hiddend.
	// done, the wrong rows will be hidden.  
	
#if 0
	// Unhide all the rows
	QMap<unsigned,unsigned>::iterator it;
	for( it = activeFilterCount.begin(); it != activeFilterCount.end();
			++it ) {
		showRow( it.key() );
	}
#endif
	
	// Clear the list of hidden rows
	activeFilterCount.clear();

	// Do the sort, taking account of the direction and the
	// column data type
	tableData.sortBy( col, (ascending ? TwoDTable<QString>::Ascending
				: TwoDTable<QString>::Descending ),
			colType[col] );

	// Look at each active filter, clear its list of hidden
	// rows, and apply it again
	Filter * f;
	for( f = filters.first(); f != 0; f = filters.next() ) {
		f->hiddenRows.clear();
		applyFilter( f );
	}

	// Update the result id to table row relation
	int c = index_col;
	int numRows = tableData.rows();
	int numColumns = tableData.columnsInRow(0);
	std::vector<QString> row_vec(numColumns);
	for (int i = 0; i < numRows; i++) {
		Q_ASSERT(i >= 0 && i < numRows);
		Q_ASSERT(numColumns == tableData.columnsInRow(i));
		row_vec = tableData[i];
		indexRow[row_vec[c]] = i;
	}
		
	updateContents();
}

// This function only sort of works.  On the Mac, it prints the
// full table just fine, except that the text is gray instead of
// black.  Printing just a range of pages or reversing the page
// order doesn't seem to work because the printer object doesn't
// report these options.  On Unix (at least AIX), when a table is
// too wide for a page (nearly always), the information on the
// width of a page is not reported correctly, so a significant
// amount of text on the right gets cut off.  On the other hand,
// printing in reverse order or a subset of pages does appear to
// work.  I haven't checked to see if the text is black or gray.
// In addition to fixing all this, it would be nice to list
// page numbers, let the user set the print font, and store this
// choice in a setting.
bool DataTable:: printTable( QPrinter * printer, const QFont& font )
{
	// First build an html-format string containing the
	// table data.  This is easy to do with the headerText
	// and dataText functions; just use the html-tags as
	// row and column separators.
	QString out;

	// Start the table and insert the header; don't include
	// the index column
	out += "<qt text=\"black\">\n"
		"<table width=\"100%\" border=1 cellspacing=0>\n"
		"<tr><th>" + headerText( "</th><th>", false ) + "</th></tr>";

	// Add the data (but not the index column)
	out += "<tr><td>" + dataText( "</td><td>", "</td></tr>\n<tr><td>",
			false, false );

	// We now have an extra <tr><td> at the end of the string;
	// drop them.
	out.truncate( out.length() - QString("<tr><td>").length() );

	// Finish off the table
	out += "</table></qt>\n";

	// Now paint the text on the printer
	
	// Get page dimensions
	QPainter painter( printer );
	int pageHeight = painter.window().height();
	int pageWidth = painter.window().width();

	// Create a QSimpleRichText object that represents the
	// table scaled and formatted for the printer.
	Q3SimpleRichText srt( out, font, QString(), 0, 0, pageHeight );
	srt.setWidth( &painter, pageWidth );

	// See how many pages wide the table is.  pageWidthUsed is the
	// total width for this printer in pixels.  The second term in
	// the formula below handles the rare case where the table width is
	// an even multiple of the page width.
	int pageWidthUsed = srt.widthUsed();
	int pagesAcross = ( pageWidthUsed / pageWidth )
		+ ( ( pageWidthUsed % pageWidth ) ? 1 : 0 );

	// Same calculation for pages down.
	int textHeight = srt.height();
	int pagesDown = ( textHeight / pageHeight )
		+ ( ( textHeight % pageHeight ) ? 1 : 0 );
	
	// Did the user ask for reverse order?
	bool forward = ( printer->pageOrder() == QPrinter::FirstPageFirst );
	//printf( "going %s\n", forward ? "forward" : "backward" );


	int minPage = 1, maxPage = pagesDown * pagesAcross;
	// Did the user limit the range of pages?
	if( printer->printRange() == QPrinter::PageRange ) {
		minPage = printer->fromPage();
		maxPage = printer->toPage();
	}
	//printf("page range is %d to %d\n", minPage, maxPage );
	//printf("Options: print to file %d print selection %d print rage %d\n",
	//		printer->isOptionEnabled( QPrinter::PrintToFile ),
	//		printer->isOptionEnabled( QPrinter::PrintSelection ),
	//		printer->isOptionEnabled( QPrinter::PrintPageRange ) );

	// Now loop over copies, vertical pages, and horizontal pages
	// to print out the table.
	bool firstPage = true;
	int hpage, vpage, seqPage;
	for( int copy = 0; copy < printer->numCopies(); ++copy ) {
		for( int v = 0; v < pagesDown; ++v ) {
			// Set page based on whether we're going forward
			// or backward
			vpage = forward ? v : pagesDown - v - 1;
			for( int h = 0; h < pagesAcross; ++h ) {
				hpage = forward ? h : pagesAcross - h - 1;
				// See which page in the overall sequence
				// (counting forward) this is.
				seqPage = vpage * pagesAcross + hpage + 1;

				// If page is not in range, skip it
				if(seqPage < minPage || seqPage > maxPage ) {
					continue;
				}
				//printf("doing page %d\n", seqPage );

				// Start a new page if this isn't page 1
				if( !firstPage ) {
					printer->newPage();
				} else {
					firstPage = false;
				}

				// Compute with section of the text to print
				QRect r( hpage * pageWidth, vpage * pageHeight,
						pageWidth, pageHeight );

				// Draw the text as specified by r at loction
				// 0,0 on the printer (since r is translated
				// into the middle of the text, we have to
				// shift the coordinate system back to get 
				// the top left corner of r to match the
				// origin of the page.)
				
				// smithm 2008-6-26
				// QPainter::saveWorldMatrix is obsolete
				//painter.saveWorldMatrix();
				painter.save();
				painter.translate( -r.x(), -r.y() );
				srt.draw( &painter, 0, 0, r, colorGroup() );
				// smithm 2008-6-26
				// QPainter::restoreWorldMatrix is obsolete
				//painter.restoreWorldMatrix();
				painter.restore();
			}
		}
	}

	// Always successful
	return true;
}
	
QString DataTable:: headerText( QString sep, bool incIndexCol ) const
{
	Q3Header * header = horizontalHeader();
	QString result;
	bool nosep = true;

	// Build a string of items separated by the separator string.
	// Some extra ugliness is needed to be sure that when we
	// omit the header for index_col, we also omit the separator,
	// even if the index_col is the first column.  nosep is set
	// to true if the next item added to the list should *not*
	// be preceded by the separator
	
	// Add first item, unless it's an unwanted index header
	if( index_col != 0 || incIndexCol ) {
		result = header->label( 0 );
		nosep = false;
	}

	for( unsigned c = 1; c < (unsigned)numCols(); ++c ) {
		if( c == index_col && !incIndexCol ) {
			nosep = true;
			continue;
		}
		result += (nosep ? QString() : sep ) + header->label( c );
		nosep = false;
	}

	return result;
}

QString DataTable:: dataText( QString colSep, QString rowSep,
		bool incHidden, bool incIndexCol )
{
	unsigned cols = numCols();
	unsigned rows = numRows();

	QString result;
	for( unsigned r = 0; r < rows; ++r ) {
		// Skip hidden rows, if requested
		if( ! incHidden && activeFilterCount[r] > 0 ) continue;

		for( unsigned c = 0; c < cols; ++c ) {
			if( c == index_col && !incIndexCol ) continue;
			result += text( r, c )
				+ ( c < cols - 1 ? colSep : rowSep );
		}
	}
	return result;
}

void DataTable::paintCell( QPainter * painter, int row, int col,
		const QRect& cr, bool selected, const QColorGroup& cg )
{
	// Define the cell rectange to be painted
	QRect rect( 0, 0, cr.width(), cr.height() );

	// Set the colors for text and background
	if( selected ) {
		painter->fillRect( rect, cg.highlight() );
		painter->setPen( cg.highlightedText() );
	} else {
		painter->fillRect( rect, cg.base() );
		painter->setPen( cg.text() );
	}

	// Paint the text in the cell
	// smithm 2008-6-26
	// Fixed scope for AlignAuto and AlignVCenter
	painter->drawText( 0, 0, cr.width(), cr.height(),
			Qt::AlignAuto | Qt::AlignVCenter, text( row, col ) );

	// Paint the grid lines around the cell, if enabled.  This
	// follows the same logic as QTable's paintCell(), since
	// we want to emulate its effect.
	if( showGrid() ) {
		// Save the current color
		QPen oldPen( painter->pen() );

		// Get the defined color for grid lines and make sure
		// it's valid; otherwise, use a medium shade
	
		// TODO: update setting of grid color to work with Qt 4
		//int gridColor = style().styleHint(
		//		QStyle::SH_Table_GridLineColor, this );
		int gridColor = -1;
		if( gridColor != -1 ) {
			const QPalette &pal = palette();
			if( cg != colorGroup() && cg != pal.disabled()
					&& cg != pal.inactive() ) {
				painter->setPen(cg.mid());
			} else { 
			       	painter->setPen((QRgb)gridColor);
			}
		} else {
			painter->setPen(cg.mid());
		}
		int xRight = cr.width() - 1;
		int yBottom = cr.height() - 1;
		painter->drawLine( xRight, 0, xRight, yBottom );  // Right
		painter->drawLine( 0, yBottom, xRight, yBottom ); // Bottom
		painter->setPen( oldPen );
	}
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


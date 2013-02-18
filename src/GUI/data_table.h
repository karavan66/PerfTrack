//! \file data_table.h

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

#ifndef DATA_TABLE_H
#define DATA_TABLE_H

#include <qfont.h>
#include <qmap.h>
#include <qprinter.h>
#include <q3ptrlist.h>
#include <q3sqlcursor.h>
#include <qstring.h>
#include <qstringlist.h>
#include <q3textstream.h>
#include <q3valuevector.h>

#include "filter_op.h"
#include "two_d_table.h"
#include "row_sort_table.h"

//! Alternative implementation of QSqlDataTable, which seems awfully slow.
//
//! This one populates itself from a QSqlCursor
//! and keeps rows together when sorting by any column.
class DataTable : public RowSortTable {
	Q_OBJECT
public:
	DataTable( QWidget * parent = 0, const char * name = 0 )
		: RowSortTable( parent, name )
	{	
		filters.setAutoDelete( true );
       	}

	//! Return the list of index keys, in lexicographic order.
	QStringList getKeyList() const
	{	return indexRow.keys();	} 

public slots:
	//! Fill table with data from cursor.  Also, sets column
	//! headings automatically.  Reads the data completely
	//! rather than retrieving it as needed, so the cursor need
	//! not support random access.
	void populateTable( Q3SqlCursor cursor );

	//! Fill table with data from file.  Also, sets the column
	//! headings automatically.  Assumes that the file has columns
	//! separated by \a colSep and rows separated by \a rowSep.
	//! The first row is taken to be the column names.
	void populateTable( Q3TextStream& ts, QString colSep, QString rowSep );

	//! Add columns to the right side of the table, one for each
	//! string in \a headers, and label them accordingly.
	void addColumns( QStringList headers );

	//! Add data to column \a columnName, with result ids
	//! specified in the first column of \a cursor matching
	//! the entries in the RESULT_ID column.
	void addColumnData( QString columnName, Q3SqlCursor cursor );
	
	//! Reimplementation removes data from underlying table as
	//! well as the table view.
	virtual void removeColumn( int col );

	//! Remove all data from the data; result is a table with
	//! no rows or columns.  Filters are NOT removed (so they
	//! will apply when new data is added).
	void clearAll();
	
	//! Hide rows in the table based on matching a filter.
	//! Filters are added cumulatively (so there is an
	//! implicit AND betwen them), and they are removed
	//! one at a time with removeFilter().
	void addFilter( QString parameter, FilterOp op, QString value );

	//! Remove a filter added with addFilter().
	void removeFilter( QString parameter, FilterOp op, QString value );

	//! Implement column sorting while handling hidden rows
	//! correctly (unhide all rows and reapply the filters
	//! after the sort).  We always sort by whole rows, so the
	//! third parameter (inherited from QDataTable) is ignored.
	virtual void sortColumn( int col, bool ascending, bool );

	//! Format data as a table and send it to the \a printer using
	//! \a font.  Returns true if printing was successful.
	bool printTable( QPrinter * printer, const QFont& font );

	//! Return the column headings, separated by the \a sep
	QString headerText( QString sep, bool incIndexCol = true ) const;

	//! Return the data from the table in a string.  Use \a colSep
	//! to separate the col data and \a rowSep to separate the
	//! row data.  If \a includeHidden is \a true, hidden rows
	//! will be included in the string.
	QString dataText( QString colSep, QString rowSep,
			bool includeHidden = true, bool incIndexCol = true );
	
	// The following functions are implementing what I hope will
	// be a faster table that we can display quickly from an
	// internal 2-D array.  Adpated from
	// http://doc.trolltech.com/qq/qq07-big-tables.html .
	
	//! Get the text for a cell from the underlying data structure.
	//! This gets called often by paintCell(), so we really need it
	//! to be inlined.
	inline QString text( int row, int col ) const
	{
		return tableData[row][col];
	}

	//! Reimplement painting the cell since we're not doing anything
	//! fancy like letting the user edit values.  This is simpler
	//! and faster than the native version.
	void paintCell( QPainter * painter, int row, int col,
			const QRect& cr, bool selected, const QColorGroup& cg );

	// The rest of these do nothing; they are here to hide the
	// base class implementations.
	QWidget * createEditor( int, int, bool ) const { return 0; }
	void setCellContentFromEditor( int , int ) {}
	QWidget * cellWidget( int, int ) const { return 0; }
	void endEdit( int, int, bool, bool ) {}
	void resizeData( int ) {}
	Q3TableItem * item( int, int ) { return 0; }
	void setItem( int, int, Q3TableItem * ) {}
	void clearCell( int, int ) {}
	void insertWidget( int, int, QWidget * ) {}
	void clearCellWidget( int, int ) {}
	
protected:

	//! Tests whether \a text matches the condition specified by
	//! \a op and either \a numVal or \a pattern.  If \a numeric
	//! is true, \a text is converted to a number and the
	//! comparison is done numerically; otherwise the test is
	//! lexicograhic.
	bool matchFilter( QString text, bool numeric, FilterOp op,
			double numVal, QString pattern );

	//! Data structure to encode an active filter
	struct Filter {
		Filter( int c, FilterOp o, QString v, double nv, bool n )
			: column( c ), op( o ), value( v ), numVal( nv ),
			numeric( n )
		{}
		int column;
		FilterOp op;
		QString value;
		double numVal;
		bool numeric;
		// This is a list of all rows hidden by this filter
		Q3ValueVector<unsigned> hiddenRows;
	};

	//! Apply a filter to each row in the table
	void applyFilter( Filter * f );

	//! List of active filters
	Q3PtrList<Filter> filters;

	//! List of row numbers and the number of active filters on each one
	QMap<unsigned,unsigned> activeFilterCount;

	//! Index of the column that contains the key values
	unsigned index_col;

	//! Map of key values (stored in the index column) to the row
	//! numbers where they reside.  This helps us add new keyed data
	//! to new columns quickly.
	QMap<QString,int> indexRow;

	//! Hold the data in a 2-D array, rather than storing it
	//! directly in QTableItems.  This might be faster.
	TwoDTable<QString> tableData;

	//! Keep track of whether we think a column is text or numbers
	Q3ValueVector<TwoDTable<QString>::CompareType> colType;
	
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


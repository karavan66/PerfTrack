//! \file two_d_table.h

// John May, 30 June 2005
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

//! Two dimensional table of T with sorting

#ifndef TWO_D_TABLE_H
#define TWO_D_TABLE_H

#include <algorithm>
#include <vector>

using namespace std;

//! Two dimensional table of T with sorting (by column number).
template<typename T>
class TwoDTable {
public:
	//! Initialize an empty table (or fill with default values)
	TwoDTable<T>( unsigned rows = 0, unsigned cols = 0,
			const T& val = T() )
		: data( rows, vector<T>( cols, val ) )
	{ }

	//! Copy a table
	TwoDTable<T>( const TwoDTable<T>& ref )
		: data( ref.data )
	{ }

	//! Assign one table to another
	TwoDTable<T>& operator=( const TwoDTable<T>& ref )
	{
		data = ref.data;
		return data;
	}

	//! Add a row to the end of the table
	void push_back( const vector<T>& row )
	{
		data.push_back( row );
	}

	//! Get number of rows.
	unsigned rows() const
	{
		return data.size(); 
	}

	//! Get number of columns for the specified row.  There
	//! is no guarantee that all rows are the same size.
	unsigned columnsInRow( unsigned row ) const
	{
		return data[row].size();
	}

	//! Set the row and column dimensions.  All columns are
	//! modified, so this can be expensive!
	void resize( unsigned rows, unsigned cols )
	{
		data.resize( rows );
		typename vector<vector<T> >::iterator it;
		for( it = data.begin(); it != data.end(); ++it ) {
			(*it).resize( cols );
		}
	}

	//! Retrieve a row
	vector<T>& operator[]( unsigned index )
	{
		return data[index];
	}

	//! Replace a row
	const vector<T>& operator[]( unsigned index ) const
	{
		return data[index];
	}

	//! Enum to specify sorting direction
	enum Direction {
		//! Sort low-to-high
		Ascending,
		//! Sort high-to-low
		Descending
	};

	//! Enum to specify comparison type -- string or numeric
	enum CompareType {
		//! Sort as text
		String,
		//! Sort as numbers
		Numeric
	};

	//! Sort the rows according to the contents of column \a col.
	//! \a d specifies whether to sort ascending or descending,
	//! and \a c specifies whether to sort as strings or numbers.
	//! Calls the std::stable_sort() algorithm,
	//! so equivalent rows aren't moved.
	
	// smithm 2008-6-26
	// Undo a change made by qt3to4.  qt3to4 misidentified this as belonging
	// to the Qt library.
	//void sortBy( unsigned col, Qt::Orientation d = Qt::AscendingOrder,
	void sortBy( unsigned col, Direction d = Ascending,
		CompareType c = String )
	{
		if( c == String ) {
			if( d == Ascending ) {
				stable_sort( data.begin(), data.end(),
					CompareByColAsc( col ) );
			} else {
				stable_sort( data.begin(), data.end(),
					CompareByColDesc( col ) );
			}
		} else {
			if( d == Ascending ) {
				stable_sort( data.begin(), data.end(),
					CompareDoublesByColAsc( col ) );
			} else {
				stable_sort( data.begin(), data.end(),
					CompareDoublesByColDesc( col ) );
			}
		}
	}

	//! Remove a row.  This is O(N)!
	void eraseRow( unsigned row )
	{
		typename vector<vector<T> >::iterator it;
		unsigned r = 0;
		for( it = data.begin(); it != data.end(); ++r, ++it ) {

			// Find the matching row (have to use an
			// iterator for erase, and this is the only
			// way I can find to get on in the middle of vector!)
			if( r == row ) {
				data.erase( it );
				break;
			}
		}
	}

	//! Remove a column.  This is O(NxM)!
	void eraseCol( unsigned col )
	{
		// Visit each row, find column c there, and erase it
		typename vector<vector<T> >::iterator rit;
		typename vector<T>::iterator cit;
		for( rit = data.begin(); rit != data.end(); ++rit ) {
			unsigned c = 0;
			for( cit = (*rit).begin(); cit != (*rit).end();
					++c, ++cit ) {
				if( c == col ) {
					(*rit).erase( cit );
					break;
				}
			}
		}
	}


	//! Remove all entries from the table
	void clear()
	{
		data.clear();
	}

private:

	//! Functor classes that defines comparison of two vectors based on
	//! a specific element.
	//! We need two versions, one for ascending comparisons, and one for
	//! descencding comparisons.  We could have had one class that 
	//! stores a flag, but that flag would have to be queried for
	//! each comparison, incurring extra overhead.
	class CompareByColAsc
		: public binary_function< vector<T>, vector<T>, bool> {
	public:
		//! Construct functor and store the column to use in sort
		CompareByColAsc( unsigned col ) : sortCol( col ) { }

		//! Function operator that does comparison
		bool operator()( const vector<T>& a, const vector<T>& b ) const
		{
			return ( a[sortCol] < b[sortCol] );
		}
	private:
		unsigned sortCol;
	};

	class CompareByColDesc
		: public binary_function< vector<T>, vector<T>, bool> {
	public:
		//! Construct functor and store the column to use in sort
		CompareByColDesc( unsigned col ) : sortCol( col ) { }

		//! Function operator that does comparison
		bool operator()( const vector<T>& a, const vector<T>& b ) const
		{
			return !( a[sortCol] < b[sortCol] );
		}
	private:
		unsigned sortCol;
	};

	//! Type-specialized functor classes that define comparison based on
	//! a specific column.  These versions convert the string to a number
	//! before doing the comparison (with no checking for whether the
	//! string decodes to a valid number; if it doesn't, then
	//! QString::toDouble just returns 0.)
	class CompareDoublesByColAsc
		: public binary_function< vector<QString>,
					vector<QString>, bool> {
	public:
		//! Construct functor and store the column to use in sort
		CompareDoublesByColAsc( unsigned col ) : sortCol( col ) { }

		//! Function operator that does comparison
		bool operator()( const vector<QString>& a,
				const vector<QString>& b ) const
		{
			return ( a[sortCol].toDouble()
					< b[sortCol].toDouble() );
		}
	private:
		unsigned sortCol;
	};

	class CompareDoublesByColDesc
		: public binary_function< vector<QString>,
					vector<QString>, bool> {
	public:
		//! Construct functor and store the column to use in sort
		CompareDoublesByColDesc( unsigned col ) : sortCol( col ) { }

		//! Function operator that does comparison
		bool operator()( const vector<QString>& a,
				const vector<QString>& b ) const
		{
			return !( a[sortCol].toDouble()
					< b[sortCol].toDouble() );
		}
	private:
		unsigned sortCol;
	};

	//! The storage for our data
	vector<vector<T> > data;
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


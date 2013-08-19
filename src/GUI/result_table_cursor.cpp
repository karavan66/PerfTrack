// result_table_cursor.cpp
// John May, 17 November 2004
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include <qsqlquery.h>
//Added by qt3to4:
#include <Q3SqlCursor>
#include <result_table_cursor.h>

ResultTableCursor:: ResultTableCursor( QString table, QSqlDatabase db )
	: Q3SqlCursor( table, TRUE, db )
{
}

QVariant ResultTableCursor:: calculateField( const QString & type )
{
	// Put name in a standard form
	QString typeLC = type.lower();

	QString queryText;

	// Look up names for resource type by finding the relevent
	// resource id in focus_has_resource.
	queryText = "SELECT name FROM resource_item "
		"WHERE id IN "
		"(SELECT resource_id FROM focus_has_resource "
			"WHERE focus_id = "
			+ field( "focus_id" ).value().toString()
			+ ") "
		"AND type = '" + type + "'";

	QSqlQuery query( queryText );

	// From here on, we assume there's only one match; that would
	// be easy to change if needed.  Return the matching item,
	// if any; conversion to a string will happen in the caller.
	if( query.next() )
		return query.value( 0 );

	// No match found; return empty string
	return QVariant( QString() );
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


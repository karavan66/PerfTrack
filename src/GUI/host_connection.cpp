// host_connection.cpp
// John May, 7 January 2005 
//
/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#include "host_connection.h"

HostConnection:: HostConnection( QString hostname, QString username,
		int portno )
	: host( hostname), user( username), port( portno)
{
	// We use ssh and its port forwarding facility to
	// establish the connection.  Set up the arguments
	// that we'll need.  We depend on the compile line to
	// define SSH_COMMAND for us.
	QStringList args;

	args += "/usr/bin/ssh";
	args += "-l";
	args += user;
	args += host;
	args += "-L" + QString::number( port ) +	// port forwarding
		":localhost:" + QString::number( port );
	args += "echo LOGINCOMPLETE;csh -f";
			// Echo some unique text so we know when we're
			// logged in, then start a shell so the connection
			// will stay alive.  The shell isn't strictly
			// needed; we just need something that will run
			// indefinitely.

	proc.setArguments( args );
}

HostConnection:: ~HostConnection()
{
	disconnect();
}

bool HostConnection:: connect()
{
	// Kill any previous process we started (maybe this isn't
	// the right choice?)
	disconnect();

	// Try to start the process
	bool success = proc.start();
	if( ! success ) return false;

	QByteArray ba_stdout;
	QByteArray ba_stderr;
	do {
		// Print stderr messages that include a password prompt
		ba_stderr = proc.readStderr();
		if( QString( ba_stderr ).contains( "word:" ) ) 
			fprintf( stderr, "%s", ba_stderr.data() );
		// Don't report stdout info; just read it until we
		// see the message that the login is complete
		ba_stdout = proc.readStdout();
	} while( ! ( QString( ba_stdout ).contains( "LOGINCOMPLETE" ) ) );

	return true;
}

bool HostConnection:: isConnected() const
{
	return proc.isRunning();
}

void HostConnection:: disconnect()
{
	if( proc.isRunning() ) {
		proc.kill();
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


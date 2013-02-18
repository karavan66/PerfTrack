# gui.pro
#
# PerfTrack Version 1.0 (September 2005)
# 
# For information on PerfTrack, please contact John May
# (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
# 
# See COPYRIGHT AND LICENSE information at the end of this file.
#

# qmake input file for PerfTrack GUI.  Process with qmake to
# generate a platform-specific Makefile.

###
# Begin local configuration options. 
###

# Set the location of Python headers.
#INCLUDEPATH += /stash/pperfdb/packages/Python-2.4.3/include/python2.4
#INCLUDEPATH += /stash/pperfdb/packages/Python-2.5.1-install/include/python2.5
#INCLUDEPATH += $(PYINC)
#INCLUDEPATH += /usr/include/python2.4
INCLUDEPATH += /usr/include/python2.6

# Set the location of Python libraries.
#LIBS += -L/pperfdb/packages/Python-2.5.1-install/lib -lpython2.5
LIBS += -L$(PYLIB) -lutil -lpython2.6
#LIBS += -L/usr/local/lib/python2.5 -lutil -lpython2.5

# Uncomment the line below to select results by focus name
#DEFINES += SELECT_WITH_FOCUS_NAME EMIT_CURSOR USE_FULL_RESOURCE_NAMES=true

# Uncomment the line below to select results using resource ids
DEFINES += USE_FULL_RESOURCE_NAMES=false

# Define the resouce delimeter.
DEFINES += PTRESDELIM=\\\"\"|\"\\\"

###
# End local configuration options.  You shouldn't need to edit
# anything below.
###

TARGET		= perftrack
TEMPLATE	= app
LANGUAGE	= C++

QT +=  sql 
QT += qt3support
CONFIG += uic3
CONFIG	+= qt warn_on debug

HEADERS	+= selection_dialog.h \
	selection_list_item.h \
	resource_selector.h \
	data_access.h \
	result_table_cursor.h \
	dataset.h \
	tg_barchart.h \
	chart_viewer.h \
	row_sort_table.h \
	resource_type_and_name.h \
	host_connection.h \
	pt_main_window.h \
	data_table.h \
	data_filter_dialog.h \
	filter_op.h \
	filter_list_box_item.h \
	file_options_dialog.h \
	plot_data_dialog.h \
	column_data_dialog.h \
	static_check_list_item.h \
	constraint_list_item.h \
	two_d_table.h \
	select_operator_dialog.h \
	comb_perfRes_widget.h \
	combine_perfReses_dialog.h \
	operator.h \
	perfResult.h

SOURCES	+= main.cpp \
	selection_dialog.cpp \
	selection_list_item.cpp \
	resource_selector.cpp \
	data_access.cpp \
	result_table_cursor.cpp \
	chart_viewer.cpp \
	dataset.cpp \
	tg_barchart.cpp \
	resource_type_and_name.cpp \
	host_connection.cpp \
	pt_main_window.cpp \
	data_table.cpp \
	data_filter_dialog.cpp \
	filter_op.cpp \
	file_options_dialog.cpp \
	plot_data_dialog.cpp \
	column_data_dialog.cpp \
	select_operator_dialog.cpp \
	comb_perfRes_widget.cpp \
	combine_perfReses_dialog.cpp \
	operator.cpp \
	perfResult.cpp


#The following line was changed from FORMS to FORMS3 by qt3to4
FORMS3	= selection_dialog_base.ui \
	resource_selector_base.ui \
	db_connection_dialog.ui \
	remotehostextension.ui \
	chart_viewer_base.ui \
	pt_main_window_base.ui \
	data_filter_dialog_base.ui \
	file_options_dialog_base.ui \
	plot_data_dialog_base.ui \
	column_data_dialog_base.ui \
	attributedialog.ui \
	execution_resource_extension.ui \
	select_operator_dialog_base.ui \
	comb_perfRes_widget_base.ui \
	combine_perfReses_dialog_base.ui

unix {
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}

# Define the platform-specific ssh location, and other
# platform-specific information.

OSNAME = $$system( uname -s )

contains( OSNAME, [Ss]olaris ) {
	message( "Building Makefile for SunOS" )
	DEFINES += SSH_COMMAND=\"/usr/local/bin/ssh\"
}
contains( OSNAME, [Dd]arwin ) {
	message( "Building Makefile for Macintosh OS X" )
# Need extra level of backslash quoting when generating Xcode file
# Be sure to change both versions when editing!
	contains( MAKEFILE_GENERATOR, PROJECTBUILDER ) {
		DEFINES += SSH_COMMAND=\\"/usr/bin/ssh\\"
	} else {
		DEFINES += SSH_COMMAND=\"/usr/bin/ssh\"
	}
}
contains( OSNAME, [Aa][Ii][Xx] ) {
	message( "Building Makefile for AIX" )
	QMAKE_CXXFLAGS += -qstaticinline -qcheck
        QMAKE_LFLAGS += -qcheck
	DEFINES += SSH_COMMAND=\"/usr/local/bin/ssh\"
}
contains( OSNAME, [Ll]inux ) {
	message( "Building Makefile for Linux" )
	DEFINES += SSH_COMMAND=\"/usr/bin/ssh\"
}
contains( OSNAME, [Oo][Ss][Ff]1 ) {
	message( "Building Makefile for Tru64" )
	DEFINES += SSH_COMMAND=\"/usr/local/bin/ssh\"
	# The following flag is supposed to be added automatically
	# when the QMAKE_CC_THREAD compiler invoked (i.e., cxx -pthread)
	# but apparently it doesn't happen.
	QMAKE_CFLAGS += -D_REENTRANT
}

# ---------------------------------------------------------------------------
# COPYRIGHT AND LICENSE
# 
# Copyright (c) 2005, Regents of the University of California and
# Portland State University.  Produced at the Lawrence Livermore
# National Laboratory and Portland State University.
# UCRL-CODE-2005-155998
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the
# distribution.
# * Neither the name of the University of California
# or Portland State Univeristy nor the names of its contributors
# may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ACKNOWLEDGMENT
#
# 1. This notice is required to be provided under our contract with the U.S.
# Department of Energy (DOE).  This work was produced at the University
# of California, Lawrence Livermore National Laboratory under Contract
# No. W-7405-ENG-48 with the DOE.
#
# 2. Neither the United States Government nor the University of California
# nor any of their employees, makes any warranty, express or implied, or
# assumes any liability or responsibility for the accuracy, completeness, or
# usefulness of any information, apparatus, product, or process disclosed, or
# #represents that its use would not infringe privately-owned rights.
#
# 3.  Also, reference herein to any specific commercial products, process, or
# services by trade name, trademark, manufacturer or otherwise does not
# necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or the University of California.
# The views and opinions of authors expressed herein do not necessarily
# state or reflect those of the United States Government or the University of
# California, and shall not be used for advertising or product endorsement
# purposes. 
# ----------------------------------------------------------------------------



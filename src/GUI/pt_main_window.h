//! \file pt_main_window.h

// John May, 19 January 2005

/*****************************************************************
* PerfTrack Version 1.0 (September 2005)
* 
* For information on PerfTrack, please contact John May
* (johnmay@llnl.gov) or Karen Karavanic (karavan@cs.pdx.edu).
* 
* See COPYRIGHT AND LICENSE information at the end of this file.
*
*****************************************************************/

#ifndef PT_MAIN_WINDOW_H
#define PT_MAIN_WINDOW_H

#include <q3dict.h>
#include <qfont.h>
#include <qpair.h>
#include <q3popupmenu.h>
#include <qprinter.h>
#include <q3sqlcursor.h>
#include <qstring.h>
#include <q3textstream.h>
#include <qtoolbutton.h>
#include <q3valuelist.h>

#include "chart_viewer.h"
#include "data_access.h"
#include "data_filter_dialog.h"
#include "file_options_dialog.h"
#include "plot_data_dialog.h"
#include "pt_main_window_base.h"
#include "selection_dialog.h"
#include "column_data_dialog.h"
#include "tg_barchart.h"
#include "select_operator_dialog.h"
#include "combine_perfReses_dialog.h"

//! PerfTrack's main GUI window.

//! Inherits PTMainWindowBase, created with Qt Designer, and implements
//! the main view for the PerfTrack GUI.
class PTMainWindow : public PTMainWindowBase {
	Q_OBJECT
public:
	PTMainWindow( DataAccess * da, QWidget * parent = 0,
			const char * name = 0,
			Qt::WFlags f = Qt::WType_TopLevel );
	~PTMainWindow();

public slots:
	//! Pop up the dialog to start a new query, and clear any
	//! old data out of the results table (but don't change
	//! and plots)
	void doNewQuery();

	//! Show or hid the dialog to get the display parameters, showing
	//! only those resources that the query determined were
	//! unique for this result set.
	void toggleDisplayParametersDialog( bool );

	//! Show or hide the dialog to filter the results shown in the table.
	void toggleFilterDialog( bool );

	//! Show or hide the dialog to plot the data.
	void togglePlotDialog( bool );

	//! Reset the data in the selection parameter list
	void resetParamList( Q3ValueList<QPair<QString,QString> > params );

	//! Enable or disable data handling tools, based on whether the
	//! cursor sent contains any data.  Also get information on 
	//! columns and pass it to the interested widgets.
	void handleNewResults( Q3SqlCursor );
	
	//! Enable or disable data handling tools, based on whether the
	//! text stream sent contains any data.  Also get information on 
	//! columns and pass it to the interested widgets.
	void handleNewResults( Q3TextStream& );

	//! Save table data in file
	void save();

	//! Save table data in file, after getting info from user
	void saveAs();

	//! Pop up a dialog to set the text file options
	void setFileOptions();

	//! Get data from file (which is requested from user)
	void openFile();

	//! Read from the current file name and populate the table
	void readFile();

	//! Print data from table or a plot; \a menuId identifies
	//! the item in the popup that says what to print
	void printData( int menuId );

	void combinePerfResults(bool haveData=true);

	//! Terminate the application cleanly
	void exit();

	// Eventually also need help and maybe some others.
protected slots:
	//! Note when dialog closes so we can set the GUI state.
	void dataFilterDialogClosing();
	//! Note when dialog closes so we can set the GUI state.
	void plotDataDialogClosing();
	//! Note when dialog closes so we can set the GUI state.
	void columnDataDialogClosing();
	//! Note the status of the database connection.  If called
	//! with \a success == true, pops up a query dialog.
	void dbConnectionDone( bool success );

	perfResultList * getPerfResultsForCombining();

	//! Create a new data plot and plot the data
	void createDataPlot( QString xAxis, QString dataLabel,
			QString plotName);
	//! Add new data to an existing plot
	void addDataToPlot( QString xAxis, QString dataLabel,
			QString plotName);
	//! Notice when a plot closes so we can update GUI elements
	void chartViewerClosing( ChartViewer * );

	//! Popup up the print submenu next to the print tool button
	void showPrintToolButtonPopup();

	//! Add named columns to the right side of the table
	void addColumns( QStringList names );

	//! Remove named columns from the table.  Designed to work
	//! fastest when the order of the names matches the
	//! order of the columns in the table, but works correctly
	//! in any case.
	void removeColumns( QStringList dropnames );

	//! Request data for each of the named resources and attributes
	void getColumnData( QStringList resourceNames,
			QStringList attributeNames );

	void saveResults();
	void clearResults();
signals:
	void savePerfRes(perfResult*, Q3ValueList<int>,bool);
	void clearPerfRes(perfResult*, int);
	void dataSheetReloading(int);
protected:
	//! What to do when blank data is encountered in the table
	enum BlankHandling { NotChecked, Allow, Skip, Cancel };
	BlankHandling askAboutBlanks( QString col, int row );

	bool plotData( TGBarChart *, QString xAxis, QString plotData );

	//! Handle specialized setup for print menu item and tool button
	void initPrintAction();

	QStringList columnList;
	SelectionDialog * selectionDialog;
	DataFilterDialog * dataFilterDialog;
	FileOptionsDialog * fileOptionsDialog;
	PlotDataDialog * plotDataDialog;
	ColumnDataDialog * columnDataDialog;
	SelectOperatorDialog * selectOperatorDialog;
	CombinePerfResesDialog * combinePerfResesDialog;
	DataAccess * dataSource;
	QPrinter * printer;
	Q3PopupMenu * printItemsPopup;
	QToolButton * printToolButton;
	QFont printFont;
	int printDataAsTextId;	// menu id corresponding to print-as-text
	int printMenuItemId; 	// menu id corresponding to print command
	QString fileName;
	QString rowSep;		// Default row separator for text
	QString colSep;		// Defailt column separator for text
	QString fileExtension;	// Default extension for text files
	bool includeHidden;	// whether to include hidden rows in output
	QStringList perfResultIds;	// performance result ids in display
	Q3Dict<ChartViewer> charts;	// keep track of all charts
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

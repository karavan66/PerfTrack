// pt_main_window.cpp
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

#include <math.h>
#include <qaction.h>
#include <qapplication.h>
#include <qfile.h>
#include <q3filedialog.h>
#include <q3listbox.h>
#include <qmessagebox.h>
#include <qstatusbar.h>
#include <qcombobox.h>
//Added by qt3to4:
#include <Q3TextStream>
#include <Q3ValueList>
#include <Q3SqlCursor>
#include <Q3PopupMenu>

#include "data_table.h"
#include "perfResult.h"
#include "pt_main_window.h"

#include "pt_main_window.moc"

PTMainWindow::PTMainWindow( DataAccess * da, QWidget * parent,
		const char * name, Qt::WFlags f )
	: PTMainWindowBase( parent, name, f ),
	rowSep( "\n" ), colSep( "," ),
	fileExtension( ".csv" ), includeHidden( false )
{
	dataSource = da;

	// Set the characteristics of the display table
	dataTable->setSorting( true );
	dataTable->setSelectionMode( Q3Table::Multi );
	dataTable->setReadOnly( true );

	// Create the dialogs
//	selectionDialog = new SelectionDialog( dataSource, this );
	// Making this window parentless and a group leader allows
	// it to create its own dialogs that work even though this
	// dialog can be modal.
	selectionDialog = new SelectionDialog( dataSource, 0, 0,
			false, Qt::WGroupLeader );
	dataFilterDialog = new DataFilterDialog( this );
	fileOptionsDialog = new FileOptionsDialog( this ); 
	plotDataDialog = new PlotDataDialog( this );
	columnDataDialog = new ColumnDataDialog( this );
	selectOperatorDialog = new SelectOperatorDialog(this);
	combinePerfResesDialog = new CombinePerfResesDialog(this, NULL,da);

	// Create a printer and set up the custom controls for it
	// (we need a popup menu to list the choices, and this doesn't
	// fit Qt's Action model)
	printer = new QPrinter( QPrinter::HighResolution );
	initPrintAction();

	 
	//selectOperatorDialog->initialize();
	combinePerfResesDialog->initializeOperators();

	// Define a default font.  This should probably be a setting. FIX
	// The user should also have a way to change it. FIX
	printFont = QFont( "Helvetica", 10 );

	// Connect action signals to slots
	connect( connectDbAction, SIGNAL( activated() ),
			dataSource, SLOT( setupDBConnection() ) );
	connect( newQueryAction, SIGNAL( activated() ),
			this, SLOT( doNewQuery() ) );
	connect( filterResultsAction, SIGNAL( toggled(bool) ),
			this, SLOT( toggleFilterDialog(bool) ) );
	connect( addDisplayParametersAction, SIGNAL( toggled(bool) ),
			this, SLOT( toggleDisplayParametersDialog(bool) ) );
	connect( combineAction, SIGNAL( activated() ),
			this, SLOT( combinePerfResults() ) );
	connect( plotDataAction, SIGNAL( toggled(bool) ),
			this, SLOT( togglePlotDialog(bool) ) );
	connect( fileQuitAction, SIGNAL( activated() ),
			this, SLOT( exit() ) ) ;
	connect( fileOpenAction, SIGNAL( activated() ),
			this, SLOT( openFile() ) );
	// Connect Save to Save As because there's no way for a user
	// to change data (other than hiding it), so saving to a
	// file usually means saving something new.  It seem safer
	// to ask for a file name every time.
	connect( fileSaveAction, SIGNAL( activated() ),
			this, SLOT( saveAs() ) );
	connect( fileSaveAsAction, SIGNAL( activated() ),
			this, SLOT( saveAs() ) );
	connect( fileOptionsAction, SIGNAL( activated() ),
			this, SLOT( setFileOptions() ) );

	// Connect results from the data source to the table
	connect( dataSource, SIGNAL( resultsReady( Q3SqlCursor ) ),
			dataTable, SLOT( populateTable( Q3SqlCursor ) ) );
	connect( dataSource, SIGNAL( resultsReady( Q3SqlCursor ) ),
			this, SLOT( handleNewResults( Q3SqlCursor ) ) );

	// Connect signals from the dialogs
	connect( dataFilterDialog, SIGNAL( closing() ),
			this, SLOT( dataFilterDialogClosing() ) );
	connect( dataFilterDialog,
			SIGNAL( applyFilter( QString, FilterOp, QString ) ),
			dataTable,
			SLOT( addFilter( QString, FilterOp, QString ) ) );

	connect( dataFilterDialog,
			SIGNAL( dropFilter( QString, FilterOp, QString ) ),
			dataTable,
			SLOT( removeFilter( QString, FilterOp, QString ) ) );
	connect( dataSource, SIGNAL( databaseConnected( bool ) ),
			this, SLOT( dbConnectionDone( bool ) ) );

	connect( plotDataDialog, SIGNAL( newPlotRequested( QString,
					QString, QString ) ),
			this, SLOT( createDataPlot( QString,
					QString, QString ) ) );

	connect( plotDataDialog, SIGNAL( addToPlotRequested( QString,
					QString, QString ) ),
			this, SLOT( addDataToPlot( QString,
					QString, QString ) ) );
	connect( plotDataDialog, SIGNAL( closing() ),
			this, SLOT( plotDataDialogClosing() ) );

	connect( columnDataDialog, SIGNAL( attributesRequested( QString,
					QString, void * ) ),
			dataSource, SLOT( findAttributesByType( QString,
					QString, void * ) ) );
	connect( dataSource, SIGNAL( foundAttributesByType( QString,
					QStringList, void * ) ),
			columnDataDialog, SLOT( setAvailableAttributes( QString,
				QStringList, void * ) ) );
	connect( columnDataDialog, SIGNAL( columnsRequested( QStringList) ),
			this, SLOT( addColumns( QStringList ) ) );
	connect( columnDataDialog,
			SIGNAL( removeColumnsRequested( QStringList) ),
			this, SLOT( removeColumns( QStringList ) ) );
	connect( columnDataDialog,
			SIGNAL( dataRequested( QStringList, QStringList ) ),
			this,
			SLOT( getColumnData( QStringList, QStringList ) ) );
	connect( columnDataDialog, SIGNAL( closing() ),
			this, SLOT( columnDataDialogClosing() ) );
	connect( dataSource,
			SIGNAL( resultDetailsReady( QString, Q3SqlCursor ) ),
			dataTable,
			SLOT( addColumnData( QString, Q3SqlCursor ) ) );

        connect (selectionDialog, SIGNAL(combineResults(bool)), this, SLOT(combinePerfResults(bool)));


	connect(this, SIGNAL(savePerfRes(perfResult*, Q3ValueList<int>,bool)), combinePerfResesDialog,SLOT(saveResult(perfResult*, Q3ValueList<int>,bool)));

	connect(this, SIGNAL(clearPerfRes(perfResult*, int)), combinePerfResesDialog, SLOT(clearResultFromSheet(perfResult*, int)));
 
	connect(this, SIGNAL(dataSheetReloading(int)), combinePerfResesDialog, SLOT(dataSheetReloading(int)));

	// Note whether we have an active database connection
	dbConnectionDone( dataSource->isConnected() );
}

PTMainWindow:: ~PTMainWindow()
{
	// Dialogs are owned by this window, so they should
	// be deleted automatically.  The exception is the
	// Selection Dialog, which does not have a parent.
	delete selectionDialog;
}

void PTMainWindow::initPrintAction()
{
	// Create a popup menu of things we can print
	printItemsPopup = new Q3PopupMenu( this );
	printDataAsTextId = printItemsPopup->insertItem( "Data as text" );

	// Add the print item (with its popup menu) to
	// the File menu.  We need to find the current menu entry
	// and replace it with one that has the popup menu.
	for( unsigned index = 0; index < fileMenu->count(); ++index ) {
		int id = fileMenu->idAt( index );
		if( fileMenu->text( id ) == filePrintAction->menuText() ) {
			fileMenu->removeItemAt( index );
			printMenuItemId = fileMenu->insertItem(
					filePrintAction->menuText(),
					printItemsPopup, id, index );
			fileMenu->setItemEnabled( printMenuItemId, false );
			break;
		}
	}

	// Add a tool button to the toolbar and have it activate the
	// popup menu as well
	printToolButton = new QToolButton( toolBar );
	printToolButton->setIconSet( filePrintAction->iconSet() );
	printToolButton->setTextLabel( filePrintAction->text() );
	printToolButton->setPopup( printItemsPopup );
	printToolButton->setPopupDelay( 0 );
	printToolButton->setEnabled( false );

	// Make the button itself (as well as the little arrow) pop up
	// the menu
	connect( printToolButton, SIGNAL( clicked() ),
			this, SLOT( showPrintToolButtonPopup() ) );

	// Connect the file item menu to the print slot
	connect( printItemsPopup, SIGNAL( activated(int) ),
			this, SLOT( printData(int) ) );
}

void PTMainWindow::showPrintToolButtonPopup()
{
	// this seems like it should be a slot without our help
	printToolButton->openPopup();
}

void PTMainWindow::doNewQuery()
{
	// Pop up the dialog (which retains its state from last
	// viewing) and do the query using the chosen parameters
	// if the user accepts the choices.
	if( selectionDialog->exec() == QDialog::Accepted ) {

	       //TODO for now there is only one data sheet, so getting new data
	       //wipes out whatever was in the old data sheet. we need to update any combined
	       //performance results that think they are still on the sheet that is being 
	       //rewritten
	        emit(dataSheetReloading(0)); 
		Q3ValueList<ResourceTypeAndName> constraintList =
			selectionDialog->buildConstraintList();

		// List the constraints in the parameter table
		resetParamList( constraintList );

		// This will take a while, so put a message in
		// the status bar
		statusBar()->message( "Retrieving data..." );

		// Be sure these changes get painted before we do
		// the query (if we ever go multithreaded, this
		// should be unneccesary)
		qApp->processEvents();

		dataSource->getResults( selectionDialog->typeCount(),
				selectionDialog->metricIdList(),
				//selectionDialog->selectionFilterLineEdit
				//	->text(),
                                QString::null,
                                selectionDialog->labelList());
		statusBar()->clear();
	}
}

void PTMainWindow::toggleDisplayParametersDialog( bool state )
{
	if( state ) {
		// Get the list of result keys (which are focus ids)
		// !! No longer need explicit list when results are
		// stored in an internal db table.
//		perfResultIds = dataTable->getKeyList();

		// Figure out which resource types vary for this list
		QStringList varyingResources
			= dataSource->
				comparePerformanceResults();

		// Show this list of resources in the new column dialog
		columnDataDialog->setAvailableResources( varyingResources,
				columnDataDialog );
		columnDataDialog->show();

	} else {
		columnDataDialog->hide();
	}
}

void PTMainWindow::addColumns( QStringList headings )
{
	// Add these headings to the list
	columnList += headings;

	// Update the dialogs that keep track of columns
	dataFilterDialog->setParameterList( columnList );
	plotDataDialog->setColumnNames( columnList );

	dataTable->addColumns( headings );
}

void PTMainWindow::removeColumns( QStringList dropnames )
{
	// Remove these headings from the list and the table.
	// Since we're likely to get the headers in the order they
	// appear in the list (and the table), optimize
	// this case by looking for the next column right after
	// the last one we found, instead of starting over at column
	// 0 each time we find a new header.  If no matching column
	// is found among those that remain, start again at column 0.
	// This algorithm assumes that the table headings match the
	// number and order of columnList.
	QStringList::iterator nit;
	QStringList::iterator colit = columnList.begin();
	int c = 0;
	for( nit = dropnames.begin(); nit != dropnames.end(); ++nit ) {
		for( int cols_not_checked = columnList.count();
			cols_not_checked > 0; --cols_not_checked ) {
			// Found a match; remove it and get ready to 
			// look at the next column for the next name to drop.
			if( *colit == *nit ) {
				dataTable->removeColumn( c );
				colit = columnList.remove( colit );
				// No need to advance c, since current item
				// will be removed, but don't let it point
				// past the end
				if( colit == columnList.end() ) {
					c = 0;
					colit = columnList.begin();
				}
				break;
			}
			// No match, look at next column
			if( ++colit == columnList.end() ) {
				c = 0;
				colit = columnList.begin();
			} else {
				++c;
			}
		}
	}

	// Update the dialogs that keep track of columns
	dataFilterDialog->setParameterList( columnList );
	plotDataDialog->setColumnNames( columnList );
}

void PTMainWindow::getColumnData( QStringList resourceNames,
		QStringList attributeNames )
{
	// Run through the list of resources and attributes,
	// requesting data for each one.  We use the list of
	// performance result ids gathered when the column
	// data dialog was shown.  Assume nothing has changed
	// in the data table since then.
	QStringList::Iterator it;
	for( it = resourceNames.begin(); it != resourceNames.end(); ++it ) {
		dataSource->getResultResources( *it );
	}

	for( it = attributeNames.begin(); it != attributeNames.end(); ++it ) {
		dataSource->getResultAttributes( *it );
	}
}

void PTMainWindow::columnDataDialogClosing()
{
	// Sets the state of the action widgets without triggering
	// any action (which would create an infinite loop)
	addDisplayParametersAction->setOn( false );
}

void PTMainWindow::toggleFilterDialog( bool state )
{
	if( state ) dataFilterDialog->show();
	else dataFilterDialog->hide();
}

void PTMainWindow::dataFilterDialogClosing()
{
	// Sets the state of the action widgets without triggering
	// any action (which would create an infinite loop)
	filterResultsAction->setOn( false );
}

void PTMainWindow::togglePlotDialog( bool state )
{
	if( state ) plotDataDialog->show();
	else plotDataDialog->hide();
}

void PTMainWindow::plotDataDialogClosing()
{
	// Sets the state of the action widgets without triggering
	// any action (which would create an infinite loop)
	plotDataAction->setOn( false );
}

void PTMainWindow::setFileOptions()
{
	// Set the current values as the defaults in the dialog
	fileOptionsDialog->setRowSep( rowSep );
	fileOptionsDialog->setColSep( colSep );
	fileOptionsDialog->setFileExtension( fileExtension );
	fileOptionsDialog->setIncludeHidden( includeHidden );

	if( fileOptionsDialog->exec() == QDialog::Accepted ) {
		rowSep = fileOptionsDialog->rowSep();
		colSep = fileOptionsDialog->colSep();
		fileExtension = fileOptionsDialog->fileExtension();
		includeHidden = fileOptionsDialog->includeHidden();
	}
}

void PTMainWindow::save()
{
	// If there's no current file name, do a Save As
	if( fileName.isEmpty() ) {
		saveAs();
		return;
	}

	QFile f( fileName );
	if( !f.open( QIODevice::WriteOnly ) ) {
		statusBar()->message( QString( "Could not write to %1" )
				.arg( fileName ), 2000 );
		return;
	}

	statusBar()->message( QString( "Saving %1...").arg( fileName ) );

	// Iterate over rows and columns, writing the data
	Q3TextStream outStream( &f );

	// First write the headings
	outStream << dataTable->headerText( colSep ) << rowSep;

	// Now write the data
	outStream << dataTable->dataText( colSep, rowSep, includeHidden );

	f.close();
	statusBar()->message( QString( "File %1 saved").arg( fileName ), 2000 );
}

void PTMainWindow::saveAs()
{
	// Ensure that the focus is in the main window (and not some
	// other dialog).  This is required on Macs (at least) to
	// be sure that the save dialog (which behaves as if it were part
	// of the main window) gets the focus.
	setActiveWindow();

	QString saveName = Q3FileDialog::getSaveFileName( QString(),
			"Text data files (*" + fileExtension + ");;"
			"All files (*.*)", this );
	if( !saveName.isEmpty() ) {
		fileName = saveName;
		save();
	} else {
		statusBar()->message( QString( "Save canceled" ), 2000 );
	}
}

void PTMainWindow::openFile()
{
	setActiveWindow();	// See comment in saveAs()

	QString openName = Q3FileDialog::getOpenFileName( QString(),
			"Text data files ( *" + fileExtension + ");;"
			"All files (*.*)", this );
	if( !openName.isEmpty() ) {
		fileName = openName;
		readFile();
	} else {
		statusBar()->message( QString( "Open canceled" ), 2000 );
	}
}

void PTMainWindow::readFile()
{
	QFile f( fileName );
	if( !f.open( QIODevice::ReadOnly ) ) {
		statusBar()->message( QString( "Could not read %1" )
				.arg( fileName ), 2000 );
		return;
	}

	statusBar()->message( QString( "Reading %1...").arg( fileName ) );

	Q3TextStream inStream( &f );

	dataTable->populateTable( inStream, colSep, rowSep );

	// Enable everything appropriate file data from a file
	handleNewResults( inStream );

	f.close();
	statusBar()->message( QString( "File %1 read" ).arg( fileName ), 2000 );
}

void PTMainWindow::printData( int id )
{
	if( ! printer->setup( this ) ) {	// Get printer information
		statusBar()->message( "Printing canceled", 2000 );
		return;
	}

	// Printing text?
	if( id == printDataAsTextId ) {
		statusBar()->message( QString( "Printing table..." ) );
		bool success = dataTable->printTable( printer, printFont );
		statusBar()->message( success ? "Printing complete"
				: "Printing failed", 2000 );
		return;
	}

	// Printing a plot...
	QString plotName = printItemsPopup->text( id );

	ChartViewer * chart_viewer = charts[plotName];
	if( chart_viewer == NULL ) {
		qWarning( "Couldn't find chart named %s!\n",
				qPrintable(plotName) );
		return;
	}

	statusBar()->message( QString( "Printing %1..." ).arg( plotName) );
	// Should pass the print font to use for labels... FIX
	bool success = chart_viewer->chart()->printChart( printer );
	statusBar()->message( success ? "Printing complete" : "Printing failed",
			2000 );
}

void PTMainWindow::exit()
{
	QApplication::exit( 0 );
}

void PTMainWindow::resetParamList( Q3ValueList<QPair<QString,QString> > params )
{

	// Clear the current list
	parameterListView->clear();

	// Put the parameter information in the table
	Q3ValueList<QPair<QString,QString> >::Iterator pit;
	for( pit = params.begin(); pit != params.end(); ++pit ) {
		new Q3ListViewItem( parameterListView, (*pit).first,
				(*pit).second );
	}
}

void PTMainWindow::handleNewResults( Q3SqlCursor cursor )
{
	// See if the query contains valid data; enable the
	// tools if so, otherwise disable them.  The test
	// here isn't as accurate as it should be, since the
	// cursor could be active but contain zero results.
	// I haven't found a way to detect that, since
	// cursor.size() can return -1 even for valid queries
	// (at least with Oracle).
	bool hasData = ( cursor.isActive() );

	addDisplayParametersAction->setEnabled( hasData );
	combineAction->setEnabled( hasData );
	filterResultsAction->setEnabled( hasData );
	plotDataAction->setEnabled( hasData );
	fileMenu->setItemEnabled( printMenuItemId, hasData );
	printToolButton->setEnabled( hasData );

	// Create a new list of the data columns and send it to
	// the interested widgets
	columnList.clear();
	for( unsigned i = 0; i < cursor.count(); ++i ) {
		columnList += cursor.fieldName( i );
	}

	dataFilterDialog->setParameterList( columnList );
	plotDataDialog->setColumnNames( columnList );

	// Clear the entries in the column selection dialog,
	// since we're creating a new table.  Then if the
	// dialog is already open, repopulate the list of
	// possible display parameters.
	columnDataDialog->reset();
	if( columnDataDialog->isVisible() )
		toggleDisplayParametersDialog( true );
}

void PTMainWindow::handleNewResults( Q3TextStream& ts )
{
	// Get the column headings, which should be in the first
	// line.  Make sure we're rewound to the start of the file.
	ts.device()->reset();

	bool hasData = ( ! ts.atEnd() );

	// Most likely, the lines are delimited by newline characters.
	// However, in case they aren't we read the whole file and
	// pick out everything up the first "newline" string.  Then
	// split that line into individual headers, which are stored
	// in the member object columnList
	QString headerLine = ts.read().section( rowSep, 0, 0 );
	columnList = QStringList::split( colSep, headerLine );

	dataFilterDialog->setParameterList( columnList );
	plotDataDialog->setColumnNames( columnList );

	// Can we really fish up additional data for items read
	// from a file??  Need to test this FIX
	addDisplayParametersAction->setEnabled( hasData );
	combineAction->setEnabled( hasData );
	
	filterResultsAction->setEnabled( hasData );
	plotDataAction->setEnabled( hasData );
	fileMenu->setItemEnabled( printMenuItemId, hasData );
	printToolButton->setEnabled( hasData );

	// Put the file information in the selection paraters dialog
	Q3ValueList<QPair<QString,QString> > params;
	params.append( QPair<QString,QString>( "File", fileName ) );
	resetParamList( params );

	// Clear the entries in the column selection dialog,
	// since we're creating a new table.  Then if the
	// dialog is already open, repopulate the list of
	// possible display parameters.
	columnDataDialog->reset();
	if( columnDataDialog->isVisible() )
		toggleDisplayParametersDialog( true );
}

void PTMainWindow::dbConnectionDone( bool success )
{
	newQueryAction->setEnabled( success );
	connectDbAction->setEnabled( ! success );

	// Give the user a query window if we have
	// an active connection, since that's normally first thing
	// to do after we connect to a database.

	// smithm 2008-6-26
	// In Qt 4 activate now takes a QAction::ActionEvent as a parameter.
	// I'm guessing that it should be QAction::Trigger
	// smithm 2008-7-1
	// This appears to be okay after running the program and looking through
	// the code becasue what this function emits is not connected to a slot.
	//if( success ) newQueryAction->activate();
	if( success )
		newQueryAction->activate(QAction::Trigger);
}

perfResultList * PTMainWindow::getPerfResultsForCombining(){
       // we'll grab the metric and value for each row selected by the user
       // we return the number of results selected
       // we return 0 for failure or if no results selected
       QString metricColumn = "metric";
       int metricCol = 0;
       QString valueColumn = "value";
       int valueCol = 0;
       QString resIdColumn = "result_id";
       int resIdCol = 0;
       
        Q3Header * topHeader = dataTable->horizontalHeader();
        for( int it = 0; it < topHeader->count(); ++it) {
                if( topHeader->label( it) == metricColumn ){
		   metricCol = it;
		}

                if( topHeader->label( it) == valueColumn ){
		   valueCol = it;
		}

                if( topHeader->label( it) == resIdColumn ){
		   resIdCol = it;
		}
        }

        // Sanity check; be sure we found  the columns we need
        if( metricCol >= topHeader->count() ) {
                qWarning( "metric column %s not found!\n", qPrintable(metricColumn) );
		return 0;
        }
        if( valueCol >= topHeader->count() ) {
                qWarning( "value column %s not found!\n", qPrintable(valueColumn) );
		return 0;
        }
        if( resIdCol >= topHeader->count() ) {
                qWarning( "value column %s not found!\n", qPrintable(resIdColumn) );
		return 0;
        }


	// Now create a perfResult for each selected row
        perfResultList * d = new perfResultList;
        int currCol;
        for( int row = 0; row < dataTable->numRows(); ++row ) {

             if( dataTable->isRowHidden( row ) ) continue;
             for( currCol = 0; currCol < dataTable->numCols(); ++currCol ) {
                // See if there are selections in this column
                if( ! dataTable->isColumnSelected( currCol, false ) )
                        continue;


                // Add data items to the perfresult 
                     if( dataTable->isSelected( row, currCol ) ) {
                          double val = dataTable->text( row, valueCol ).toDouble();
                          QString metric = dataTable->text( row, metricCol );
			  int resid = dataTable->text(row, resIdCol).toInt();
                          d->append( perfResult(  val,metric, resid ) );
                          //we've gotten the data from this row, so leave
                          break;
                     }
                }

	}

        return d;
}
    
void PTMainWindow::saveResults(){
    //save results to the database
    //first get the results to save from the data table
       QString resIdColumn = "result_id";
       int resIdCol = 0;
       QString savedColumn = "saved";
       int savedCol = 0;

        Q3Header * topHeader = dataTable->horizontalHeader();
        for( int it = 0; it < topHeader->count(); ++it) {
                if( topHeader->label( it) == resIdColumn ){
                   resIdCol = it;
                }
                if( topHeader->label( it) == savedColumn ){
                   savedCol = it;
                }
        }

        Q3ValueList<perfResult*> d;

        if( resIdCol >= topHeader->count() ) {
                qWarning( "value column %s not found!\n", qPrintable(resIdColumn) );
                return ;
        }

        if( savedCol >= topHeader->count() ) {
                qWarning( "saved column %s not found!\n", qPrintable(savedColumn) );
                return ;
        }

        // Now create a perfResult for each selected row
        int currCol;
        for( int row = 0; row < dataTable->numRows(); ++row ) {
             if( dataTable->isRowHidden( row ) ) continue; 
             for( currCol = 0; currCol < dataTable->numCols(); ++currCol ) {
                // See if there are selections in this column
                if( ! dataTable->isColumnSelected( currCol, false ) )
                        continue;
                // Add data items to the perfresult 
                     if( dataTable->isSelected( row, currCol ) ) {
                          int resid = dataTable->text(row, resIdCol).toInt();
                          int saved = dataTable->text(row,savedCol).toInt();
                          perfResult * pr  = new perfResult();
                          pr->setResultId(resid);
                          if (saved) pr->setSaved();
                          d.append( pr );
                          //we've gotten the data from this row, so leave
                          break;
                     } 
                }
        }

    perfResult * pr;
    Q3ValueList<perfResult*>::iterator it;
    Q3ValueList<int> resids;

    //then signal to the combinePerfResesDialog to save them
    for (it=d.begin(); it!= d.end(); ++it){
	if ((*it)->isSaved()){
	    QMessageBox::information(this, "Save error", "This result won't be saved. It's already saved.");
	    continue;
	}

       pr = (*it);

       emit(savePerfRes(pr,resids,true));
    }
}

void PTMainWindow::clearResults(){
    //clear results from a data sheet
    //first grab the data to clear from the data table
       QString resIdColumn = "result_id";
       int resIdCol = 0;
       QString savedColumn = "saved";
       int savedCol = 0;

        Q3Header * topHeader = dataTable->horizontalHeader();
        for( int it = 0; it < topHeader->count(); ++it) {
                if( topHeader->label( it) == resIdColumn ){
                   resIdCol = it;
                }

                if( topHeader->label( it) == savedColumn ){
                   savedCol = it;
                }
        }

        Q3ValueList<perfResult*> d;

        if( resIdCol >= topHeader->count() ) {
                qWarning( "value column %s not found!\n", qPrintable(resIdColumn));
                return ;
        }

        if( savedCol >= topHeader->count() ) {
                qWarning( "saved column %s not found!\n", qPrintable(savedColumn));
                return ;
        }

        // Now create a perfResult for each selected row
        int currCol;
        for( int row = 0; row < dataTable->numRows(); ++row ) {
             if( dataTable->isRowHidden( row ) ) continue;
             for( currCol = 0; currCol < dataTable->numCols(); ++currCol ) {
                // See if there are selections in this column
                if( ! dataTable->isColumnSelected( currCol, false ) )
                        continue;
                // Add data items to the perfresult 
                     if( dataTable->isSelected( row, currCol ) ) {
                          int resid = dataTable->text(row, resIdCol).toInt();
                          int saved = dataTable->text(row,savedCol).toInt();
                          perfResult * pr  = new perfResult();
                          pr->setResultId(resid);
                          if (saved) pr->setSaved();
                          d.append( pr );
                          //we've gotten the data from this row, so leave
                          break;
                     } 
                }
        }
        int items = d.count();

    if (items == 0){
          QMessageBox::information(this, "Not cleared","No performance results were cleared because none were selected. Please try again.");
	  return;
    }

    perfResult * pr;
    Q3ValueList<perfResult*>::iterator it;
    Q3ValueList<int> resids;

    //then signal to the combinedPerfResesDialog to clear them
    for (it=d.begin(); it!= d.end(); ++it){
       pr = (*it);
       emit(clearPerfRes(pr,0));
    }
}

void PTMainWindow::combinePerfResults(bool haveData){
    //combines performance results
    //if haveData is true, the request came from a data sheet
    //if haveData is false, the request came from the query window

   QStringList * opNames = combinePerfResesDialog->getOperatorNames();
   selectOperatorDialog->setOperators(*opNames); 

   if (selectOperatorDialog->exec() == QDialog::Accepted){
       if (haveData){
          int resCount = 0;
          perfResultList * prs; 
          prs = getPerfResultsForCombining();
          resCount = prs->count();

          if (!resCount){
             QMessageBox::information( this, "No Data Selected",
                             "No data was combined because none was "
                             "selected in the table.\n",
                             QMessageBox::Ok );
             return;
          }

          QString op = selectOperatorDialog->getSelectedOperator();
          combinePerfResesDialog->show();
          combinePerfResesDialog->combineData(op,prs);
       } else{
          perfResultList * prs;
          int typeCount = selectionDialog->typeCount();
          QString metrics = selectionDialog->metricIdList();
          QStringList labels = selectionDialog->labelList();
          prs = dataSource->getResultsForCombining(typeCount, metrics, labels);
          int resCount = prs->count();

          if (!resCount){
             //dataSource code gives the error message...
             return;
          }

          selectionDialog->close();
          QString op = selectOperatorDialog->getSelectedOperator();
          combinePerfResesDialog->show();
          combinePerfResesDialog->combineData(op,prs);
       }
       
   }

   delete opNames;
}

void PTMainWindow::createDataPlot( QString xAxis, QString dataLabel,
		QString plotName )
{
	// Create a chart that will show our data; have it destroy itself
	// when it closes.
	ChartViewer * chart_viewer = new ChartViewer( 0, 0,
			Qt::WDestructiveClose );

	// Pick out a name for the chart
	if( plotName.isEmpty() ) {
		plotName = "Bar Chart";
	}

	// Be sure the name is unique
	QString fullName = plotName;
	int count = 0;
	while( charts.find( fullName ) != 0 ) {
		fullName = plotName + " " + QString::number( ++count );
	}

	chart_viewer->setCaption( fullName );

	// Extract the chart so we can pass data to it
	TGBarChart * bar_chart = chart_viewer->chart();

	// Delete the data we give the chart when it's destroyed
	bar_chart->setAutoDeleteData( true );

	// Put the data in the plot
	bool hasData = plotData( bar_chart, xAxis, dataLabel );

	// Only show the display if there's some data in it
	if( hasData ) {
		chart_viewer->show();
		plotDataDialog->addPlotName( fullName );
		charts.insert( fullName, chart_viewer );
		printItemsPopup->insertItem( fullName );

		// Find out when this item is closed
		connect( chart_viewer, SIGNAL( closing( ChartViewer *) ),
			this, SLOT( chartViewerClosing( ChartViewer *) ) );
	}
	else delete chart_viewer;
}

void PTMainWindow::addDataToPlot( QString xAxis, QString dataLabel,
		QString plotName )
{
	// Look up the chart viewer, get its chart, and plot
	// the data on it.
	ChartViewer * chart_viewer = charts[plotName];
	if( chart_viewer == NULL ) {
		qWarning( "Couldn't find chart named %s!\n",
				qPrintable(plotName) );
		return;
	}

	plotData( chart_viewer->chart(), xAxis, dataLabel );
}
	

void PTMainWindow::chartViewerClosing( ChartViewer * chart_viewer )
{
	// Get the name of the view being closed and notify the
	// plot data dialog
	QString name = chart_viewer->caption();

	charts.remove( name );
	plotDataDialog->removePlotName( name );

	// Remove from popup window
	for( unsigned index = 0; index < printItemsPopup->count(); ++index ) {
		if( printItemsPopup->text( printItemsPopup->idAt( index ) )
				== name ) {
			printItemsPopup->removeItemAt( index );
		}
	}
}

bool PTMainWindow::plotData( TGBarChart * bar_chart, QString xAxis,
		QString dataLabel )
{
	// Figure out what data to plot.  Since the selections can
	// be disjoint, this is slightly complicated.  We'll look
	// through each selected column (ignoring the one that has
	// been designated as the X axis, if it was selected) and
	// create a data set for that column containing each selected
	// row and the corresponding data from the X axis column.

	// Determine the column that contains the X Axis.
	int xAxisCol;
	Q3Header * topHeader = dataTable->horizontalHeader();
	for( xAxisCol = 0; xAxisCol < topHeader->count(); ++xAxisCol ) {
		if( topHeader->label( xAxisCol ) == xAxis )
			break;
	}

	// Sanity check; be sure we found a valid column for the x axis
	if( xAxisCol >= topHeader->count() ) {
		qWarning( "Selected X Axis column %s not found!\n",
				qPrintable(xAxis) );
		return false;
	}

	// Now create a dataset for each selected column
	int maxItems = 0;
	double maxValue = -HUGE_VAL;	
	double minValue = 0;	// min scale should be 0 unless data is less
	int yAxisCol;
	BlankHandling blankHandling = NotChecked; // How to handle blank x vals
	for( yAxisCol = 0; yAxisCol < dataTable->numCols(); ++yAxisCol ) {
		// Don't plot data against itself
		// Disable for texting FIX
//		if( yAxisCol == xAxisCol ) continue;

		// See if there are selections in this column
		if( ! dataTable->isColumnSelected( yAxisCol, false ) )
			continue;
		// Create a new dataset
		Dataset * d = new Dataset;
		
		// Keep track of first selected row
		int firstSelRow = -1;

		// Add data items to it
		for( int row = 0; row < dataTable->numRows(); ++row ) {
			if( dataTable->isRowHidden( row ) ) continue;
			if( dataTable->isSelected( row, yAxisCol ) ) {
				double yVal = dataTable->text( row, yAxisCol )
								.toDouble();
				if( yVal > maxValue ) maxValue = yVal;
				if( yVal < minValue ) minValue = yVal;
				QString xVal = dataTable->text( row, xAxisCol );
				// Handle blank x value
				if( xVal.isEmpty() ) {
					if( blankHandling == NotChecked ) {
						blankHandling = askAboutBlanks(
								xAxis, row);
						if( blankHandling == Cancel ) {
							delete d;
							return false;
						}
					}
					if( blankHandling == Skip ) continue;
					// Blanks OK; set to empty string
					// not null string
					xVal = QString();
				}

				d->append( DataPoint( xVal, yVal ) );
				if( firstSelRow < 0 ) firstSelRow = row;
			}
		}

		// Sort the data by X value (this is a lexicographic sort)
		// so that matching items in future data sets will line up
		qSort( *d );

		// Check that the data set contains no data points with duplicate
		// x values.  If the data set contains duplicate x values this would
		// imply that the x would map to multiple y values.
		if (d->size() >= 2) {
			QList<DataPoint>::const_iterator cur_iter;
			QList<DataPoint>::const_iterator prev_iter;
			QMessageBox mb;
			mb.setText("The data set can't be plotted.");
			mb.setInformativeText("A duplicate item was found in the "
				"X Axis column.");
			mb.setIcon(QMessageBox::Warning);
		
			cur_iter = d->begin();
			prev_iter = d->begin();		
			for(++cur_iter; cur_iter != d->end(); ++cur_iter, ++prev_iter) {
				// if duplicate found inform user, clean up, and return
				if ((*cur_iter).x == (*prev_iter).x) {
					mb.setDetailedText(QString("Items from the X Axis column "
					"must be unique.\n") +
					(*cur_iter).x + QString(" was selected multiple times."));
					mb.exec();
					delete d;
					return false;
				}
			}
		}
		
		// Put the dataset in the chart.  Label with the column name.
		int items = d->count();
		if( items > 0 ) {
			// Get the data label from the selected row
			// of the column specified by the user
			int labelCol;
			for( labelCol = 0; labelCol < topHeader->count();
					++labelCol ) {
				if( topHeader->label( labelCol )
						== dataLabel )
					break;
			}

			// Produce a non-duplicate label
			QString label
				= dataTable->text( firstSelRow, labelCol );
			// Make sure the label is unique (data won't display
			// right if it's not)
			if( bar_chart->hasLabel( label ) ) {
				int i = 2;
				QString newLabel;
				do {
					newLabel = label + " ("
						+ QString::number( i++ ) + ")";
				} while( bar_chart->hasLabel( newLabel ) );
				label = newLabel;
			}

			bar_chart->addDataset( label, d );

			// Calculate max items
			// Max items is the number of elements in the union of the
			// set of current bar labels and the set of new bar labels.
			// A fast way to determine this is is to insert all the labels
			// into a hash and get the size of the hash.  This works since
			// QMap::insert does not allow duplicate keys.  Thus the
			// complexity of this operation is O(M+N+log(M+N)) were M is the
			// number of elements in the current bar label set and N is the
			// number of elments in new bar label set.
			QMap<QString, int> barLabelMap;
			QStringList curLabels = bar_chart->getBarLabels();
			QStringList::const_iterator cur_label_iter;
			for(cur_label_iter = curLabels.constBegin();
				cur_label_iter != curLabels.constEnd();
				++cur_label_iter)
			{	
				barLabelMap.insert(*cur_label_iter, 1);
			}
			QListIterator<DataPoint> new_label_iter(*d);
			while(new_label_iter.hasNext()) {
				barLabelMap.insert(new_label_iter.next().x, 1);
			}
			maxItems = barLabelMap.size();
		} else {
			delete d;
		}
	}

	// See if anything was plotted; if not, tell the user why
	if( maxItems <= 0 ) {
		QMessageBox::information( this, "No Data Selected",
				"No data was plotted because none was "
				"selected in the table.\n"
				"Be sure to select columns other than "
				"the X Axis column.",
				QMessageBox::Ok );
		return false;
	}

	bar_chart->setYScale( QMIN( minValue, bar_chart->ymin() ),
			QMAX( maxValue, bar_chart->ymax() ) );
	// 2008-6-25 smithm
	// xmax() returns a double, explicitly casting to an int
	bar_chart->setXScale( 0, QMAX( maxItems, (int)bar_chart->xmax() ) );
	return true;
}

PTMainWindow::BlankHandling
PTMainWindow::askAboutBlanks( QString col, int row )
{
	int response = QMessageBox::question ( this, "Blank Data Warning",
			"Column " + col + " has blank data at row " +
			QString::number( row + 1 ) + "\n"
			"What do you want to do?",
			"Allow blanks", "Skip all blanks", "Cancel plot", 0, 2);

	switch( response ) {
		case 0:
			return Allow;
		case 1:
			return Skip;
		default:
			return Cancel;
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


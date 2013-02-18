/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you want to add, delete, or rename functions or slots, use
** Qt Designer to update this file, preserving your code.
**
** You should not define a constructor or destructor in this file.
** Instead, write your code in functions called init() and destroy().
** These will automatically be called by the form's constructor and
** destructor.
*****************************************************************************/

#include <qmessagebox.h>
#include <qsqldatabase.h>
#include <qstringlist.h>
void DBConnectionDialog::init()
{
 // Get the list of available db connection types 
 QStringList drivers = QSqlDatabase::drivers();
 
 // Make sure we got at least one driver; if not, suggest
 // to the user how to fix this.
 if( drivers.empty()  ) {
  QMessageBox::warning( 0, "PerfTrack GUI",
          "No Qt database drivers could be found. "
          "Try setting the environment variable\n"
          "PERFTRACK_PLUGIN_PATH to a directory that "
          "contains the \"sqldrivers\" subdirectory\n"
          "with the Qt database drivers for this system. "
          "The Qt version of these drivers must match\n"
          "the version used to build this application "
          "(" QT_VERSION_STR ").\n"
          "Also set the dynamic library path (LD_LIBRARY_PATH, "
          "LIBPATH, or DYLD_LIBRARY_PATH)\n"
          "to the directory where the database's software "
          "libraries reside.",
          QMessageBox::Ok, Qt::NoButton );
  exit( -1 );
 }
 
 // Populate the combo box with driver names
 dbTypeComboBox->insertStringList( drivers );
 // Support an extension to the dialog for entering remote host information
 extensionShown = FALSE;
 ext = new RemoteHostExtension( this );
 setExtension( ext );
 setOrientation( Qt::Horizontal );
}


void DBConnectionDialog::toggleEntension()
{
 extensionShown = !extensionShown;
 showExtension( extensionShown );
 QString text = "Remote host settings ";
 text += (extensionShown ? "<<<" : ">>>");
 remoteHostPushButton->setText( text );
}


void DBConnectionDialog::clearEntries()
{
 dbNameLineEdit->clear();
 userNameLineEdit->clear();
 passwordLineEdit->clear();
 hostNameLineEdit->clear();
 dbTypeComboBox->clear();
 ext->hostNameLineEdit->clear();
 ext->userNameLineEdit->clear();
}

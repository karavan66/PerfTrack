#ifndef DBCONNECTIONDIALOG_H
#define DBCONNECTIONDIALOG_H

#include "ui_db_connection_dialog.h"
#include "remotehostextension.h"

#include <QDialog>

class DBConnectionDialog : public QDialog, public Ui::DBConnectionDialog
{
    Q_OBJECT

public:
    DBConnectionDialog(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~DBConnectionDialog();

    RemoteHostExtension * ext;

protected:
    bool extensionShown;

protected slots:
    virtual void languageChange();

    virtual void init();
    virtual void toggleEntension();
    virtual void clearEntries();

};

#endif // DBCONNECTIONDIALOG_H

#ifndef FILEOPTIONSDIALOGBASE_H
#define FILEOPTIONSDIALOGBASE_H

#include "ui_file_options_dialog_base.h"

#include <QDialog>

class FileOptionsDialogBase : public QDialog, public Ui::FileOptionsDialogBase
{
    Q_OBJECT

public:
    FileOptionsDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~FileOptionsDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // FILEOPTIONSDIALOGBASE_H

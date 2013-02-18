#ifndef COLUMNDATADIALOGBASE_H
#define COLUMNDATADIALOGBASE_H

#include <QDialog>

#include "ui_column_data_dialog_base.h"

class ColumnDataDialogBase : public QDialog, public Ui::ColumnDataDialogBase
{
    Q_OBJECT

public:
    ColumnDataDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~ColumnDataDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // COLUMNDATADIALOGBASE_H

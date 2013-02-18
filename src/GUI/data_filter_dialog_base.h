#ifndef DATAFILTERDIALOGBASE_H
#define DATAFILTERDIALOGBASE_H

#include "ui_data_filter_dialog_base.h"

#include <QDialog>

class DataFilterDialogBase : public QDialog, public Ui::DataFilterDialogBase
{
    Q_OBJECT

public:
    DataFilterDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~DataFilterDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // DATAFILTERDIALOGBASE_H

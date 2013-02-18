#ifndef SELECTOPERATORDIALOGBASE_H
#define SELECTOPERATORDIALOGBASE_H

#include "ui_select_operator_dialog_base.h"

#include <QDialog>

class SelectOperatorDialogBase : public QDialog, public Ui::Dialog
{
    Q_OBJECT

public:
    SelectOperatorDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~SelectOperatorDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // SELECTOPERATORDIALOGBASE_H

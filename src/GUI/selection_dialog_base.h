#ifndef SELECTIONDIALOGBASE_H
#define SELECTIONDIALOGBASE_H

#include "ui_selection_dialog_base.h"

#include <QDialog>

class SelectionDialogBase : public QDialog, public Ui::SelectionDialogBase
{
    Q_OBJECT

public:
    SelectionDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~SelectionDialogBase();

public slots:
    virtual void combineResultsSelected();
    virtual void labelSelected();

protected slots:
    virtual void languageChange();

};

#endif // SELECTIONDIALOGBASE_H

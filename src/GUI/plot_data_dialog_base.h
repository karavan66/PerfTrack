#ifndef PLOTDATADIALOGBASE_H
#define PLOTDATADIALOGBASE_H

#include "ui_plot_data_dialog_base.h"

#include <QDialog>

class PlotDataDialogBase : public QDialog, public Ui::PlotDataDialogBase
{
    Q_OBJECT

public:
    PlotDataDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~PlotDataDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // PLOTDATADIALOGBASE_H

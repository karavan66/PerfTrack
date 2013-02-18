#ifndef PTMAINWINDOWBASE_H
#define PTMAINWINDOWBASE_H

#include "ui_pt_main_window_base.h"

#include <Q3MainWindow>

class PTMainWindowBase : public Q3MainWindow, public Ui::PTMainWindowBase
{
    Q_OBJECT

public:
    PTMainWindowBase(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = Qt::WType_TopLevel);
    ~PTMainWindowBase();

public slots:
    virtual void combinePerfResults();
    virtual void saveResults();
    virtual void clearResults();

protected slots:
    virtual void languageChange();

};

#endif // PTMAINWINDOWBASE_H

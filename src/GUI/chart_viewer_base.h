#ifndef CHARTVIEWERBASE_H
#define CHARTVIEWERBASE_H

#include "ui_chart_viewer_base.h"

#include <Q3MainWindow>

class ChartViewerBase : public Q3MainWindow, public Ui::ChartViewerBase
{
    Q_OBJECT

public:
    ChartViewerBase(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = Qt::WType_TopLevel);
    ~ChartViewerBase();

protected slots:
    virtual void languageChange();

};

#endif // CHARTVIEWERBASE_H

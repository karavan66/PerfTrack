#ifndef COMBPERFRESWIDGETBASE_H
#define COMBPERFRESWIDGETBASE_H

#include "ui_comb_perfRes_widget_base.h"

#include <QWidget>

class CombPerfResWidgetBase : public QWidget, public Ui::CombPerfResWidgetBase
{
    Q_OBJECT

public:
    CombPerfResWidgetBase(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = 0);
    ~CombPerfResWidgetBase();

public slots:
    virtual void getCloseTabClick();
    virtual void getSaveToDBClick();
    virtual void getAddToExistingSheetClick();
    virtual void getAddToNewSheetClick();
    virtual void somethingChanged(const QString&);

protected slots:
    virtual void languageChange();

};

#endif // COMBPERFRESWIDGETBASE_H

#ifndef RESOURCESELECTORBASE_H
#define RESOURCESELECTORBASE_H

#include "ui_resource_selector_base.h"

#include <QWidget>

class ResourceSelectorBase : public QWidget, public Ui::ResourceSelectorBase
{
    Q_OBJECT

public:
    ResourceSelectorBase(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = 0);
    ~ResourceSelectorBase();

protected slots:
    virtual void languageChange();

};

#endif // RESOURCESELECTORBASE_H

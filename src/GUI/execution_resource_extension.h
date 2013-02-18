#ifndef EXECUTIONRESOURCEEXTENSION_H
#define EXECUTIONRESOURCEEXTENSION_H

#include "ui_execution_resource_extension.h"

#include <QWidget>

class ExecutionResourceExtension : public QWidget, public Ui::ExecutionResourceExtension
{
    Q_OBJECT

public:
    ExecutionResourceExtension(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = 0);
    ~ExecutionResourceExtension();

protected slots:
    virtual void languageChange();

};

#endif // EXECUTIONRESOURCEEXTENSION_H

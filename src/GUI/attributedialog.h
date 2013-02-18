#ifndef ATTRIBUTEDIALOG_H
#define ATTRIBUTEDIALOG_H

#include "ui_attributedialog.h"
#include "execution_resource_extension.h"

#include <QDialog>

class AttributeDialog : public QDialog, public Ui::AttributeDialog
{
    Q_OBJECT

public:
    AttributeDialog(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~AttributeDialog();

    ExecutionResourceExtension * executionResourceExtension;

public slots:
    void showExecutionExtension( bool show );

protected:
    virtual void init();

protected slots:
    virtual void languageChange();

};

#endif // ATTRIBUTEDIALOG_H

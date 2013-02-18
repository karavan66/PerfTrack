#ifndef REMOTEHOSTEXTENSION_H
#define REMOTEHOSTEXTENSION_H

#include "ui_remotehostextension.h"

#include <QWidget>

class RemoteHostExtension : public QWidget, public Ui::RemoteHostExtension
{
    Q_OBJECT

public:
    RemoteHostExtension(QWidget* parent = 0, const char* name = 0, Qt::WindowFlags fl = 0);
    ~RemoteHostExtension();

protected slots:
    virtual void languageChange();

};

#endif // REMOTEHOSTEXTENSION_H

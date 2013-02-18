#ifndef COMBINEPERFRESESDIALOGBASE_H
#define COMBINEPERFRESESDIALOGBASE_H

#include <qvariant.h>


#include <Qt3Support/Q3MimeSourceFactory>
#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QHeaderView>

QT_BEGIN_NAMESPACE

class Ui_CombinePerfResesDialogBase
{
public:

    void setupUi(QDialog *CombinePerfResesDialogBase)
    {
        if (CombinePerfResesDialogBase->objectName().isEmpty())
            CombinePerfResesDialogBase->setObjectName(QString::fromUtf8("CombinePerfResesDialogBase"));
        CombinePerfResesDialogBase->resize(594, 474);

        retranslateUi(CombinePerfResesDialogBase);

        QMetaObject::connectSlotsByName(CombinePerfResesDialogBase);
    } // setupUi

    void retranslateUi(QDialog *CombinePerfResesDialogBase)
    {
        CombinePerfResesDialogBase->setWindowTitle(QApplication::translate("CombinePerfResesDialogBase", "Combined Performance Results", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class CombinePerfResesDialogBase: public Ui_CombinePerfResesDialogBase {};
} // namespace Ui

QT_END_NAMESPACE

class CombinePerfResesDialogBase : public QDialog, public Ui::CombinePerfResesDialogBase
{
    Q_OBJECT

public:
    CombinePerfResesDialogBase(QWidget* parent = 0, const char* name = 0, bool modal = false, Qt::WindowFlags fl = 0);
    ~CombinePerfResesDialogBase();

protected slots:
    virtual void languageChange();

};

#endif // COMBINEPERFRESESDIALOGBASE_H

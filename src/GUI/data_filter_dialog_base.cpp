#include "data_filter_dialog_base.h"

#include <qvariant.h>

#include "data_filter_dialog_base.moc"
/*
 *  Constructs a DataFilterDialogBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  true to construct a modal dialog.
 */
DataFilterDialogBase::DataFilterDialogBase(QWidget* parent, const char* name, bool modal, Qt::WindowFlags fl)
    : QDialog(parent, name, modal, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
DataFilterDialogBase::~DataFilterDialogBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void DataFilterDialogBase::languageChange()
{
    retranslateUi(this);
}


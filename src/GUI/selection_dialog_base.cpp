#include "selection_dialog_base.h"

#include <qvariant.h>
#include "resource_selector.h"

#include "selection_dialog_base.moc"
/*
 *  Constructs a SelectionDialogBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 *  The dialog will by default be modeless, unless you set 'modal' to
 *  true to construct a modal dialog.
 */
SelectionDialogBase::SelectionDialogBase(QWidget* parent, const char* name, bool modal, Qt::WindowFlags fl)
    : QDialog(parent, name, modal, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
SelectionDialogBase::~SelectionDialogBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void SelectionDialogBase::languageChange()
{
    retranslateUi(this);
}

void SelectionDialogBase::combineResultsSelected()
{
    qWarning("SelectionDialogBase::combineResultsSelected(): Not implemented yet");
}

void SelectionDialogBase::labelSelected()
{
    qWarning("SelectionDialogBase::labelSelected(): Not implemented yet");
}


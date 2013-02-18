#include "comb_perfRes_widget_base.h"

#include <qvariant.h>

#include "comb_perfRes_widget_base.moc"
/*
 *  Constructs a CombPerfResWidgetBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 */
CombPerfResWidgetBase::CombPerfResWidgetBase(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : QWidget(parent, name, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
CombPerfResWidgetBase::~CombPerfResWidgetBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void CombPerfResWidgetBase::languageChange()
{
    retranslateUi(this);
}

void CombPerfResWidgetBase::getCloseTabClick()
{
    qWarning("CombPerfResWidgetBase::getCloseTabClick(): Not implemented yet");
}

void CombPerfResWidgetBase::getSaveToDBClick()
{
    qWarning("CombPerfResWidgetBase::getSaveToDBClick(): Not implemented yet");
}

void CombPerfResWidgetBase::getAddToExistingSheetClick()
{
    qWarning("CombPerfResWidgetBase::getAddToExistingSheetClick(): Not implemented yet");
}

void CombPerfResWidgetBase::getAddToNewSheetClick()
{
    qWarning("CombPerfResWidgetBase::getAddToNewSheetClick(): Not implemented yet");
}

void CombPerfResWidgetBase::somethingChanged(const QString&)
{
    qWarning("CombPerfResWidgetBase::somethingChanged(const QString&): Not implemented yet");
}


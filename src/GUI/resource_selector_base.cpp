#include "resource_selector_base.h"

#include <qvariant.h>

#include "resource_selector_base.moc"
/*
 *  Constructs a ResourceSelectorBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 */
ResourceSelectorBase::ResourceSelectorBase(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : QWidget(parent, name, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
ResourceSelectorBase::~ResourceSelectorBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void ResourceSelectorBase::languageChange()
{
    retranslateUi(this);
}


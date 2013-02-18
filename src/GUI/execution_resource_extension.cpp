#include "execution_resource_extension.h"

#include <qvariant.h>

#include "execution_resource_extension.moc"
/*
 *  Constructs a ExecutionResourceExtension as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 */
ExecutionResourceExtension::ExecutionResourceExtension(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : QWidget(parent, name, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
ExecutionResourceExtension::~ExecutionResourceExtension()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void ExecutionResourceExtension::languageChange()
{
    retranslateUi(this);
}


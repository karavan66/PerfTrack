#include "remotehostextension.h"

#include <qvariant.h>

#include "remotehostextension.moc"
/*
 *  Constructs a RemoteHostExtension as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 */
RemoteHostExtension::RemoteHostExtension(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : QWidget(parent, name, fl)
{
    setupUi(this);

}

/*
 *  Destroys the object and frees any allocated resources
 */
RemoteHostExtension::~RemoteHostExtension()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void RemoteHostExtension::languageChange()
{
    retranslateUi(this);
}


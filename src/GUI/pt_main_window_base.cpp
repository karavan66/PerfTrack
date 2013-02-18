#include "pt_main_window_base.h"

#include <qvariant.h>
#include "data_table.h"

#include "pt_main_window_base.moc"
/*
 *  Constructs a PTMainWindowBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 */
PTMainWindowBase::PTMainWindowBase(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : Q3MainWindow(parent, name, fl)
{
    setupUi(this);

    (void)statusBar();
}

/*
 *  Destroys the object and frees any allocated resources
 */
PTMainWindowBase::~PTMainWindowBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void PTMainWindowBase::languageChange()
{
    retranslateUi(this);
}

void PTMainWindowBase::combinePerfResults()
{
    qWarning("PTMainWindowBase::combinePerfResults(): Not implemented yet");
}

void PTMainWindowBase::saveResults()
{
    qWarning("PTMainWindowBase::saveResults(): Not implemented yet");
}

void PTMainWindowBase::clearResults()
{
    qWarning("PTMainWindowBase::clearResults(): Not implemented yet");
}


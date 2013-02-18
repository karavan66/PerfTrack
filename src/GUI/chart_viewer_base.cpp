#include "chart_viewer_base.h"

#include <qvariant.h>
#include <qimage.h>
#include <qpixmap.h>

#include "tg_barchart.h"

#include "chart_viewer_base.moc"
/*
 *  Constructs a ChartViewerBase as a child of 'parent', with the
 *  name 'name' and widget flags set to 'f'.
 *
 */
ChartViewerBase::ChartViewerBase(QWidget* parent, const char* name, Qt::WindowFlags fl)
    : Q3MainWindow(parent, name, fl)
{
    setupUi(this);

    (void)statusBar();
}

/*
 *  Destroys the object and frees any allocated resources
 */
ChartViewerBase::~ChartViewerBase()
{
    // no need to delete child widgets, Qt does it all for us
}

/*
 *  Sets the strings of the subwidgets using the current
 *  language.
 */
void ChartViewerBase::languageChange()
{
    retranslateUi(this);
}


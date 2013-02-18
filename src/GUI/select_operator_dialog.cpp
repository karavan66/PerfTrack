
#include <qcombobox.h>

#include "select_operator_dialog.h"

#include "select_operator_dialog.moc"

SelectOperatorDialog::SelectOperatorDialog(QWidget * parent, const char* name){

}

SelectOperatorDialog::~SelectOperatorDialog(){
}

void SelectOperatorDialog::setOperators(QStringList opNames){
    operatorCombBox->clear();
    for ( QStringList::Iterator it = opNames.begin(); it != opNames.end(); ++it){
        operatorCombBox->insertItem(*it);
    }
		       
}

QString SelectOperatorDialog::getSelectedOperator(){
    return operatorCombBox->currentText();
}


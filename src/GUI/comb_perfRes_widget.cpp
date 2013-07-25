#include "comb_perfRes_widget.h"

#include "comb_perfRes_widget.moc"

CombPerfResWidget::CombPerfResWidget(QWidget * Parent, QString op, perfResult * pr, QStringList Metrics, int numValsCombined){

    CreateNewDataSheetBtn->hide();
     OperatorNameLbl->setText(op);

     myparent = Parent;
     value = pr->getValue();
     saved = false;
     QString val;
     val.setNum(value,'g');
     ValueLbl->setText(val);

     metrics = Metrics;
     MetricsListBox->clear();
     MetricsListBox->insertStringList(metrics);

     QString numVals;
     numVals.setNum(numValsCombined);
     NumValuesLbl->setText(numVals);

     resultIds = pr->getParentResultIds();
     perfRes = pr;

     QStringList labels = ((CombinePerfResesDialog*)myparent)->getAllLabelNamesFromDB();
     labels.prepend("");
     NewLabelCmbBox->insertStringList(labels);
     QStringList mets = ((CombinePerfResesDialog*)myparent)->getAllMetricNamesFromDB();
     mets.prepend("");
     NewMetricCmbBox->insertStringList(mets);
     QStringList units = ((CombinePerfResesDialog*)myparent)->getAllUnitsNamesFromDB();
     units.prepend("");
     NewUnitsCmbBox->insertStringList(units);
 
     connect(myparent, SIGNAL(saveSuccess(perfResult*)), this, SLOT(saveCompleted(perfResult*)));



}


void CombPerfResWidget::getCloseTabClick(){
     if (saved){
        if(!QMessageBox::question(this,"Remove this Tab?", "Are you sure you want to remove this tab?", "&Yes", "&No", QString::null, 1, 0))
         emit(closeMe((QWidget*)this));
	 return;
     }
     if(!QMessageBox::question(this,"Delete This Result?", "Are you sure you want to delete this result?", "&Yes", "&No", QString::null, 1, 0))
         emit(closeMe((QWidget*)this));
}

void CombPerfResWidget::getSaveToDBClick(){
     //get the current values of the parameters the user has specified
     QString label = NewLabelCmbBox->currentText();
     perfRes->setLabel(label);
     QString metric = NewMetricCmbBox->currentText();
     if (metric == "" or metric == QString::null){
          QMessageBox::information( this, "Performance Result Error","All performance results need to have a metric. Please select a metric and try again." );
	  return;
     }
     perfRes->setMetric(metric);
     QString units = NewUnitsCmbBox->currentText();
     perfRes->setUnits(units);
     QString startTime = NewStartTimeText->text();
     perfRes->setStartTime(startTime);
     QString endTime = NewEndTimeText->text();
     perfRes->setEndTime(endTime);
     if (saved){
        QMessageBox::information(this, "Already Saved!", "This result has already been saved to the database. It will not be saved again.");
	return;
     }
     emit(saveMe(perfRes,resultIds));

}

void CombPerfResWidget::saveCompleted(perfResult * pr){
    if (perfRes == pr){   //if it was my perfRes that was saved
        saved = true;
        SaveToDbBtn->setDisabled(true);
        NewMetricCmbBox->setDisabled(true);
        NewLabelCmbBox->setDisabled(true);
        NewUnitsCmbBox->setDisabled(true);
        NewStartTimeText->setDisabled(true);
        NewEndTimeText->setDisabled(true);
    }
}

void CombPerfResWidget::getAddToExistingSheetClick(){
     //get the current values of the parameters the user has specified
     QString label = NewLabelCmbBox->currentText();
     perfRes->setLabel(label);
     QString metric = NewMetricCmbBox->currentText();
     if (metric == "" or metric == QString::null){
          QMessageBox::information( this, "Performance Result Error","All performance results need to have a metric. Please select a metric and try again." );
          return;
     }
     perfRes->setMetric(metric);
     QString units = NewUnitsCmbBox->currentText();
     perfRes->setUnits(units);
     QString startTime = NewStartTimeText->text();
     perfRes->setStartTime(startTime);
     QString endTime = NewEndTimeText->text();
     perfRes->setEndTime(endTime);

     emit(addMeToExistingSheet(perfRes));
}

void CombPerfResWidget::getAddToNewSheetClick(){
     //get the current values of the parameters the user has specified
     QString label = NewLabelCmbBox->currentText();
     perfRes->setLabel(label);
     QString metric = NewMetricCmbBox->currentText();
     if (metric == "" or metric == QString::null){
          QMessageBox::information( this, "Performance Result Error","All performance results need to have a metric. Please select a metric and try again." );
          return;
     }
     perfRes->setMetric(metric);
     QString units = NewUnitsCmbBox->currentText();
     perfRes->setUnits(units);
     QString startTime = NewStartTimeText->text();
     perfRes->setStartTime(startTime);
     QString endTime = NewEndTimeText->text();
     perfRes->setEndTime(endTime);

     emit(addMeToNewSheet(perfRes));
}

void CombPerfResWidget::somethingChanged(const QString& s){
    //hmm, not using this now, should remove when there is time
}

CombPerfResWidget::~CombPerfResWidget(){

}


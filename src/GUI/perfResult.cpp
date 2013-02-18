
#include "perfResult.h"
//Added by qt3to4:
#include <Q3ValueList>

perfResult::perfResult(){
    value = 0.0;
    metric = QString::null;
    resultId = -1;
    start_time = QString::null;
    end_time = QString::null;
    label = QString::null;
    units = QString::null;
    saved = false;
    index = -1;

}

perfResult::perfResult(double val, QString met, int res){
    value = val;
    metric = met;
    resultId = res;
    start_time = QString::null;
    end_time = QString::null;
    label = QString::null;
    units = QString::null;
    saved = false;
    index = -1;

}

void perfResult::setIndex(int x){
    index = x;
}

int perfResult::getIndex(){
    return index;
}

perfResult::~perfResult(){

}

void perfResult::setSaved(){
     saved = true;
}

bool perfResult::isSaved(){
     return saved;
}

double perfResult::getValue(){
  return value;
}

void perfResult::setValue(double val){
   value = val;
}

Q3ValueList<int> perfResult::getParentResultIds(){
   return parentResIds;
}

void perfResult::setParentResultIds(Q3ValueList<int> ids){
   parentResIds = ids;
}

QString perfResult::getMetric(){
  return metric;
}

void perfResult::setMetric(QString met){
  metric = met;
}

int perfResult::getResultId(){
  return resultId;
}

void perfResult::setResultId(int id){
   resultId = id;
}

Context perfResult::getContext(){
    return context;
}

void perfResult::setContext(Context c){
    context = c;
}

QString perfResult::getLabel(){
    return label;
}

void perfResult::setLabel(QString l){
    label = l;
}

QString perfResult::getUnits(){
    return units;
}

void perfResult::setUnits(QString u){
    units = u;
}

QString perfResult::getStartTime(){
    return start_time;
}

void perfResult::setStartTime(QString s){
   start_time = s;
}

QString perfResult::getEndTime(){
   return end_time;
}

void perfResult::setEndTime(QString e){
   end_time = e;
}

void perfResult::addToSheet(int x){
   dataSheets.append(x); 
}

bool perfResult::isOnSheet(int x){
   Q3ValueList<int>::iterator it;
   for(it = dataSheets.begin(); it != dataSheets.end(); ++it){
       if ((*it) == x)
	   return true;
   }

   return false;
}

void perfResult::removeFromSheet(int x){

   Q3ValueList<int>::iterator it;
   for(it = dataSheets.begin(); it != dataSheets.end(); ++it){
      if((*it) == x){
         dataSheets.remove(it);
	 break;
      }
   }
}

Q3ValueList<int> perfResult::getSheets(){
   return dataSheets;
}


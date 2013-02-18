
#ifndef PERFRESULT_H
#define PERFRESULT_H

#include <qstring.h>
#include <qstringlist.h>
#include <q3valuelist.h>
#include "resource_type_and_name.h"

class perfResult{
   public:
       perfResult();
       perfResult(double val, QString met, int res);
       ~perfResult();
       double getValue();
       void setValue(double);
       Q3ValueList<int> getParentResultIds();
       void setParentResultIds(Q3ValueList<int>);
       QString getMetric();
       void setMetric(QString);
       int getResultId();
       void setResultId(int);
       Context getContext();
       void setContext(Context);
       QString getLabel();
       void setLabel(QString);
       QString getStartTime();
       void setStartTime(QString);
       QString getEndTime();
       void setEndTime(QString);
       QString getUnits();
       void setUnits(QString);
       bool isSaved();
       void setSaved();
       int getIndex();
       void setIndex(int);
       void addToSheet(int);
       void removeFromSheet(int);
       bool isOnSheet(int);
       Q3ValueList<int> getSheets();

   private:
       double value;
       QString metric;
       int resultId;  // the database id
       int index ;  // the identifier that the GUI will use
                        // need a different one than db one in case it's not saved yet
       Q3ValueList<int> dataSheets; // a list of the dataSheet indexes that this belongs to
       QString units;
       Context context;
       QString start_time;
       QString end_time;
       QString label;
       bool saved;
       Q3ValueList<int> parentResIds;
};


typedef Q3ValueList<perfResult> perfResultList;

#endif 

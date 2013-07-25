#ifdef __APPLE__
    #include <Python/Python.h>
#else
    #include <Python.h>
#endif

#include "combine_perfReses_dialog.h"

//Added by qt3to4
#include <Q3ValueList>

#include "combine_perfReses_dialog.moc"

CombinePerfResesDialog::CombinePerfResesDialog(QWidget * parent, const char * name, DataAccess * da) : CombinePerfResesDialogBase(parent, name){

    Py_Initialize(); 
    resultNum = 1;
    combPRtabWidget  = new QTabWidget(this);
    combPRtabWidget->setGeometry(0,0,611,501);
    dataSource = da;
    prIndex = 0;
    metricNames = getAllMetricNamesFromDB();
    //fprintf(stderr, "retrieved %d metrics from db", metricNames.size());
    //for (QStringList::Iterator it = metricNames.begin(); it != metricNames.end(); ++it)
	 //fprintf(stderr, "metric is %s\n", (*it).latin1());
    unitsNames = getAllUnitsNamesFromDB();
    labelNames = getAllLabelNamesFromDB();
}

void CombinePerfResesDialog::initializeOperators(){

    //import the file operator.py
    //this initializes the operators
    //and implements the operator functionality
    PyObject * module, *func,*fName,*opInst,*plugIns;
    module = PyImport_ImportModule("operator_pt");
    if (module == 0){
		PyErr_Print();
       fprintf(stderr, "SelectOperatorDialog::initialize can't load operator module\n");
    }

//    fName = PyString_FromString("operator");
    func = PyObject_GetAttrString(module, "operator");
    if (!func){
		PyErr_Print();
        fprintf(stderr,"SelectOperatorDialog::initialize could not access class operator\n");
    }
    //get an instance of the class
    opInst = PyEval_CallObject(func, NULL);
    if (!opInst){
       fprintf(stderr,"SelectOperatorDialog::initialize failed to get instance of class operator\n");
    }
    //fprintf(stderr,"opinst is %u\n",opInst);
    //keep a copy of the operator instance for future use
    pyOpClassInst = opInst;
    //get the plugins that class operator knows about
    plugIns = PyObject_CallMethod(opInst, (char *)"getPlugins", (char *)"", NULL);
    if (!plugIns){
       fprintf(stderr,"SelectOperatorDialog::initialize failed to get plugins from class operator\n");
    }
   //should be a list of plugins
    int isList = PyList_Check(plugIns);
    if (!isList){
       fprintf(stderr,"SelectOperatorDialog::initialize plugins returned from class operator not a list\n");
    }

    // how many plugins did we get
    int len = PyList_Size(plugIns);
    //loop through the plugins
    for (int x=0; x < len; ++x){
       //get the plugin from the list
       PyObject * obj = PyList_GetItem(plugIns, x);
       if (!obj){
           fprintf(stderr,"SelectOperatorDialog::initialize failed to get plugin item\n");
       }
       //get the plugin's name 
       PyObject * pyName = PyObject_CallMethod(opInst, (char *)"getName", (char *)"S", obj);
       if (!pyName){
          fprintf(stderr,"SelectOperatorDialog::initialize callMethod failed for getName\n");
       }
       int check = PyString_Check(pyName);
       if (!check){
          fprintf(stderr,"SelectOperatorDialog::initialize operator name is not string!\n");
       }
       char * name = PyString_AsString(pyName);
       if (!name ){
           fprintf(stderr,"SelectOperatorDialog::initialize operator name is null\n");
       }
       //fprintf(stderr,"got name:%s\n", name);
       //fprintf(stderr,"obj for %s is %u\n",name,obj);
       //get the return type of the operator
       PyObject * pyRetType = PyObject_CallMethod(opInst, (char *)"getRetType", (char *)"S", obj);
       check = PyString_Check(pyRetType);
       if (!check){
          fprintf(stderr,"retType is not string!\n");
          return ;
       }
       char * retType = PyString_AsString(pyRetType);
       if (!retType){
          fprintf(stderr,"Could not get cstring for retType\n");
          return ;
       }
       //fprintf(stderr,"got retType:%s\n", retType);
       //get the arguments expected by the operator
       PyObject * pyArgList = PyObject_CallMethod(opInst, (char *)"getArgList", (char *)"S", obj);
       check = PyList_Check(pyArgList);
       if (!check){
          fprintf(stderr,"argument list not a list type\n");
          return ;
       }
       //how many args are there?
       int numArgs = PyList_Size(pyArgList);
       // make a new python dictionary to hold them
       PyObject * pyArgs = PyDict_New();
       ArgumentList argList;
       for (int i = 0; i < numArgs; ++i){
          PyObject * arg = PyList_GetItem(pyArgList,i);
          check = PyTuple_Check(arg);
          if (!check){
             fprintf(stderr,"argument to %s not a tuple\n",name);
             return ;
          }
          // first item in tuple is name, second is type
          PyObject * pyArgName = PyTuple_GetItem(arg,0);
          check = PyString_Check(pyArgName);
          if (!check){printf("argName not string\n"); return ;}
          PyObject * pyArgType = PyTuple_GetItem(arg,1);
          check = PyString_Check(pyArgType);
          if (!check){printf("argType not string\n"); return ;}
          char * argName = PyString_AsString(pyArgName);
          if (!check){printf("argName conversion failed\n"); return ;}
          char * argType = PyString_AsString(pyArgType);
          if (!check){printf("argType conversion failed\n"); return ;}
          ///fprintf(stderr,"arguments are name:%s, type:%s\n",argName,argType);

       }
       //save the operator information in our list of operators
       QString qname = name;
       QString returnType =  retType;
       Operator * op = new Operator(qname,retType,argList,obj);
       operators.append(*op);
    }

}

QStringList * CombinePerfResesDialog::getOperatorNames(){
    //returns a list of operator names 
    QStringList * names = new QStringList();
    for (OperatorList::Iterator it = operators.begin(); it != operators.end(); ++it){
       names->append((*it).getName());
    }	

    return names;

}

Operator * CombinePerfResesDialog::getOperatorByName(QString opName){
    //given an operator name, return a pointer to the operator with that name
    int i = 0;
    Operator * op;
    for (OperatorList::Iterator it = operators.begin(); it != operators.end(); ++it){
    
	 if ((*it).getName() == opName){
	     //stupid compiler
	     op = (Operator*)&(*it);
	     return op;
	 }
	 ++i;
    }
    return NULL;
}

void CombinePerfResesDialog::combineData(QString opName, perfResultList * d){
    //combine performance results
    //given an operator name, and a list of performance results
    Operator * op = getOperatorByName(opName);
    if (!op){
       fprintf(stderr, "couldn't get operator given name:%s\n", qPrintable(opName));
       return;
    }
    //get the python object for the operator
    PyObject * pyOpObj = (PyObject*)op->getPyOpObject();
    ArgumentList args = op->getArgumentList();
    int numArgs = args.size();
    //fprintf(stderr, "there are %d args for this operator\n",numArgs);
    PyObject * pyArgs = PyDict_New();
    for (int i = 0; i< numArgs; ++i){
       //omitting for now because the base operators do not take arguments
       //future work! TODO
    }
    //create a Python List to send in the data
    PyObject * dataList = PyList_New(d->size());
    // also grab the metric names, because we will need them later
    QStringList metrics; 
    Q3ValueList<int> resIds;
    if (!dataList){printf("failed to create datalist\n"); return ;}
    int index = 0;
    int check;
    for (perfResultList::Iterator it = d->begin(); it != d->end(); ++it){
	//fprintf(stderr,"adding %f to datalist\n", (*it).getValue());
	//get the value from each performance result
        PyObject * pyVal = PyFloat_FromDouble((double)(*it).getValue());
        if (!pyVal){printf("failed to create python value\n"); return ;}
	//add the value to the list of data
        check = PyList_SetItem(dataList,index, pyVal);
        if (check==-1){printf("failed to add data to python list\n");return ;}
        //fprintf(stderr, "adding %s to metrics list\n",(*it).getMetric().latin1());	
	QStringList::iterator mt;
        if (metrics.find((*it).getMetric()) == metrics.end()) //don't want duplicates in list
	   metrics.append((*it).getMetric());
	resIds.append((*it).getResultId());
	++index;
    }
    //call the operator with the data
    PyObject * ret = PyObject_CallMethod((PyObject*)pyOpClassInst, (char *)"operator", 
                                         (char *)"SSS", pyOpObj,dataList,pyArgs);
    QString retType = op->getReturnType();
    //TODO: only supporting float and int types now
    double val; 
    if (retType == "float"){
       val = PyFloat_AsDouble(ret);
       //printf("val returned: %f\n",val);
    }
    else if (retType == "int"){
       val = (double)PyInt_AsLong(ret);
       //printf("val returned: %f\n",val);
    }

     //make a new performance result to hold the new value
    perfResult * pr = new perfResult(); 
    pr->setIndex(prIndex++);
    pr->setValue(val);
    //the parent result ids are the ids of the results that were combined
    pr->setParentResultIds(resIds);
    //add this result to the master list of results
    masterCPRlist.append(pr);

    //make a new tab to hold this result
    CombPerfResWidget * combPerfResWidget = new CombPerfResWidget(this,opName, pr,metrics,d->size());
    char temp[100];
    sprintf(temp,"Result %d",resultNum);
    QString resultName = temp;
    combPRtabWidget->addTab(combPerfResWidget, resultName);
    //connect up the signals for saving, adding to sheets, removing 
    QObject::connect(combPerfResWidget, SIGNAL(closeMe(QWidget*)),this, SLOT(removeResult(QWidget*)));
    QObject::connect(combPerfResWidget, SIGNAL(saveMe(perfResult*,Q3ValueList<int>)),this, SLOT(saveResult(perfResult*,Q3ValueList<int>)));
    QObject::connect(combPerfResWidget, SIGNAL(addMeToExistingSheet(perfResult*)),this, SLOT(addResultToExistingSheet(perfResult*)));
    QObject::connect(combPerfResWidget, SIGNAL(addMeToNewSheet(perfResult*)),this, SLOT(addResultToNewSheet(perfResult*)));
    combPerfResWidget->show();
    combPRtabWidget->showPage(combPerfResWidget);
    ++resultNum;
}

int CombinePerfResesDialog::getTabIndex(QWidget * prTab){
    return combPRtabWidget->indexOf(prTab);
}

void CombinePerfResesDialog::removeResult(QWidget * page){
    //remove the result tab from the combined results dialog
    //fprintf(stderr,"removing result: \n");
    page->close();
    combPRtabWidget->removePage(page);
    if (combPRtabWidget->count() == 0){
       this->hide();
       resultNum = 1;
    }
}

void CombinePerfResesDialog::saveResult(perfResult* pr,Q3ValueList<int> resIds, bool fromDataSheet){
    //save a performance result, pr
    //if it's from the combined results widget, we'll have a list of parent_ids, resIds
    //if it's from a data sheet, we need to look up the resIds
    
    //fprintf(stderr,"saving result\n");
    if (fromDataSheet){  //need to look up the perf result data
	Q3ValueList<perfResult*>::iterator it;
	bool found = false;
	for (it=masterCPRlist.begin(); it != masterCPRlist.end(); ++it){
           if((*it)->getResultId() != -1){
             if (pr->getResultId() == (*it)->getResultId()){
                pr = (*it);
		resIds = pr->getParentResultIds();
	//	fprintf(stderr,"found my pr, resId:%d, hereresid:%d", (*it)->getResultId(), pr->getResultId());
		found = true;
		break;
	     }
	   }
	}
	if (!found){
	    QMessageBox::information(this, "Unknown error", "Couldn't find the result id of the result you want to save. The result will not be saved to the database.");
	    return;
	}
    }
    ContextList contexts = getContextsFromResultIds(resIds);
    Context combinedContext = getCombinedContext(contexts);
    pr->setContext(combinedContext);
    bool saved = saveResultToDB(pr);
    if(!saved){
       QMessageBox::information(this,"Performance Result Save Error", "The performance result was not saved. Please try again.");
    }
    else{
       pr->setSaved();
       //TODO add support for multiple sheets.
       Q3ValueList<int> sheets = pr->getSheets();
           dataSource->resultSaved(0,pr);
       Q3ValueList<int>::iterator it;
       for (it = sheets.begin(); it != sheets.end(); ++it){
	   //fprintf(stderr, "notifying sheets\n");
           dataSource->resultSaved((*it),pr);
       }
       emit(saveSuccess(pr));
    }
}

void CombinePerfResesDialog::dataSheetReloading(int sheet){
    //a data sheet is reloading, wiping out what is on it
    //so we tell the results that think they are on this sheet
    //that they are no longer on it
    Q3ValueList<perfResult*>::iterator it;
    for (it=masterCPRlist.begin(); it != masterCPRlist.end(); ++it){
       if((*it)->isOnSheet(sheet)){
	   (*it)->removeFromSheet(sheet);
       }
    }

}

void CombinePerfResesDialog::addResultToExistingSheet(perfResult * pr){
    //add a result to a datasheet
    //fprintf(stderr,"adding result to existing sheet\n");
    //TODO add support for more sheets. for now there is only one sheet, sheet 0
    bool check = pr->isOnSheet(0); 
    if (check){
       QMessageBox::information(this,"Performance Result Add Error", "The performance result was not added to the sheet because it is already on the specified sheet. Please try a different sheet or a different result.");
       return;
    }
    check = dataSource->addCombinedResultToDataSheet(pr);

    if (check){
	//fprintf(stderr,"adding to sheet \n");
	pr->addToSheet(0);
    }
    return;
}

void CombinePerfResesDialog::clearResultFromSheet(perfResult * pr, int sheet){
    //fprintf(stderr, "clearing result from sheet\n");
    Q3ValueList<perfResult*>::iterator it;
    bool found = false;
    for (it=masterCPRlist.begin(); it != masterCPRlist.end(); ++it){
       if((*it)->getResultId() != -1){
         if (pr->getResultId() == (*it)->getResultId()){
            pr = (*it);
            found = true;
            break;
         }
       }
    }
    if (!found){
        QMessageBox::information(this, "Unknown error", "Couldn't find the result id of the result you want to clear. ");
        return;
    }  
    pr->removeFromSheet(sheet);
    if(pr->isOnSheet(sheet))
	fprintf(stderr, "hmm, removal didn't work\n");
    bool check = dataSource->removeResultFromSheet(pr,sheet);
    if(!check){
        QMessageBox::information(this, "Unknown error", "Couldn't not clear the item");
    }
}

void CombinePerfResesDialog::addResultToNewSheet(perfResult * pr){
    fprintf(stderr,"add result to new sheet not yet implemented\n");
}

bool CombinePerfResesDialog::saveResultToDB(perfResult * pr){
    return dataSource->savePerformanceResult(pr,true);
}

QStringList CombinePerfResesDialog::getAllMetricNamesFromDB(){
    return dataSource->getAllMetricNames();
}

QStringList CombinePerfResesDialog::getAllLabelNamesFromDB(){
    return dataSource->getAllLabelNames();
}

QStringList CombinePerfResesDialog::getAllUnitsNamesFromDB(){
    return dataSource->getAllUnitsNames();
}

ContextList CombinePerfResesDialog::getContextsFromResultIds(Q3ValueList<int> resIds){
    return dataSource->getContextsFromResultIds(resIds);
}

Context CombinePerfResesDialog::getCombinedContext(ContextList cl){
    return dataSource->createCombinedContext(cl);
}

QStringList CombinePerfResesDialog::getAllMetricNames(){
    return metricNames;
}

QStringList CombinePerfResesDialog::getAllLabelNames(){
    return labelNames;
}

QStringList CombinePerfResesDialog::getAllUnitsNames(){
    return unitsNames;
}

CombinePerfResesDialog::~CombinePerfResesDialog(){
   //TODO: need to delete operators
}


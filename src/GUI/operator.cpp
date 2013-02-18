#include "operator.h"

Operator::Operator(){

}

Operator::Operator(QString newName, QString retType, ArgumentList args,void * pyobj ){
   name = newName;
   returnType = retType;
   argList = args;
   pyOpObject = pyobj;
}

QString Operator::getName(){
    return name;
}

QString Operator::getReturnType(){
    return returnType;
}

ArgumentList Operator::getArgumentList(){
    return argList;
}

void * Operator::getPyOpObject(){
    return pyOpObject;
}

Operator::~Operator(){

}

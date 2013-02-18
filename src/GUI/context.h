
#ifndef CONTEXT_H
#define CONTEXT_H

#include <qstring.h>
#include <qstringlist.h>
#include <q3valuelist.h>

class resource{
    public:
	resource(QString Name, QString Type): name(Name),type(Type) {};
	~resource(){};
	QString getName(){return name;};
	QString getType(){return type;};
    private:
	QString name;
	QString type;
};


class context{
   public:
       context();
       ~context();
       void addResource(resource res) {resources.append(resource)};
       
       Q3ValueList<resource> getResources() {return resources};
       QString getType() {return type};

   private:
       Q3ValueList<resource> resources;
       QString type;
};


typedef Q3ValueList<context> ContextList;

#endif 

// testdataaccess.cpp
//
// Unit tests for the DataAccess class.
// To build:
// qmake test.pro
// To run:
// ./perftrack

#include <Q3ListView>
#include <Q3SqlSelectCursor>
#include <QString>
#include <QtTest/QtTest>
#include "data_access.h"
#include "resource_type_and_name.h"
#include "selection_list_item.h"

// A class for receiving signals
class SignalReceiver: public QObject
{
	Q_OBJECT
	
	public:
		SignalReceiver();
		bool isReceived() { return received; }
		
	public slots:
		void receive () { received = true; };
	
	private:
		bool received;
};

SignalReceiver::SignalReceiver() {
	received = false;
}

class TestDataAccess: public QObject
{
    Q_OBJECT
    private:
        // Create an instance of DataAccess
        DataAccess * da;
       
    private slots:
        // initTestCase is called before any test cases are ran
		void cleanupTestCase ();
        void initTestCase ();
		void testAddAncestorsByAttribute ();
		void testAddAncestorsByName ();
		void testAddCombinedResultToDataSheet ();
		void testAddDescendantsByAttribute ();
		void testAddDescendantsByName ();
		void testAddResourcesByAttribute () ;
		void testCompareExecutions ();
		void testComparePerformanceResults ();
		void testCreateContext ();
		void testDeleteAllResources ();
		void testDeleteAncestorsByAttribute ();
		void testDeleteAncestorsByName ();
		void testDeleteDescendantsByAttribute ();
		void testDeleteDescendantsByName ();
		void testDeleteResourcesByAttribute ();
		void testDeleteResourcesByName ();
		void testFindAttributesById ();
		void testFindAttributesByName ();
		void testFindAttributesByResourceName ();
		void testFindAttributesByType ();
		void testFindContextByName ();
		void testFindExecutionResourcesById ();
		void testFindExecutionResourcesByName ();
		void testFindResourceByName ();
		void testFindResourceIdsByType ();
		void testFindResourcesByParent1 ();
		void testFindResourcesByParent2 ();
		void testFindResourcesByType ();
		void testGetAllLabelNames ();
		void testGetAllMetricNames ();
		void testGetAllUnitsNames ();
		void testGetAncestorIds ();
		void testGetContextFromResultId ();
		void testGetDescendantIds ();
		void testGetFocusFrameworkId ();
		void testGetResourceTypes ();
		void testGetResultAttributes ();
		void testGetResultCount ();
		void testGetResultCountLabels ();
		void testGetResultCountMetrics ();
		void testGetResultCountSingle ();
		void testGetResultLabels ();
		void testGetResultResources ();
		void testGetResults ();
		void testGetResultsForCombining ();
		void testInsertResource ();
		void testRemoveResultFromSheet ();
		void testResultSaved ();
		void testSavePerformanceResult ();
};

void TestDataAccess::testAddAncestorsByAttribute(){
	QString type = "grid|machine|node";
	QString attr = "NodeName";
	QString value = "jaccn002";
	QCOMPARE(da->addAncestorsByAttribute (type, attr , value), 54);
}

void TestDataAccess::testAddAncestorsByName(){
	QString type = "execution|process";
	QString name = "Process-0";
	QCOMPARE(da->addAncestorsByName (type, name), 54);
	
}

void TestDataAccess::testAddCombinedResultToDataSheet () {
	perfResult * pr = new perfResult();
	QCOMPARE(da->addCombinedResultToDataSheet(pr), true);
}

void TestDataAccess::testAddDescendantsByAttribute() {
	// None of the resources in the resource_has_ancestor table are in the
	// resource_attribute table.  So, with this database there will be 0
	// descendants added;
	// TODO: add descendants to database
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	QCOMPARE(da->addDescendantsByAttribute (type, attr , value), 0);
}

void TestDataAccess::testAddDescendantsByName () {
	// None of the resources in the resource_has_ancestor table are in the
	// resource_attribute table.  So, with this database there will be 0
	// descendants added;
	// TODO: add descendants to database
	QString type = "execution|process";
	QString name = "Process-0";
	QCOMPARE(da->addDescendantsByName (type, name), 0);
}

void TestDataAccess::testAddResourcesByAttribute () {
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	QCOMPARE(da->addResourcesByAttribute(type, attr, value), 54);
}

void TestDataAccess::testCompareExecutions () {
	QStringList eids;
	eids << "313";
	
	QStringList executions;
	executions << "build|module" << "environment|module" << "execution|process";
	executions << "execution|process|thread" << "fileSystem" << "fileSystem|device";
	executions << "metric" << "operatingSystem" << "time|interval";
	
	QStringList actual = da->compareExecutions(eids);
	
	executions.sort();
	actual.sort();
	QCOMPARE(actual, executions);
}

void TestDataAccess::testComparePerformanceResults () {

	// This function uses a query that queries for data in a
	// temporary function.  Since we are unable to add data
	// to the temporary table, for this unit test, we are
	// just testing that the DBMS accepts the syntax.
	QCOMPARE(da->comparePerformanceResults().empty(), true);		
}

void TestDataAccess::testCreateContext () {
	// Create resources
	ResourceTypeAndName r1 = QPair<QString,QString> ("resource1", "SingleMachineJacquard|Jacquard|jaccn001");
	ResourceTypeAndName r2 = QPair<QString,QString> ("resource2", "SingleMachineJacquard|Jacquard|jaccn002");
	// Create a context
	Context c;
	// Add resources
	c << r1 << r2;

	QCOMPARE(da->createContext(c), 23);
}


void TestDataAccess::testDeleteAllResources () {
	// There is no way to test if this unit test
	// passes because deleteAllResources() returns void
	// and doesn't emit anything.  You will need
	// to look for warning messages in the output.
	da->deleteAllResources();
}

void TestDataAccess::testDeleteAncestorsByAttribute () {
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	da->deleteResourcesByAttribute(type, attr, value);
}

void TestDataAccess::testDeleteAncestorsByName () {
	QString type = "execution|process";
	QString name = "Process-0";
	da->deleteAncestorsByName (type, name);
}

void TestDataAccess::testDeleteDescendantsByAttribute () {
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	da->deleteDescendantsByAttribute (type, attr , value);
}

void TestDataAccess::testDeleteDescendantsByName () {
	QString type = "execution|process";
	QString name = "Process-0";
	da->deleteDescendantsByName (type, name);
}

void TestDataAccess::testDeleteResourcesByAttribute () {
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	da->deleteResourcesByAttribute(type, attr, value);
}

void TestDataAccess::testDeleteResourcesByName () {
	QString type = "execution|process";
	QString name = "Process-0";
	da->deleteResourcesByName (type, name);
}

void TestDataAccess::testFindAttributesById () {
	QString id = "3";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findAttributesById(id, sli);
	delete sli;
}

void TestDataAccess::testFindAttributesByName () {
	QString attribute = "Vendor";
	QString filter = "value = 'AuthenticAMD'";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findAttributesByName(attribute, filter, sli);
	delete sli;
}

void TestDataAccess::testFindAttributesByResourceName () {
	QString name = "jaccn001";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findAttributesByResourceName(name, sli);
	delete sli;
}

void TestDataAccess::testFindAttributesByType () {
	QString resourceType = "grid|machine|node";
	QString filter = "parent_id= 2";
	da->findAttributesByType(resourceType, filter, (void *)*filter);
}

void TestDataAccess::testFindContextByName () {
	// Create resources
	ResourceTypeAndName r1 = QPair<QString,QString> ("resource1", "SingleMachineJacquard|Jacquard|jaccn001");
	ResourceTypeAndName r2 = QPair<QString,QString> ("resource2", "SingleMachineJacquard|Jacquard|jaccn002");
	// Create a context
	Context c;
	// Add resources
	c << r1 << r2;
	da->findContextByName(c);
}

void TestDataAccess::testFindExecutionResourcesById () {
	QString id = "313";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findExecutionResourcesById(id, sli);
	delete sli;
}

void TestDataAccess::testFindExecutionResourcesByName () {
	QString name = "SingleMachineJacquard|Jacquard";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findExecutionResourcesByName(name, sli);
	delete sli;
}

void TestDataAccess::testFindResourceByName () {
	QString resName = "SingleMachineJacquard|Jacquard";
	da->findResourceByName(resName);
}

void TestDataAccess::testFindResourceIdsByType () {
	QString resourceType = "grid|machine|node";
	QString filter = "parent_id= 2";
	da->findResourcesByType(resourceType, filter, (void *)*filter);
}

void TestDataAccess::testFindResourcesByParent1 () {
	QString idList = "2,3";
	QString filter = "type = 'grid|machine|node'";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findResourcesByParent(idList, filter, sli);
	delete sli;
}

void TestDataAccess::testFindResourcesByParent2 () {
	QString parentType = "grid|machine";
	QString baseName = "Jacquard";
	QString filter = "rip.id < 100";
	Q3ListView *lv = new Q3ListView;
	QString str = "string";
	bool bl = true;
	SelectionListItem *sli = new SelectionListItem(lv, str, str, str, str, bl, bl);
	da->findResourcesByParent(parentType, baseName, filter, sli);
	delete sli;
}

void TestDataAccess::testFindResourcesByType () {
	QString resourceType = "grid|machine|node";
	QString filter = "parent_id= 2";
	da->findResourcesByType(resourceType, filter, (void *)*filter);
}

void TestDataAccess::testGetAllLabelNames () {
	da->getAllLabelNames();
}

void TestDataAccess::testGetAllMetricNames () {
	da->getAllMetricNames();
}

void TestDataAccess::testGetAllUnitsNames () {
	da->getAllUnitsNames();
}

void TestDataAccess::testGetAncestorIds () {
	QString resIds = "334, 359";
	da->getAncestorIds(resIds);
}

void TestDataAccess::testGetContextFromResultId () {
	da->getContextFromResultId(10);
}

void TestDataAccess::testGetDescendantIds () {
	QString resIds = "1, 396";
	da->getDescendantIds(resIds);
}

void TestDataAccess::testGetFocusFrameworkId () {
	QString type = "grid|machine";
	da->getFocusFrameworkId(type);
}

void TestDataAccess::testGetResourceTypes () {
	da->getResourceTypes();
}

void TestDataAccess::testGetResultAttributes () {
	SignalReceiver sr;
	connect(da, SIGNAL(resultDetailsReady(QString, Q3SqlCursor)), &sr, SLOT(receive ()));
	da->getResultAttributes("Architecture");
	QCOMPARE(sr.isReceived(), true);
}

void TestDataAccess::testGetResultCount () {
	// populate the temp table first
	QString type = "submission";
	QString attr = "machinePartition";
	QString value = "batch";
	da->addResourcesByAttribute(type, attr, value);
	// test getResultCount();	
	da->getResultCount(1);
}

void TestDataAccess::testGetResultCountLabels () {
	QStringList labels;
	labels << "su3_rmd-182-ppn1-n16" << "su3_rmd-194-ppn2-n16";
	da->getResultCountLabels (labels);
}

void TestDataAccess::testGetResultCountMetrics () {
	QString tableName = "resource_item";
	QStringList labels;
	labels << "su3_rmd-182-ppn1-n16" << "su3_rmd-194-ppn2-n16";
	da->getResultCountMetrics(tableName, labels);
}

void TestDataAccess::testGetResultCountSingle () {
	QString table = "resource_item";
	da->getResultCountSingle(table);
}

void TestDataAccess::testGetResultLabels () {
	da->getResultLabels();
}

void TestDataAccess::testGetResultResources () {
	SignalReceiver sr;
	connect(da, SIGNAL(resultDetailsReady(QString, Q3SqlCursor)), &sr, SLOT(receive ()));
	da->getResultResources("grid|machine|node");
	QCOMPARE(sr.isReceived(), true);
}

void TestDataAccess::testGetResults () {
	QString str = "type = 'grid|machine|node'";
	QStringList labels;
	labels << "su3_rmd-182-ppn1-n16" << "su3_rmd-194-ppn2-n16";
	da->getResults(1, str, str, labels);
}

void TestDataAccess::testGetResultsForCombining () {
	QString metricIds = "";
	QStringList labels;
	labels << "su3_rmd-182-ppn1-n16" << "su3_rmd-194-ppn2-n16";
	da->getResultsForCombining(1, metricIds, labels);
}

void TestDataAccess::testInsertResource () {
	QString resName = "a-resource";
	QString resType = "application";
	da->insertResource(resName, resType);
}

void TestDataAccess::testRemoveResultFromSheet () {
	perfResult * pr = new perfResult();
	QCOMPARE(da->addCombinedResultToDataSheet(pr), true);
	da->removeResultFromSheet(pr, 1);
	delete pr;
}

void TestDataAccess::testResultSaved () {
	perfResult * pr = new perfResult();
	QCOMPARE(da->addCombinedResultToDataSheet(pr), true);
	da->resultSaved(1, pr);
	delete pr;
}

void TestDataAccess::testSavePerformanceResult () {
	perfResult * pr = new perfResult();
	QCOMPARE(da->addCombinedResultToDataSheet(pr), true);
	da->savePerformanceResult(pr, true);
	da->savePerformanceResult(pr, false);
	delete pr;
}

void TestDataAccess::initTestCase ()
{
	da = new DataAccess();
    if( !da->setupDBConnection() ) {
        QFAIL ("Didn't get database info");
    }
}

void TestDataAccess::cleanupTestCase () {
	delete da;
}

QTEST_MAIN(TestDataAccess)
#include "testdataaccess.moc"
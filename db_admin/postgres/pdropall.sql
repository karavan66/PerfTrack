DROP TABLE performance_result_has_focus;
DROP TABLE combined_perf_result_members;
DROP TABLE performance_result;
DROP SEQUENCE seq_performance_result;
DROP TABLE focus_has_resource;
DROP TABLE focus_has_resource_name;
DROP TABLE focus;
DROP SEQUENCE seq_focus;
DROP TABLE resource_constraint;
DROP TABLE resource_attribute;
DROP SEQUENCE seq_resource_item;
DROP SEQUENCE seq_focus_framework;
DROP SEQUENCE seq_resource_name;
DROP SEQUENCE seq_build_name;
DROP TABLE execution_has_resource;
DROP TABLE application_has_execution;
DROP TABLE resource_has_descendant;
DROP TABLE resource_has_ancestor;
DROP TABLE resource_item;
DROP TABLE focus_framework;
DROP INDEX resItemLookup;
DROP INDEX focusNameSearch;
DROP INDEX resourceFindEid;

-- Added 'value_in_range' and 'complex_perf_result' tables

DROP TRIGGER IF EXISTS value_chk ON value_in_range;
DROP TABLE value_in_range;
DROP FUNCTION update_perf_result();
DROP TABLE complex_perf_result;
DROP TYPE complex_result;
DROP SEQUENCE seq_complex_perfresult;

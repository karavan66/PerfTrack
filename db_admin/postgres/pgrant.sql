
-- GRANT privileges to group on table objects
--GRANT ALL PRIVILEGES
--ON focus_framework, resource_item, resource_attribute, resource_constraint,
--   focus, focus_has_resource, performance_result, performance_result_has_focus,
--   application_has_execution, execution_has_resource, resource_has_ancestor,
--   resource_has_descendant
--TO GROUP pperftrac;

-- GRANT privileges to group on other objects
--GRANT ALL PRIVILEGES
--ON seq_focus_framework, seq_resource_item, seq_focus, seq_performance_result,
--   seq_resource_name, seq_build_name
--TO GROUP pperftrac;

-- GRANT all privileges to user perftrac on table and other objects
GRANT ALL PRIVILEGES
ON focus_framework, resource_item, resource_attribute, resource_constraint,
   focus, focus_has_resource, focus_has_resource_name, performance_result, 
   performance_result_has_focus, application_has_execution, 
   execution_has_resource, resource_has_ancestor, resource_has_descendant, 
   seq_focus_framework, seq_resource_item, seq_focus, seq_performance_result, 
   seq_resource_name, seq_build_name
TO perftrac;

-- GRANT privileges to user on other objects
--GRANT ALL PRIVILEGES
--ON seq_focus_framework, seq_resource_item, seq_focus, seq_performance_result,
--   seq_resource_name, seq_build_name
--TO perftrac;


-- GRANT limited privileges to user on table and seq objects
GRANT SELECT
ON focus_framework, resource_item, resource_attribute, resource_constraint,
   focus, focus_has_resource, focus_has_resource_name, performance_result,
   performance_result_has_focus, application_has_execution, 
   execution_has_resource, resource_has_ancestor, resource_has_descendant, 
   seq_focus_framework, seq_resource_item, seq_focus, seq_performance_result, 
   seq_resource_name, seq_build_name
TO GROUP pperftrac;



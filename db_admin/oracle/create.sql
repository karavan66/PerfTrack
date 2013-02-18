-- PerfTrack Version 1.0     September 1, 2005
-- See PTLICENSE for distribution information. 

CREATE SEQUENCE seq_focus_framework START WITH 1 INCREMENT BY 1;

CREATE TABLE focus_framework (
  id INTEGER NOT NULL,
  type_string VARCHAR2(4000) NULL,
  parent_id CONSTRAINT fk_focus_framework_id1
    REFERENCES focus_framework(id) ON DELETE CASCADE,
  PRIMARY KEY(id)
);

CREATE SEQUENCE seq_resource_item START WITH 1 INCREMENT BY 1;

CREATE TABLE resource_item (
  id INTEGER NOT NULL,
  name VARCHAR2(3000) NOT NULL,
  type VARCHAR2(3000) NOT NULL,
  ff SMALLINT, 
  parent_id CONSTRAINT fk_resource_id1
    REFERENCES resource_item(id) ON DELETE CASCADE,
  focus_framework_id CONSTRAINT fk_focus_framework_id2
    REFERENCES focus_framework(id) ON DELETE CASCADE,
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX resItemLookup ON resource_item (id, name, type);

CREATE TABLE resource_attribute (
  resource_id CONSTRAINT fk_resource_id2
    REFERENCES resource_item(id) ON DELETE CASCADE,
  name VARCHAR2(4000) NOT NULL,
  value VARCHAR2(4000) NOT NULL,
  attr_type VARCHAR2(4000),
  PRIMARY KEY(resource_id, name)
);

CREATE TABLE resource_constraint (
  from_resource CONSTRAINT fk_resource_id3
    REFERENCES resource_item(id) ON DELETE CASCADE,
  to_resource CONSTRAINT fk_resource_id4
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(from_resource, to_resource)
);

CREATE SEQUENCE seq_focus START WITH 1 INCREMENT BY 1;

CREATE TABLE focus (
  id INTEGER NOT NULL,
  focusname VARCHAR2(4000) NOT NULL, 
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX focusNameSearch ON focus (focusname, id);

CREATE TABLE focus_has_resource (
  focus_id CONSTRAINT fk_focus_id1
    REFERENCES focus(id) ON DELETE CASCADE,
  resource_id CONSTRAINT fk_resource_id6
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(focus_id, resource_id)
);
 
CREATE TABLE focus_has_resource_name (
  focus_id CONSTRAINT fk_focus_id3
    REFERENCES focus(id) ON DELETE CASCADE,
  resource_name VARCHAR2(4000) NOT NULL,
  PRIMARY KEY(focus_id, resource_name)
);


CREATE SEQUENCE seq_performance_result START WITH 1 INCREMENT BY 1;

CREATE TABLE performance_result (
  id INTEGER NOT NULL,
  metric_id CONSTRAINT fk_resource_id8
    REFERENCES resource_item(id) ON DELETE CASCADE,
  value FLOAT NOT NULL,
  units VARCHAR2(4000) NULL,
  start_time VARCHAR2(4000) NULL,
  end_time VARCHAR2(4000) NULL,
  focus_id INTEGER 
	REFERENCES focus(id),
  label VARCHAR2(4000),
  combined SMALLINT,
  PRIMARY KEY(id)
);

CREATE TABLE performance_result_has_focus (
  performance_result_id CONSTRAINT fk_performance_result_id1
    REFERENCES performance_result(id) ON DELETE CASCADE,
  focus_id CONSTRAINT fk_focus_id2
    REFERENCES focus(id) ON DELETE CASCADE,
  focus_type VARCHAR2(4000) DEFAULT 'primary',
    CONSTRAINT check_focus_type CHECK
      (focus_type IN ('primary', 'parent', 'child', 'sender', 'receiver')),
  PRIMARY KEY(performance_result_id, focus_id)
);

CREATE TABLE combined_perf_result_members(
  -- the parent combined_performance_result
  c_pr_id INTEGER CONSTRAINT fk_performance_result_id2
    REFERENCES performance_result(id) ON DELETE CASCADE,
  -- the child perf result
  pr_id INTEGER CONSTRAINT fk_performance_result_id3
    REFERENCES performance_result(id) ON DELETE CASCADE
);

CREATE SEQUENCE seq_resource_name START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE seq_build_name START WITH 1 INCREMENT BY 1 NOCACHE;

CREATE TABLE application_has_execution (
	aid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	eid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	PRIMARY KEY (eid,aid)
);

CREATE TABLE execution_has_resource (
	eid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	rid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	has_type VARCHAR2(4000),
	PRIMARY KEY (rid,eid)
);

CREATE INDEX resourceFindEid ON execution_has_resource(rid, eid);

CREATE TABLE resource_has_ancestor(
	rid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	aid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	PRIMARY KEY (rid,aid)
);

CREATE TABLE resource_has_descendant(
	rid INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	did INTEGER NOT NULL
	   REFERENCES resource_item(id) ON DELETE CASCADE,
	PRIMARY KEY (rid,did)
);

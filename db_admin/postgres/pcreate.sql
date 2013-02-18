CREATE SEQUENCE seq_focus_framework INCREMENT BY 1 START WITH 1;

CREATE TABLE focus_framework (
  id INTEGER NOT NULL,
  type_string VARCHAR(4000),
  parent_id  INTEGER CONSTRAINT fk_focus_framework_id1
     REFERENCES focus_framework(id) ON DELETE CASCADE,
  PRIMARY KEY(id) 
);

CREATE SEQUENCE seq_resource_item INCREMENT BY 1 START WITH 1;

CREATE TABLE resource_item (
  id INTEGER NOT NULL,
  name VARCHAR(4000) NOT NULL,
  type VARCHAR(4000) NOT NULL,
  ff SMALLINT, 
  parent_id INTEGER CONSTRAINT fk_resource_id1
     REFERENCES resource_item(id) ON DELETE CASCADE,
  focus_framework_id INTEGER CONSTRAINT fk_focus_framework_id2
     REFERENCES focus_framework(id) ON DELETE CASCADE,
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX resItemLookup ON resource_item (id, name, type);

CREATE TABLE resource_attribute (
  resource_id INTEGER CONSTRAINT fk_resource_id2
     REFERENCES resource_item(id) ON DELETE CASCADE,
  name VARCHAR(4000) NOT NULL,
  value VARCHAR(4000) NOT NULL,
  attr_type VARCHAR(4000),
  PRIMARY KEY(resource_id, name)
);

CREATE TABLE resource_constraint (
  from_resource INTEGER CONSTRAINT fk_resource_id3
     REFERENCES resource_item(id) ON DELETE CASCADE,
  to_resource INTEGER CONSTRAINT fk_resource_id4
     REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(from_resource, to_resource)
);

CREATE SEQUENCE seq_focus INCREMENT BY 1 START WITH 1;

CREATE TABLE focus (
  id INTEGER NOT NULL,
  focusname VARCHAR(4000) NOT NULL, 
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX focusNameSearch ON focus (focusname, id);

CREATE TABLE focus_has_resource (
  focus_id INTEGER CONSTRAINT fk_focus_id1
     REFERENCES focus(id) ON DELETE CASCADE,
  resource_id INTEGER CONSTRAINT fk_resource_id6
     REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(focus_id, resource_id)
);

CREATE TABLE focus_has_resource_name (
  focus_id INTEGER CONSTRAINT fk_focus_id1
     REFERENCES focus(id) ON DELETE CASCADE,
  resource_name VARCHAR(4000) NOT NULL,
  PRIMARY KEY (focus_id, resource_name)
);

CREATE SEQUENCE seq_performance_result INCREMENT BY 1 START WITH 1;

CREATE TABLE performance_result (
  id INTEGER NOT NULL,
  metric_id INTEGER CONSTRAINT fk_resource_id8
     REFERENCES resource_item(id) ON DELETE CASCADE,
  value FLOAT8 NOT NULL,
  units VARCHAR(4000),
  start_time VARCHAR(4000),
  end_time VARCHAR(4000),
  focus_id INTEGER
     REFERENCES focus(id),
  label VARCHAR(4000),
  combined SMALLINT,
  PRIMARY KEY(id)
);


CREATE TABLE performance_result_has_focus (
  performance_result_id INTEGER CONSTRAINT fk_performance_result_id1
    REFERENCES performance_result(id) ON DELETE CASCADE,
  focus_id INTEGER CONSTRAINT fk_focus_id2
    REFERENCES focus(id) ON DELETE CASCADE,
  focus_type VARCHAR(4000) DEFAULT 'primary',
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

CREATE SEQUENCE seq_resource_name INCREMENT BY 1 START WITH 1;
CREATE SEQUENCE seq_build_name INCREMENT BY 1 START WITH 1;

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
  has_type VARCHAR(4000),
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

CREATE TABLE resource_has_descendant (
  rid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  did INTEGER NOT NULL 
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY (rid,did)
);

--Changes for adding 'Expected value'

ALTER TABLE performance_result
ADD COLUMN chk CHAR;


CREATE TABLE value_in_range ( 
  metric_id INTEGER,
  focus_id INTEGER,
  range_from DOUBLE PRECISION,
  range_to DOUBLE PRECISION,
  PRIMARY KEY (metric_id, focus_id) 
);

CREATE FUNCTION Update_perf_result() RETURNS TRIGGER AS $value_chk$
BEGIN
            UPDATE performance_result p
                set chk = (case
                when (p.value > v.range_from and p.value < v.range_to) then 'E'
                when p.value < v.range_from then 'L'
                when p.value > v.range_to then 'H'
                else 'U' end)
                from  value_in_range v
        where
                p.metric_id=v.metric_id
        and     p.focus_id=v.focus_id;
        RETURN NEW;
END;
$value_chk$ LANGUAGE plpgsql;

CREATE TRIGGER value_chk
After INSERT OR UPDATE ON value_in_range
FOR EACH ROW EXECUTE PROCEDURE update_perf_result();

--Changes for adding 'Complex Result'

CREATE TYPE complex_result AS (
            value       double precision[],
            start_time character varying(4000)[],
            end_time character varying(4000)[]
);

CREATE TABLE complex_perf_result (
        result_id INTEGER PRIMARY KEY,
        result_value complex_result
);

CREATE SEQUENCE seq_complex_perfresult INCREMENT BY 1 START WITH 1;

ALTER TABLE performance_result
ADD COLUMN complex_result_id INTEGER;

ALTER TABLE performance_result
ADD CONSTRAINT fk_result_id FOREIGN KEY (complex_result_id)
REFERENCES complex_perf_result (result_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

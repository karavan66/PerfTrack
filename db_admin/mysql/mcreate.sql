-- mcreate.sql
-- Creates tables in a MySQL database for PerfTrack.
-- Derived from pcreate.sql.
--
-- Michael Smith
-- 2008-7-10

-- Requires the InnoDb engine for MySQL.  I believe this is included.

-- MySQL as of version 5.0 does not support sequences.  Opted to not use
-- AUTO_INCREMENT because:
-- 1) From the MySQL documentation: "LAST_INSERT_ID() returns the first
--    automatically generated value that was set for an
--    AUTO_INCREMENT column by the most recently executed  INSERT statement to
--    affect such a column."  This means that the value returned by LAST_INSERT_ID()
--    is dependent upon the last INSERT performed.  We may not know what the last
--    insert was.
-- 2) If INSERT inserts multiple rows AUTO_INCREMENT will only increment the value by 1.
--
-- So, instead of using AUTO_INCREMENT we'll create a table to store sequences

CREATE TABLE sequence (
  name CHAR(50) PRIMARY KEY,
  prev_value INT UNSIGNED NOT NULL
);

-- Example usage:
-- UPDATE sequence SET prev_value = @value := prev_value + 1
--   where name = "seq_focus_framework";
-- SELECT @value;


INSERT INTO sequence (name, prev_value) VALUES ("seq_focus_framework", 0);

CREATE TABLE focus_framework (
  id INTEGER PRIMARY KEY,
  type_string VARCHAR(4000),
  parent_id INTEGER,
  CONSTRAINT fk_focus_framework_id1 FOREIGN KEY (parent_id)
    REFERENCES focus_framework(id) ON DELETE CASCADE
) ENGINE = INNODB;

INSERT INTO sequence (name, prev_value) VALUES ("seq_resource_item", 0);

-- The length of name and type were decreased from 4,000 to 767 because
-- MySQL restricts the length of the keys to 767 bytes as used in the
-- resItemLookup index.
CREATE TABLE resource_item (
  id INTEGER PRIMARY KEY,
  name VARCHAR(767) NOT NULL,
  type VARCHAR(767) NOT NULL,
  ff SMALLINT,
  parent_id INTEGER,
  CONSTRAINT fk_resource_id1 FOREIGN KEY (parent_id)
    REFERENCES resource_item(id) ON DELETE CASCADE,
  focus_framework_id INTEGER,
  CONSTRAINT fk_focus_framework_id2 FOREIGN KEY (focus_framework_id)
    REFERENCES focus_framework(id) ON DELETE CASCADE
) ENGINE = INNODB;

CREATE UNIQUE INDEX resItemLookup ON resource_item (id, name, type);

-- Decreased the length of name to 767 because MySQL limits the length of
-- keys to 767 byts.
CREATE TABLE resource_attribute (
  resource_id INTEGER,
  CONSTRAINT fk_resource_id2 FOREIGN KEY (resource_id)
     REFERENCES resource_item(id) ON DELETE CASCADE,
  name VARCHAR(767) NOT NULL,
  value VARCHAR(4000) NOT NULL,
  attr_type VARCHAR(4000),
  PRIMARY KEY(resource_id, name)
) ENGINE = INNODB;

CREATE TABLE resource_constraint (
  from_resource INTEGER,
  CONSTRAINT fk_resource_id3 FOREIGN KEY (from_resource)
     REFERENCES resource_item(id) ON DELETE CASCADE,
  to_resource INTEGER,
  CONSTRAINT fk_resource_id4 FOREIGN KEY (to_resource)
     REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(from_resource, to_resource)
) ENGINE = INNODB;

INSERT INTO sequence (name, prev_value) VALUES ("seq_focus", 0);

-- Decreased the length of name to 767 because MySQL limits the length of
-- keys to 767 byts.
CREATE TABLE focus (
  id INTEGER NOT NULL,
  focusname VARCHAR(767) NOT NULL, 
  PRIMARY KEY(id)
) ENGINE = INNODB;

CREATE UNIQUE INDEX focusNameSearch ON focus (focusname, id);

CREATE TABLE focus_has_resource (
  focus_id INTEGER,
  CONSTRAINT fk_focus_id1 FOREIGN KEY (focus_id)
     REFERENCES focus(id) ON DELETE CASCADE,
  resource_id INTEGER,
  CONSTRAINT fk_resource_id6 FOREIGN KEY (resource_id)
     REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY(focus_id, resource_id)
) ENGINE = INNODB;

-- Decreased the length of name to 767 because MySQL limits the length of
-- keys to 767 byts.  Changed constraint name from fk_focus_id1 to
-- fk_focus_id2 because fk_focus_id1 is a duplicate constraint name.
CREATE TABLE focus_has_resource_name (
  focus_id INTEGER,
  CONSTRAINT fk_focus_id2 FOREIGN KEY (focus_id)
     REFERENCES focus(id) ON DELETE CASCADE,
  resource_name VARCHAR(767) NOT NULL,
  PRIMARY KEY (focus_id, resource_name)
) ENGINE = INNODB;

INSERT INTO sequence (name, prev_value) VALUES ("seq_performance_result", 0);

CREATE TABLE performance_result (
  id INTEGER NOT NULL,
  metric_id INTEGER,
  CONSTRAINT fk_resource_id8 FOREIGN KEY (metric_id)
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
) ENGINE = INNODB;

-- Changed constraint name from fk_focus_id2 to
-- fk_focus_id3 because fk_focus_id2 is a duplicate constraint name.
CREATE TABLE performance_result_has_focus (
  performance_result_id INTEGER,
  CONSTRAINT fk_performance_result_id1 FOREIGN KEY (performance_result_id)
    REFERENCES performance_result(id) ON DELETE CASCADE,
  focus_id INTEGER,
  CONSTRAINT fk_focus_id3 FOREIGN KEY (focus_id)
    REFERENCES focus(id) ON DELETE CASCADE,
  focus_type VARCHAR(4000) DEFAULT 'primary',
  CONSTRAINT check_focus_type CHECK
      (focus_type IN ('primary', 'parent', 'child', 'sender', 'receiver')),
  PRIMARY KEY(performance_result_id, focus_id)
) ENGINE = INNODB;

CREATE TABLE combined_perf_result_members(
  -- the parent combined_performance_result
  c_pr_id INTEGER,
  CONSTRAINT fk_performance_result_id2 FOREIGN KEY (c_pr_id)
    REFERENCES performance_result(id) ON DELETE CASCADE,
  -- the child perf result 
  pr_id INTEGER,
  CONSTRAINT fk_performance_result_id3 FOREIGN KEY (pr_id)
    REFERENCES performance_result(id) ON DELETE CASCADE
) ENGINE = INNODB;

INSERT INTO sequence (name, prev_value) VALUES ("seq_resource_name", 0);
INSERT INTO sequence (name, prev_value) VALUES ("seq_build_name", 0);

CREATE TABLE application_has_execution (
  aid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  eid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY (eid,aid)
) ENGINE = INNODB;

CREATE TABLE execution_has_resource (
  eid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  rid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  has_type VARCHAR(4000),
  PRIMARY KEY (rid,eid)
) ENGINE = INNODB;

CREATE INDEX resourceFindEid ON execution_has_resource(rid, eid);

CREATE TABLE resource_has_ancestor(
  rid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  aid INTEGER NOT NULL 
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY (rid,aid)
) ENGINE = INNODB;

CREATE TABLE resource_has_descendant (
  rid INTEGER NOT NULL
    REFERENCES resource_item(id) ON DELETE CASCADE,
  did INTEGER NOT NULL 
    REFERENCES resource_item(id) ON DELETE CASCADE,
  PRIMARY KEY (rid,did)
) ENGINE = INNODB;

-- SQL script for adding complex_perf_result to a 
-- PerfTrack database created without it.
--
-- 2013-08-15 HH

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

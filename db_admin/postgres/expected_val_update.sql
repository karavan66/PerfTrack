-- SQL Script to update existing PerfTrack database to support expected values
-- Run this script if your database schema was not created with expected
-- value support:
--   chk column in performance_result
--   value_in_range table
--   trigger: value_chk
--   function: update_perf_result

-- Add chk column to performance_result
ALTER TABLE performance_result
   add column chk character varying(4000);

-- Create new table
CREATE TABLE value_in_range
   (metric_id integer,
    focus_id integer,
    range_from double precision,
    range_to double precision,
    PRIMARY KEY (metric_id, focus_id));

-- Create update function and trigger
CREATE FUNCTION update_perf_result() RETURNS TRIGGER AS $value_chk$ 
   BEGIN
      UPDATE performance_result p
      set chk = (case
          when (p.value > v.range_from and p.value < v.range_to) then 'E'
          when p.value < v.range_from then 'L'
          when p.value > v.range_to then 'H'
          else 'U' end)
      from  value_in_range v
      where p.metric_id=v.metric_id
            and p.focus_id=v.focus_id;
      RETURN NEW;
   END;
$value_chk$ LANGUAGE plpgsql;

CREATE TRIGGER value_chk
   After INSERT OR UPDATE ON value_in_range 
   FOR EACH ROW EXECUTE PROCEDURE update_perf_result();

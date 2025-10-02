-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

WITH time_shift AS (
  SELECT 
    MAX(__time) AS max_time
  FROM bids_data_raw
),
shifted_data AS (
  SELECT
    __time + (CURRENT_TIMESTAMP - time_shift.max_time) AS __time,
    * EXCLUDE (__time)
  FROM bids_data_raw, time_shift
)
SELECT * FROM shifted_data
-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

WITH time_shift AS (
  SELECT 
    MAX(__time) AS max_time
  FROM auction_data_raw
),
shifted_data AS (
  SELECT
    __time + (CURRENT_TIMESTAMP - time_shift.max_time) AS __time,
    * EXCLUDE (__time, device_region),
    CASE WHEN device_region ILIKE '%/%' THEN SPLIT(device_region, '/')[2] ELSE 'Unknown' END AS device_state,
    CASE WHEN device_region ILIKE '%/%' THEN SPLIT(device_region, '/')[1] ELSE 'Unknown' END AS device_country
  FROM auction_data_raw, time_shift
)
SELECT * FROM shifted_data
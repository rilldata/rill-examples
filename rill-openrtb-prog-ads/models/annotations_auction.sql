-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true
-- @refresh.cron: 0 0 * * *

WITH base AS (
  SELECT
    date_trunc('minute', now() - interval '1 day') AS t1,
    date_trunc('minute', now() - interval '8 hours') AS t2,
    date_trunc('minute', now() - interval '3 hours') AS t3
)
SELECT
  t1 AS time,
  NULL::TIMESTAMP AS time_end,
  'Release 2.57' AS description
FROM base

UNION ALL

SELECT
  t2 AS time,
  date_trunc('minute', t2 + interval '3 hours') AS time_end,
  'Spike window' AS description
FROM base

UNION ALL

SELECT
  t3 AS time,
  NULL::TIMESTAMP AS time_end,
  'Experimental' AS description
FROM base
ORDER BY time
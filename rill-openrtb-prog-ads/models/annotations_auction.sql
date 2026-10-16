-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true
-- @refresh.cron: 0 0 * * *

WITH base AS (
  SELECT
    date_trunc('minute', now() - interval '1 day') AS t1,
    date_trunc('minute', now() - interval '5 hours') AS t2,
    date_trunc('minute', now() - interval '3 hours') AS t3
)
SELECT
  t1 AS time,
  NULL::TIMESTAMP AS end_time,
  'Daily checkpoint at ' || strftime(t1, '%Y-%m-%d %H:%M:%S') AS description
FROM base

UNION ALL

SELECT
  t2 AS time,
  date_trunc('minute', t2 + interval '2 hours') AS end_time,
  'Auction window from ' || strftime(t2, '%Y-%m-%d %H:%M:%S') || ' to ' || strftime(date_trunc('minute', t2 + interval '2 hours'), '%Y-%m-%d %H:%M:%S') AS description
FROM base

UNION ALL

SELECT
  t3 AS time,
  NULL::TIMESTAMP AS end_time,
  'Recent activity spike at ' || strftime(t3, '%Y-%m-%d %H:%M:%S') AS description
FROM base
ORDER BY time
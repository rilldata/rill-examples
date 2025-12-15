-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
select
  'traffic' as type,
  date_path,
  insightTrafficSourceType as sub_type,
  views,
  estimatedMinutesWatched,
  null as averageViewDuration,
  null as averageViewPercentage,
  null as subscribersGained,
  null as viewerPercentage
from
  "__demographics_traffic"

UNION ALL

select
  'geo' as type,
  date_path,
  country as sub_type,
  views,
  estimatedMinutesWatched,
  averageViewDuration,
  averageViewPercentage,
  subscribersGained,
  null as viewerPercentage
from
  "__demographics_geo"

UNION ALL

select
  'device' as type,
  day as date,
  deviceType as sub_type,
  views,
  null as estimatedMinutesWatche,
  null as averageViewDuration,
  null as averageViewPercentage,
  null as subscribersGained,
  null as viewerPercentage
from
  "__demographics_device"

UNION ALL

select
  'gender' as type,
    date_path,
  gender as sub_type,
  null as views,
  null as estimatedMinutesWatched,
  null as averageViewDuration,
  null as averageViewPercentage,
  null as subscribersGained,
  viewerPercentage

from
  "__demographics_gender"

UNION ALL

select
  'age' as type,
    date_path,
  ageGroup as sub_type,
  null as views,
  null as estimatedMinutesWatched,
  null as averageViewDuration,
  null as averageViewPercentage,
  null as subscribersGained,
  viewerPercentage
from
  "__demographics_age"
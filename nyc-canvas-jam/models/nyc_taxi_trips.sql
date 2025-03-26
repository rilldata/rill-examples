-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models


--@materialize: true  

SELECT 
  t.*,
  upper(p.borough) as borough,
  upper(p.borough) as pickup_borough,
  p.zone_name as pickup_zone_name,
  upper(d.borough) as dropoff_borough,
  d.zone_name as dropoff_zone
FROM
  taxi_trips t
  left join nyc_locations p on t.pickup_location_id = p.zone_id
  left join nyc_locations d on t.dropoff_location_id = d.zone_id
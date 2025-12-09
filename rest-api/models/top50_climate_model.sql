-- Model SQL
-- Reference documentation: https://docs.rilldata.com/build/models

SELECT 
  
  aq.*,
  wave_height,
  wave_direction,
  wave_period,

  wind_wave_height,
  wind_wave_direction,
  wind_wave_period,
  wave_direction_compass,
  sea_state,
  
  temperature_2m,
  relativehumidity_2m
  
  from top50cities_aq aq

left join top50cities_marine marine on (aq.city = marine.city and aq.time = marine.time)
left join top50cities_temps temp on (aq.city = temp.city and aq.time = temp.time)
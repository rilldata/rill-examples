-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

select 
  Date,
  CAST("Global_active_power" as DOUBLE) as Global_active_power,
  CAST("Global_reactive_power" as DOUBLE) as Global_reactive_power,
  CAST("Global_intensity" as DOUBLE) as Global_intensity,

  CAST("Voltage" as DOUBLE) as Voltage,

  CAST("Sub_metering_1" as DOUBLE) as Sub_metering_1,
  CAST("Sub_metering_2" as DOUBLE) as Sub_metering_2,
  CAST("Sub_metering_3" as DOUBLE) as Sub_metering_3,
  
  

  case 
    when Global_active_power < 1 then 'Low'
    when Global_active_power < 3 then 'Medium'
    when Global_active_power < 6 then 'High'
    when Global_active_power >= 6 then 'Very High'
  end as GAP_category,
    case 
    when Global_reactive_power < 0.5 then 'Low'
    when Global_reactive_power < 2 then 'Medium'
    when Global_reactive_power < 3 then 'High'
    when Global_reactive_power >= 5 then 'Very High'
  end as GRP_category
  
  
  from household_power_consumption 
  where "Global_active_power" != '?' and "Global_reactive_power" != '?'
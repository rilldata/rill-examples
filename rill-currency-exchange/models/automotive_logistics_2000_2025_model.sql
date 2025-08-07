-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

select al.*,
  te.exchange_rate,
  te.country,
  te.record_date,
  al.total_value / te.exchange_rate as usd_price
  
  from automotive_logistics_2000_2025 al

left join treasury_exchange_rates_filled te on
  al.origin_country = te.country 
  and
  al.ship_date = te.record_date

-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

SELECT 
    iso_duration,
    CASE iso_duration
        WHEN 'PT' THEN current_date()
        WHEN 'P1D' THEN current_date() + INTERVAL '1 day'
        WHEN 'P1W' THEN current_date() + INTERVAL '1 week'
        WHEN 'P2W' THEN current_date() + INTERVAL '2 weeks'
        WHEN 'P1M' THEN current_date() + INTERVAL '1 month'
        WHEN 'P3M' THEN current_date() + INTERVAL '3 months'
        WHEN 'P1Y' THEN current_date() + INTERVAL '1 year'
    END AS timestamp
FROM (
    SELECT unnest(ARRAY['PT','P1D', 'P1W', 'P2W', 'P1M', 'P3M', 'P1Y']) AS iso_duration
) t

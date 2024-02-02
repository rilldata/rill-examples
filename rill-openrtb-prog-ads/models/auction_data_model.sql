select * EXCEPT (device_region), 
CASE WHEN device_region ILIKE '%/%' THEN splitByChar('/', assumeNotNull(device_region))[2] ELSE 'Unknown' END AS device_state, 
CASE WHEN device_region ILIKE '%/%' THEN splitByChar('/', assumeNotNull(device_region))[1] ELSE 'Unknown' END AS device_country
from {{ ref "auction_data_raw" }}

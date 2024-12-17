-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

select * 
from mobile_events
ORDER BY event_time DESC
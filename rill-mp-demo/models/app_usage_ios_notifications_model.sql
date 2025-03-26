-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

SELECT 
    notifications.*,
    used.*,
    pickups.*
FROM 
    app_usage_ios_notifications AS notifications
INNER JOIN 
    app_usage_ios_used AS used
ON 
    notifications.user_id = used.user_id
INNER JOIN 
    app_usage_ios_pickups AS pickups
ON 
    notifications.user_id = pickups.user_id


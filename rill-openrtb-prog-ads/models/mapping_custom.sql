-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'Value0'),
      ('Disney', 'Value2'),
      ('LG USA', 'Value2'),
      ('Pluto', 'Value2')
    ) AS t(PubName, custom_attribute)

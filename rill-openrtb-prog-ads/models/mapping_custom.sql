-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'Value1'),
      ('LG USA', 'Value2'),
      ('Pluto', 'Value3')
    ) AS t(PubName, custom_attribute)

-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('LG USA', 'Value1'),
      ('Disney', 'Value2'),
      ('Pluto', 'Value3')
    ) AS t(PubName, custom_attribute)

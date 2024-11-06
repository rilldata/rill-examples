-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'x'),
      ('Disney', 'yes'),
      ('LG USA', 'z'),
      ('Pluto', 'a')
    ) AS t(PubName, var)

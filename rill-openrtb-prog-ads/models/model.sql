-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'test@domain.com'),
      ('Disney', 'royendo@rilldata.com')

    ) AS t(PubName, email)

-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'domain.com'),
      ('Disney', 'rilldata.com')

    ) AS t(PubName, domain)

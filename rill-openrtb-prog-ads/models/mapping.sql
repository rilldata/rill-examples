-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

    SELECT * FROM (VALUES 
      ('Disney', 'domain.com', ''),
      ('Disney', 'rilldata.com', ''),
      ('LG USA', 'rilldata.com', 'roy.endo@rilldata.com'),
      ('Pluto', 'rilldata.com', '')
    ) AS t(PubName, domain, email)

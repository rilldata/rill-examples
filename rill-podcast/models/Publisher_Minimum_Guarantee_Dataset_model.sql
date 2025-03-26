-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

select stream.*, min.min_guarantee_usd from  
  "podcast_data"  stream
left join "Publisher_Minimum_Guarantee_Dataset" min on stream.publisher_id = min.publisher_id
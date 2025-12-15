-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

select 
  metrics.*,
  mapping.Title
  from "__metrics" metrics
left join video_mapping mapping on metrics.video = mapping."Video ID"
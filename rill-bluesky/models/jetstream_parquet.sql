-- @materialize: true
-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models

{{if dev}} 
  SELECT * FROM read_parquet('https://hive.buz.dev/bluesky/jetstream/latest.parquet',
    union_by_name=true)
{{else}}
  SELECT * FROM read_parquet('gs://medriscoll-rill/rill-bluesky-jetstream/year=2024/month=11/day=17/hour=*/*.parquet',
    union_by_name=true)
{{end}}
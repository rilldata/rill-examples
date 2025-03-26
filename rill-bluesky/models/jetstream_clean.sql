-- @materialize: true
-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- language lookup

WITH iso639 AS (
   SELECT map_from_entries(ARRAY_AGG(struct_pack(alpha2, english_name))) AS alpha2english 
   FROM read_csv('https://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt', 
                  delim='|', columns={'alpha3_bibliographic': 'TEXT','alpha3_terminologic': 'TEXT','alpha2': 'VARCHAR','english_name': 'VARCHAR','french_name': 'VARCHAR'
                 }, header=False
   )
   WHERE alpha2 IS NOT null)

FROM jetstream_parquet, iso639

SELECT
  to_timestamp(time_us / 10^6) AS time,
  did,
  CONCAT('https://bsky.app/profile/', did) AS did_uri,
  regexp_replace(json_extract(commit, '$.operation'), '^"(.*)"$', '\1') AS commit_operation,
  regexp_replace(json_extract(commit, '$.record.$type'), '.*\.(.*)"$', '\1') AS record_type,
  regexp_replace(json_extract(commit, '$.record.langs[0]'), '^"(.*)"$', '\1') AS record_lang,
  iso639.alpha2english[record_lang][1] AS record_language,
  regexp_replace(json_extract(commit, '$.rkey'), '^"(.*)"$', '\1') AS record_key,
  CONCAT('https://bsky.app/profile/',did,'/post/',record_key) AS record_uri,
  WHERE commit_operation IN ('create')

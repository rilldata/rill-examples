-- @materialize: true

WITH 

commit_files_long AS (
  SELECT *, UNNEST(files) AS f FROM duckdb_commit_details_source
)

SELECT
  CAST(commit.author.date AS TIMESTAMP) AS date,
  sha AS commit_sha,
  commit.message AS commit_message,
  author.login AS username,
  commit.comment_count,
  f.filename,
  RIGHT(f.filename, POSITION('.' IN REVERSE(f.filename))) AS file_extension,
  CASE WHEN CONTAINS(f.filename, '/')
    THEN SPLIT_PART(f.filename, '/', 1)
    ELSE NULL
  END AS first_directory,
  CASE WHEN CONTAINS(SUBSTRING(f.filename, LENGTH(first_directory) + 2), '/')
    THEN SPLIT_PART(f.filename, '/', 2)
    ELSE NULL
  END AS second_directory,
  CASE 
    WHEN first_directory IS NOT NULL AND second_directory IS NOT NULL
      THEN CONCAT(first_directory, '/', second_directory) 
    WHEN first_directory IS NOT NULL
      THEN first_directory
    WHEN first_directory IS NULL
      THEN NULL
  END AS second_directory_concat,
  f.additions,
  f.deletions, 
  f.changes, 
  f.status,
  f.previous_filename, 
  f.patch, 
  html_url AS commit_url,
  f.blob_url AS file_url,
FROM commit_files_long

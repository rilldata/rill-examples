-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

SELECT
    author_date AS date,
    c.commit_hash,
    commit_msg AS commit_message,
    author_name AS username,
    merge AS is_merge_commit,
    new_path AS file_path,
    filename,
    RIGHT(filename, POSITION('.' IN REVERSE(filename))) AS file_extension,
    CASE WHEN CONTAINS(file_path, '/')
      THEN SPLIT_PART(file_path, '/', 1)
      ELSE NULL
    END AS first_directory,
    CASE WHEN CONTAINS(SUBSTRING(file_path, LENGTH(first_directory) + 2), '/')
      THEN SPLIT_PART(file_path, '/', 2)
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
    added_lines AS additions,
    deleted_lines AS deletions, 
    additions + deletions AS changes, 
    old_path AS previous_file_path,
FROM clickhouse_commits_source c
LEFT JOIN clickhouse_modified_files f ON c.commit_hash = f.commit_hash
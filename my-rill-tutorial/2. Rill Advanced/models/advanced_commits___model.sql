-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

WITH commit_file_stats AS (
    SELECT
        a.*,
        b.filename,
        b.added_lines,
        b.deleted_lines,
        REGEXP_EXTRACT(b.new_path, '(.*/)', 1) AS directory_path, 
    FROM
        commits__ a
    inner JOIN
        modified_files__ b
    ON
        a.commit_hash = b.commit_hash
)
SELECT
    author_date,
    author_name,
    directory_path,
    -- UNNEST(regexp_split_to_array(directory_path, '/')),
    filename,
    STRING_AGG(DISTINCT commit_msg, ', ') AS commit_msg,

    COUNT(DISTINCT commit_hash) AS num_commits,
    SUM(added_lines) - SUM(deleted_lines) AS net_line_changes, 
    SUM(added_lines) + SUM(deleted_lines) AS total_line_changes, 

    -- (SUM(deleted_lines) / (SUM(added_lines) + SUM(deleted_lines))) as CodeDeletePercent, 
    sum(added_lines) as added_lines,
    sum(deleted_lines) as deleted_lines, 

FROM
    commit_file_stats
WHERE
    directory_path IS NOT NULL
    AND author_date < (CURRENT_DATE + INTERVAL '1 week')
GROUP BY 
    --directory_path, filename, author_name, author_date
    ALL
ORDER BY
    author_date DESC 

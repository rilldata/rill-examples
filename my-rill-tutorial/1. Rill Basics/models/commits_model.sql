-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

SELECT
    a.*,
    b.filename,
    b.added_lines,
    b.deleted_lines
FROM
     commits  a
LEFT JOIN
    modified_files b
ON
    a.commit_hash = b.commit_hash
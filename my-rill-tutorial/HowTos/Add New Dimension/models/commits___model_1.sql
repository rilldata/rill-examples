SELECT
    a.commit_hash,
    a.author_date,
    a.author_name,

    a.author_email, -- new column

    b.filename,
    b.added_lines,
    b.deleted_lines
FROM
    commits__ a
INNER JOIN
    modified_files__ b
ON
    a.commit_hash = b.commit_hash


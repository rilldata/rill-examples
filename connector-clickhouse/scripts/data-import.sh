#!/bin/bash

# Import repository data into ClickHouse
## Usage Sample
# scripts/data-import.sh <path-to-repository>
repo=$1
if [ -z "$repo" ]; then
    # If no argument provided, use the current directory
    repo=$(pwd)
fi
# Check if repo name starts with https:// or contains github
if [[ "$repo" == https://* ]] || [[ "$repo" == *github* ]]; then
    temp_dir=$(mktemp -d)
    cd "$temp_dir"
    echo "Cloning repository into temporary directory $repo..."
    git clone "$repo"
    reponame=$(basename "$repo")
    repo="$temp_dir/${reponame%.git}"
fi


# Generate TSV files for repository data
cd $repo && clickhouse git-import --skip-paths 'generated\.cpp|^(contrib|docs?|website|libs/(libcityhash|liblz4|libdivide|libvectorclass|libdouble-conversion|libcpuid|libzstd|libfarmhash|libmetrohash|libpoco|libwidechar_width))/' --skip-commits-with-messages '^Merge branch '

# Import data into clickhouse
clickhouse client --query="DROP TABLE IF EXISTS file_changes"
clickhouse client --query="CREATE TABLE file_changes
                           (
                               change_type Enum('Add' = 1, 'Delete' = 2, 'Modify' = 3, 'Rename' = 4, 'Copy' = 5, 'Type' = 6),
                               path LowCardinality(String),
                               old_path LowCardinality(String),
                               file_extension LowCardinality(String),
                               lines_added UInt32,
                               lines_deleted UInt32,
                               hunks_added UInt32,
                               hunks_removed UInt32,
                               hunks_changed UInt32,

                               commit_hash String,
                               author LowCardinality(String),
                               time DateTime,
                               commit_message String,
                               commit_files_added UInt32,
                               commit_files_deleted UInt32,
                               commit_files_renamed UInt32,
                               commit_files_modified UInt32,
                               commit_lines_added UInt32,
                               commit_lines_deleted UInt32,
                               commit_hunks_added UInt32,
                               commit_hunks_removed UInt32,
                               commit_hunks_changed UInt32
                           ) ENGINE = MergeTree ORDER BY time"

clickhouse client --query="INSERT INTO file_changes FORMAT TSV" < $repo/file_changes.tsv

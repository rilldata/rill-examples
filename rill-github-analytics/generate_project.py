#!/usr/bin/env python3
"""
Setup script to generate Rill project files for analyzing any GitHub repository.

Usage:
    python generate_project.py owner/repo --gcs --bucket gs://bucket/path [--display-name "My Repo"]
    python generate_project.py owner/repo --local [--display-name "My Repo"]

Examples:
    python generate_project.py duckdb/duckdb --gcs --bucket gs://my-bucket/github-analytics
    python generate_project.py duckdb/duckdb --local
    python generate_project.py clickhouse/clickhouse --gcs --bucket gs://my-bucket --display-name "ClickHouse"
"""

import argparse
import logging
import os
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def sanitize_name(repo_slug):
    """Convert 'owner/repo' to 'repo' for file naming."""
    return repo_slug.split("/")[-1].replace("-", "_").lower()


def create_source_files(name, repo_slug, use_local=True, gcs_bucket=None):
    """Generate source YAML files for commits and modified files."""
    
    if use_local:
        # Local DuckDB sources
        commits_source = f"""# Visit https://docs.rilldata.com/ to learn more about Rill code files.

type: "duckdb"
sql: "SELECT * FROM read_parquet('data/{name}_commits*.parquet')"
"""
        modified_files_source = f"""# Visit https://docs.rilldata.com/ to learn more about Rill code files.

type: "duckdb"
sql: "SELECT * FROM read_parquet('data/{name}_modified_files*.parquet')"
"""
    else:
        # GCS sources
        commits_source = f"""# Visit https://docs.rilldata.com/ to learn more about Rill code files.

connector: "gcs"
uri: "{gcs_bucket}/{repo_slug}/commits*.parquet"
# Get the most recent file
extract:
  files:
    strategy: tail
    size: 1
"""
        modified_files_source = f"""# Visit https://docs.rilldata.com/ to learn more about Rill code files.

connector: "gcs"
uri: "{gcs_bucket}/{repo_slug}/modified_files*.parquet"
# Get the most recent file
extract:
  files:
    strategy: tail
    size: 1
"""
    
    # Write files
    os.makedirs("sources", exist_ok=True)
    
    commits_path = f"sources/{name}_commits_source.yaml"
    with open(commits_path, "w") as f:
        f.write(commits_source)
    logger.info(f"Created {commits_path}")
    
    modified_path = f"sources/{name}_modified_files.yaml"
    with open(modified_path, "w") as f:
        f.write(modified_files_source)
    logger.info(f"Created {modified_path}")


def create_model_file(name):
    """Generate the SQL model file."""
    
    model_sql = f"""-- Model SQL
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
FROM {name}_commits_source c
LEFT JOIN {name}_modified_files f ON c.commit_hash = f.commit_hash
"""
    
    os.makedirs("models", exist_ok=True)
    model_path = f"models/{name}_commits_model.sql"
    with open(model_path, "w") as f:
        f.write(model_sql)
    logger.info(f"Created {model_path}")


def create_metrics_file(name, display_name):
    """Generate the metrics view YAML file."""
    
    metrics_yaml = f"""# Metrics view YAML
# Reference documentation: https://docs.rilldata.com/reference/project-files/dashboards

version: 1
type: metrics_view

display_name: {display_name} Commits Metrics
model: {name}_commits_model
timeseries: date
smallest_time_grain: "day"

dimensions:
  - name: commit_hash
    display_name: Commit hash
    expression: commit_hash
    description: ""
  - name: commit_message
    display_name: Commit message
    expression: commit_message
    description: ""
  - name: username
    display_name: Username
    expression: username
    description: ""
  - name: file_path
    display_name: File path
    expression: file_path
    description: ""
  - name: filename
    display_name: Filename
    expression: filename
    description: ""
  - name: file_extension
    display_name: File extension
    expression: file_extension
    description: ""
  - name: first_directory
    display_name: First directory
    expression: first_directory
    description: ""
  - name: second_directory
    display_name: Second directory
    expression: second_directory_concat
    description: ""
  - name: previous_file_path
    display_name: Previous file path
    expression: previous_file_path
    description: ""
  - name: is_merge_commit
    display_name: Merge commit
    expression: is_merge_commit
    description: "True if the commit is a merge commit"

measures:
  - display_name: "Number of commits"
    expression: "count(distinct commit_hash)"
    name: count_distinct_commit_hash
    description: ""
    format_preset: humanize
  - display_name: Number of files touched
    expression: count(distinct filename)
    name: count_distinct_filename
    description: ""
    format_preset: humanize
  - display_name: "Number of contributors"
    expression: "count(distinct username)"
    name: count_distinct_username
    description: ""
    format_preset: humanize
  - display_name: "Code additions"
    expression: "sum(additions)"
    name: sum_of_additions
    description: ""
    format_preset: humanize
  - display_name: "Code deletions"
    expression: "sum(deletions)"
    name: sum_of_deletions
    description: ""
    format_preset: humanize
  - display_name: "Code changes"
    expression: "sum(changes)"
    name: sum_of_changes
    description: ""
    format_preset: humanize
  - display_name: "Code deletion %"
    expression: "sum(deletions) / sum(changes)"
    name: percent_code_change
    description: "The percentage of code changes that were deletions."
    format_preset: percentage
  - display_name: "Files touched per commit"
    expression: "count(*) / count(distinct commit_hash)"
    name: count_files_touched_per_commit
    description: ""
    format_preset: humanize
"""
    
    os.makedirs("metrics", exist_ok=True)
    metrics_path = f"metrics/{name}_commits_metrics.yaml"
    with open(metrics_path, "w") as f:
        f.write(metrics_yaml)
    logger.info(f"Created {metrics_path}")


def create_dashboard_file(name, display_name):
    """Generate the explore dashboard YAML file."""
    
    dashboard_yaml = f"""# Explore YAML
# Reference documentation: https://docs.rilldata.com/reference/project-files/explores

type: explore

display_name: "{display_name} Commits"
metrics_view: {name}_commits_metrics

dimensions: "*"
measures: "*"
defaults:
  measures:
    - count_distinct_commit_hash
    - count_distinct_filename
    - count_distinct_username
    - sum_of_additions
    - sum_of_deletions
    - sum_of_changes
    - percent_code_change
    - count_files_touched_per_commit
  dimensions:
    - commit_hash
    - commit_message
    - username
    - file_path
    - filename
    - file_extension
    - first_directory
    - second_directory
    - previous_file_path
    - is_merge_commit
  time_range: P12M
"""
    
    os.makedirs("dashboards", exist_ok=True)
    dashboard_path = f"dashboards/{name}_commits_explore.yaml"
    with open(dashboard_path, "w") as f:
        f.write(dashboard_yaml)
    logger.info(f"Created {dashboard_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Rill project files for analyzing a GitHub repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # For GCS deployment
  python generate_project.py duckdb/duckdb --gcs --bucket gs://my-bucket/github-analytics
  
  # For local testing
  python generate_project.py duckdb/duckdb --local
  
  # With custom display name
  python generate_project.py clickhouse/clickhouse --gcs --bucket gs://my-bucket --display-name "ClickHouse"
        """
    )
    parser.add_argument(
        "repo_slug",
        help="GitHub repository in format 'owner/repo' (e.g., 'duckdb/duckdb')"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local parquet files in data/ directory (for testing)"
    )
    parser.add_argument(
        "--gcs",
        action="store_true",
        help="Use Google Cloud Storage (for deployment)"
    )
    parser.add_argument(
        "--bucket",
        help="GCS bucket path (required with --gcs, e.g., gs://my-bucket/github-analytics)"
    )
    parser.add_argument(
        "--display-name",
        help="Display name for the dashboard (default: repo name)"
    )
    
    args = parser.parse_args()
    
    # Validate repo slug format
    if not re.match(r"^[\w-]+/[\w-]+$", args.repo_slug):
        logger.error("Invalid repo slug format. Use 'owner/repo' (e.g., 'duckdb/duckdb')")
        return 1
    
    # Validate storage flags
    storage_flags = sum([args.local, args.gcs])
    
    if storage_flags == 0:
        logger.error("Must specify storage location: --local or --gcs")
        return 1
    
    if storage_flags > 1:
        logger.error("Cannot specify both --local and --gcs")
        return 1
    
    # Validate bucket requirement
    if args.gcs and not args.bucket:
        logger.error("--bucket is required when using --gcs")
        return 1
    
    # Generate sanitized name and display name
    name = sanitize_name(args.repo_slug)
    display_name = args.display_name or name.replace("_", " ").title()
    
    logger.info(f"Setting up Rill project for {args.repo_slug}")
    logger.info(f"  File prefix: {name}")
    logger.info(f"  Display name: {display_name}")
    logger.info(f"  Storage: {'Local files' if args.local else f'GCS ({args.bucket})'}")
    
    # Create all files
    create_source_files(name, args.repo_slug, args.local, args.bucket)
    create_model_file(name)
    create_metrics_file(name, display_name)
    create_dashboard_file(name, display_name)
    
    logger.info("✅ Setup complete!")
    logger.info("Next steps:")
    
    if args.local:
        logger.info(f"  1. Download commit data:")
        logger.info(f"     python download_commits.py {args.repo_slug} --local")
        logger.info(f"  2. Start Rill: rill start")
        logger.info(f"  3. Open dashboard: {name}_commits_explore")
    else:
        logger.info(f"  1. Download and upload data:")
        logger.info(f"     python download_commits.py {args.repo_slug} --gcs \\")
        logger.info(f"       --bucket {args.bucket}")
        logger.info(f"  2. Start Rill: rill start")
        logger.info(f"  3. Open dashboard: {name}_commits_explore")
        logger.info(f"  4. Deploy: rill deploy")
    
    return 0


if __name__ == "__main__":
    exit(main())


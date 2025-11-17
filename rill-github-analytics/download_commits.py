#!/usr/bin/env python3
"""
Download GitHub commit data for a repository.

Usage:
    python download_commits.py owner/repo --gcs --bucket gs://bucket/path [--limit N]
    python download_commits.py owner/repo --local [--limit N]

Examples:
    # Upload to GCS (recommended for deployment)
    python download_commits.py duckdb/duckdb --gcs --bucket gs://my-bucket/github-analytics
    
    # Save locally (for testing)
    python download_commits.py rilldata/rill --local --limit 1000
"""

import argparse
import logging
import os
from pathlib import Path

import pandas as pd
from pydriller import Repository

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


def write_to_local(df, filename, repo_name):
    """Write dataframe to local parquet file."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    TIMESTAMP = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
    filepath = data_dir / f"{repo_name}_{filename}_{TIMESTAMP}.parquet"
    df.to_parquet(filepath)
    logger.info(f"Wrote {len(df)} rows to {filepath}")
    return filepath


def write_to_gcs(df, filename, bucket_path, repo_slug, service_account_key_file):
    """Write dataframe to GCS bucket."""
    # Set the environment variable for the service account key file
    if service_account_key_file and os.path.exists(service_account_key_file):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_file
    
    TIMESTAMP = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
    filepath = f"{bucket_path}/{repo_slug}/{filename}_{TIMESTAMP}.parquet"
    df.to_parquet(filepath)
    logger.info(f"Wrote {len(df)} rows to {filepath}")
    return filepath


def download_commits(repo_url, repo_slug, repo_name, use_local=True, limit=None, gcs_bucket=None, gcs_key_file=None):
    """Download commits and modified files from a GitHub repository."""
    commits = []
    modified_files = []
    
    logger.info(f"Downloading commits from {repo_url}")
    if limit:
        logger.info(f"Limiting to {limit} most recent commits")

    # Traverse the commits in the repository
    count = 0
    for commit in Repository(repo_url).traverse_commits():
        commits.append(
            {
                "commit_hash": commit.hash,
                "commit_msg": commit.msg,
                "author_name": commit.author.name,
                "author_email": commit.author.email,
                "author_date": commit.author_date,
                "author_timezone": commit.author_timezone,
                "merge": commit.merge,
            }
        )

        # Iterate over the modified files in each commit
        for modified_file in commit.modified_files:
            modified_files.append(
                {
                    "commit_hash": commit.hash,
                    "filename": modified_file.filename,
                    "old_path": modified_file.old_path,
                    "new_path": modified_file.new_path,
                    "added_lines": modified_file.added_lines,
                    "deleted_lines": modified_file.deleted_lines,
                }
            )
        
        count += 1
        if count % 100 == 0:
            logger.info(f"Processed {count} commits...")
        
        if limit and count >= limit:
            logger.info(f"Reached limit of {limit} commits")
            break

    logger.info(f"Downloaded {len(commits)} commits with {len(modified_files)} file modifications")
    
    # Convert to dataframes
    commits_df = pd.DataFrame(commits)
    modified_files_df = pd.DataFrame(modified_files)
    
    # Write the commits and modified files
    if use_local:
        write_to_local(commits_df, "commits", repo_name)
        write_to_local(modified_files_df, "modified_files", repo_name)
    else:
        write_to_gcs(commits_df, "commits", gcs_bucket, repo_slug, gcs_key_file)
        write_to_gcs(modified_files_df, "modified_files", gcs_bucket, repo_slug, gcs_key_file)

    return


def main():
    parser = argparse.ArgumentParser(
        description="Download GitHub commit data for analysis in Rill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload to GCS (recommended for deployment)
  python download_commits.py duckdb/duckdb --gcs --bucket gs://my-bucket/github-analytics
  python download_commits.py duckdb/duckdb --gcs --bucket gs://my-bucket/github-analytics --limit 1000
  
  # Save locally (for testing)
  python download_commits.py duckdb/duckdb --local --limit 1000
        """
    )
    parser.add_argument(
        "repo_slug",
        help="GitHub repository in format 'owner/repo' (e.g., 'rilldata/rill')"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Save to local data/ directory (for testing)"
    )
    parser.add_argument(
        "--gcs",
        action="store_true",
        help="Save to Google Cloud Storage"
    )
    parser.add_argument(
        "--s3",
        action="store_true",
        help="Save to Amazon S3 (not yet supported - use GCS for now)"
    )
    parser.add_argument(
        "--bucket",
        help="Cloud storage bucket path (required with --gcs, e.g., gs://my-bucket/github-analytics)"
    )
    parser.add_argument(
        "--gcs-key-file",
        help="Path to GCS service account key file (optional if GOOGLE_APPLICATION_CREDENTIALS is set)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of commits to download (useful for testing)"
    )
    
    args = parser.parse_args()
    
    # Construct repo URL (always use HTTPS)
    repo_url = f"https://github.com/{args.repo_slug}.git"
    repo_name = sanitize_name(args.repo_slug)
    
    # Determine storage location
    storage_flags = sum([args.local, args.gcs, args.s3])
    
    if storage_flags == 0:
        logger.error("Must specify storage location: --local, --gcs, or --s3")
        return 1
    
    if storage_flags > 1:
        logger.error("Cannot specify multiple storage locations")
        return 1
    
    if args.s3:
        logger.error("S3 support is not yet implemented. Please use --gcs for cloud storage.")
        logger.info("You can still use S3 with Rill by manually uploading the parquet files.")
        return 1
    
    if args.gcs and not args.bucket:
        logger.error("--bucket is required when using --gcs")
        return 1
    
    use_local = args.local
    
    logger.info(f"Repository: {args.repo_slug}")
    logger.info(f"Storage: {'Local (data/)' if use_local else 'GCS'}")
    
    download_commits(
        repo_url=repo_url,
        repo_slug=args.repo_slug,
        repo_name=repo_name,
        use_local=use_local,
        limit=args.limit,
        gcs_bucket=args.bucket,
        gcs_key_file=args.gcs_key_file if args.gcs else None
    )
    
    logger.info("\n✅ Download complete!")
    if use_local:
        logger.info(f"Data saved to data/ directory")
        logger.info(f"Next step: rill start")
    
    return 0


if __name__ == "__main__":
    exit(main())

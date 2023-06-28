# TODO:
# - Clean up code

import asyncio
import json
import logging
import os
import time
import urllib.request

import pandas as pd
from dotenv import load_dotenv
from google.cloud import storage

# REPO_SLUG = "rilldata/rill"
# REPO_START_DATE = "2021-12-09T00:00:00Z"

REPO_SLUG = "duckdb/duckdb"
REPO_START_DATE = "2018-06-26T00:00:00Z"

# Load environment variables from a .env file
load_dotenv()

# GitHub configurations
REPO_URL = f"https://api.github.com/repos/{REPO_SLUG}"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Google Cloud configurations
PROJECT_ID = "rilldata"
BUCKET = "pkg.rilldata.com"
BUCKET_SUBDIRECTORY = f"example-github-analytics/{REPO_SLUG}"

# File names
COMMITS = "commits"
COMMIT_DETAILS = "commit_details"
CURSOR_FILE = "cursor.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def fetch_api(path):
    url = REPO_URL + path
    req = urllib.request.Request(url)
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    try:
        with urllib.request.urlopen(req) as res:
            data = json.load(res)
            return data
    except Exception as e:
        raise e


def read_cursor(bucket, directory, key):
    blob = bucket.blob(f"{BUCKET_SUBDIRECTORY}/{directory}/{CURSOR_FILE}")

    if not blob.exists():
        logger.info(f"Cursor for {directory} does not exist")
        return None

    url = blob.generate_signed_url(version="v4", expiration=60, method="GET")
    req = urllib.request.Request(url)

    # Add headers to prevent caching
    req.add_header("Cache-Control", "no-cache")
    req.add_header("Pragma", "no-cache")
    req.add_header("If-None-Match", "*")

    with urllib.request.urlopen(req) as res:
        cursor_json = res.read().decode().strip()
        logger.info(f"Read {directory} cursor: {cursor_json}")
        cursor_data = json.loads(cursor_json)
        return cursor_data.get(key)


def get_commits_cursor(bucket):
    cursor = read_cursor(bucket, COMMITS, "until")
    return cursor or REPO_START_DATE


def get_commit_details_cursor(bucket):
    cursor = read_cursor(bucket, COMMIT_DETAILS, "commit_number")
    return cursor or None


def write_cursor(bucket, directory, cursor):
    cursor_json = json.dumps(cursor)
    try:
        blob = bucket.blob(f"{BUCKET_SUBDIRECTORY}/{directory}/{CURSOR_FILE}")
        blob.upload_from_string(cursor_json)
        logger.info(f"Wrote {directory} cursor: {cursor}")
    except Exception:
        logger.exception(
            f"Error occurred while updating {directory} cursor. Cursor is intended to be {cursor}"
        )


def write_parquet(data, path):
    df = pd.DataFrame(data)
    df.to_parquet(path)


def clean_commit_detail(commit_detail):
    # If `previous_filename` does not exist in the "files" array of structs, add it
    # Necessary as long as this issue is open: https://github.com/duckdb/duckdb/issues/7908
    commit_detail["files"] = [
        {**file, "previous_filename": None} if "previous_filename" not in file else file
        for file in commit_detail["files"]
    ]
    return commit_detail


def get_commits(bucket):
    commit_files = bucket.list_blobs(prefix=f"{BUCKET_SUBDIRECTORY}/{COMMITS}/")
    commit_file_paths = [blob.name for blob in commit_files]

    commit_data_frames = []
    for file_path in commit_file_paths:
        if file_path.endswith(".parquet"):
            blob = bucket.blob(file_path)
            with blob.open("rb") as f:
                df = pd.read_parquet(f)
                commit_data_frames.append(df)
    commits = pd.concat(commit_data_frames, ignore_index=True)
    return commits


# Fetches commits from the GitHub API and stores them in GCS
def download_commits(bucket):
    commits = []

    initial_cursor = get_commits_cursor(bucket)
    cursor = initial_cursor

    try:
        # Loop through days
        while True:
            # Create a 1-day window for each fetch
            next_cursor_dt = pd.to_datetime(cursor) + pd.Timedelta(days=1)
            if next_cursor_dt > pd.to_datetime("today", utc=True):
                logger.info("Reached today's date. Stopping.")
                break
            next_cursor = next_cursor_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            path = f"/commits?since={cursor}&until={next_cursor}"

            page_size = 100
            page = 1

            # Loop through pages
            while True:
                path += f"&per_page={page_size}&page={page}"

                try:
                    data = fetch_api(path)
                    logger.info(
                        f"Fetched {len(data)} commits from {cursor} to {next_cursor}"
                    )
                except Exception:
                    logger.exception(
                        f"Error occurred while fetching commits from {cursor} to {next_cursor}."
                    )
                    break  # Stop fetching more data upon encountering an error

                if len(data) == 0:
                    break

                data.reverse()  # Github returns data from newest to oldest. This reverses it.

                commits.extend(data)

                if len(data) == page_size:
                    page += 1
                else:
                    break

            # Move the cursor to the next day
            cursor = next_cursor

    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
        # Clean up and exit gracefully

    if cursor != initial_cursor:
        if len(commits) > 0:
            write_parquet(
                commits,
                f"gs://{BUCKET}/{BUCKET_SUBDIRECTORY}/{COMMITS}/{time.strftime('%Y%m%d%H%M%S')}_{COMMITS}.parquet",
            )
            logger.info(f"Wrote {len(commits)} commits to GCS")
        else:
            logger.info("No new commits to upload")
        write_cursor(bucket, COMMITS, {"until": cursor, "page": page})
    else:
        logger.info("No new commits to upload")

    logger.info("Done downloading commits")


# Fetches commit details for each commit and stores them in GCS
def download_commit_details(bucket):
    commit_details = []

    initial_cursor = get_commit_details_cursor(bucket)
    cursor = initial_cursor

    commits = get_commits(bucket)
    try:
        for commit_number, commit in commits.iterrows():
            # Skip until reaching the commit_details cursor
            if cursor and commit_number <= cursor:
                continue

            sha = commit["sha"]

            path = f"/commits/{sha}"
            try:
                commit_details_data = fetch_api(path)
                logger.info(f"Fetched details for commit {commit_number} (SHA: {sha})")
            except Exception:
                logger.exception(
                    f"Error occurred while fetching details for commit {commit_number} (SHA: {sha})."
                )
                break  # Stop fetching more data upon encountering an error

            commit_details.append(clean_commit_detail(commit_details_data))
            cursor = commit_number

    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
        # Clean up and exit gracefully

    if cursor != initial_cursor:
        write_parquet(
            commit_details,
            f"gs://{BUCKET}/{BUCKET_SUBDIRECTORY}/{COMMIT_DETAILS}/{time.strftime('%Y%m%d%H%M%S')}_{COMMIT_DETAILS}.parquet",
        )
        logger.info(f"Wrote {len(commit_details)} commit details to GCS")
        write_cursor(
            bucket,
            COMMIT_DETAILS,
            {"commit_number": cursor, "sha": commit_details[-1]["sha"]},
        )
    else:
        logger.info("No new commit details to upload")

    logger.info("Done downloading commit details")


async def main():
    storage_client = storage.Client(
        project=PROJECT_ID
    )  # authenticates via Application Default Credentials

    bucket = storage_client.bucket(BUCKET)

    download_commits(bucket)
    download_commit_details(bucket)


if __name__ == "__main__":
    asyncio.run(main())

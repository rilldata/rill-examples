# GitHub analytics with Rill

This project analyzes a Git project's commit activity. We use the [PyDriller Python library](https://pydriller.readthedocs.io/en/latest/) to traverse git commits, we store the data in Google Cloud Storage, and we analyze the data with an interactive Rill dashboard.

Here's the dashboard deployed for the DuckDB repository: https://ui.rilldata.com/demo/rill-github-analytics/duckdb_commits

Answer questions like:

- What parts of your codebase are the most active? What parts have the most churn?
- How large are commits? What do commits that touch many files have in common?
- How productive are your contributors? How does productivity change week over week?
- What parts of your codebase are different contributors working on? With what programming languages?

Follow the instructions below to analyze your own Git project.

## Clone this repository

To start, you'll want to clone this repository so you can edit the files and run the scripts.

```bash
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-github-analytics
```

## Create a bucket in Google Cloud Storage and set up a service account

1. Create a bucket in Google Cloud Storage
2. See these instructions for setting up a GCS service account: https://docs.rilldata.com/deploy/credentials/gcs#how-to-create-a-service-account-using-the-google-cloud-console
3. Save the service account key as a JSON file

## Run the download script

1. Edit the following variables in `download_commits.py`:

- `REPO_SLUG`
- `REPO_URL` (if your repo isn't on GitHub)
- `BUCKET_PATH`
- `GCP_SERVICE_ACCOUNT_KEY_FILE`

2. Run the script locally or setup a cronjob to run it periodically.

The project uses Poetry to manage its Python virtual environment. [Install Poetry](https://python-poetry.org/docs/) and run the following commands:

```bash
poetry install
poetry run python3 download.py
```

3. Upon completion, find the following files at your provided `BUCKET_PATH`:

- `commits/commits_{TIMESTAMP}.parquet`
- `commits/modified_files_{TIMESTAMP}.parquet`

## Edit the Rill artifacts and start Rill

1. Copy the `sources/duckdb_commits_source.yaml` and `sources/duckdb_modified_files_source.yaml` files and edit them to point to your bucket.
2. Copy the `models/duckdb_commits_model.sql` file and edit it to point to your new sources.
3. Copy the `dashboards/duckdb_commits.yaml` file and edit it to point to your new model.
4. Configure your storage credentials: https://docs.rilldata.com/deploy/credentials/
5. Install and start Rill

```bash
curl -s https://cdn.rilldata.com/install.sh | bash
rill start
```

6. Explore your dashboard!

## Publish your dashboard to Rill Cloud

Run `rill deploy` in your project directory and follow the instructions. [See docs](https://docs.rilldata.com/deploy/existing-project).

# GitHub Analytics with Rill

Analyze commit activity for any GitHub repository with interactive dashboards. This project provides automation scripts to extract Git history and generate Rill analytics in just a few commands.

**[See live demo →](https://ui.rilldata.com/demo/rill-github-analytics)** | **[Read the full guide →](https://docs.rilldata.com/guides/github-analytics)**

## Overview

This project uses:

- **[PyDriller](https://pydriller.readthedocs.io/)** to extract commit data from Git repositories
- **Automation scripts** (`download_commits.py`, `generate_project.py`) to scrape Git history and generate Rill project files
- **Cloud storage** (GCS) or local files for data
- **Rill** for fast, interactive analytics dashboards

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-github-analytics
poetry install

# 2. Generate Rill files
python generate_project.py your-org/your-repo --gcs --bucket gs://your-bucket/github-analytics

# 3. Download and upload data
python download_commits.py your-org/your-repo --gcs --bucket gs://your-bucket/github-analytics

# 4. Deploy
rill deploy
```

## Automation Scripts

This project includes two scripts to streamline setup:

### `generate_project.py`

Generates all Rill files (sources, models, metrics, dashboards) for a repository:

```bash
python generate_project.py owner/repo --gcs --bucket gs://bucket/path
python generate_project.py owner/repo --local  # For local testing
```

### `download_commits.py`

Extracts commit history and saves to cloud storage:

```bash
python download_commits.py owner/repo --gcs --bucket gs://bucket/path
python download_commits.py owner/repo --local  # For local testing
```

Both scripts require explicit storage flags (`--gcs` or `--local`).

## Project Structure

Generated files for each repository:

- `sources/{repo}_commits_source.yaml` – Data source for commits
- `sources/{repo}_modified_files.yaml` – Data source for file changes
- `models/{repo}_commits_model.sql` – SQL transformations
- `metrics/{repo}_commits_metrics.yaml` – Metrics definitions
- `dashboards/{repo}_commits_explore.yaml` – Explore dashboard

## Authentication

**For private repositories:** Set `GITHUB_TOKEN` environment variable with a [fine-grained personal access token](https://github.com/settings/tokens?type=beta).

**For GCS:** Set `GOOGLE_APPLICATION_CREDENTIALS` to your service account key path. See [GCS credentials guide](https://docs.rilldata.com/deploy/credentials/gcs).

## Learn More

- **[Full Tutorial](https://docs.rilldata.com/guides/github-analytics)** – Step-by-step guide with prerequisites and examples
- **[Rill Documentation](https://docs.rilldata.com)** – Learn more about Rill
- **[Discord Community](https://discord.gg/DJ5qcsxE2m)** – Get help and share your dashboards

# Analyzing GitHub commits with Rill and Clickhouse

To start, clone this repository and navigate to the `connector-clickhouse` directory.

```bash
git clone git@github.com:rilldata/rill-examples.git && cd rill-examples/connector-clickhouse
```

## Install and start ClickHouse

Install ClickHouse:

```bash
curl https://clickhouse.com/ | sh
```

Start a ClickHouse Local server in a contained directory:

```bash
mkdir clickhouse_data && cd clickhouse_data
clickhouse server
```

## Import data from a GitHub repository

Replace the below git URL with the one you want to analyze.

```bash
scripts/data-import.sh https://github.com/ClickHouse/ClickHouse
```

## Install and start Rill

Install Rill:

```bash
curl https://rill.sh | sh
```

Start Rill:

```bash
rill start
```

This will open Rill in your browser. Navigate to http://localhost:9009/dashboard/git_commits to see the dashboard.

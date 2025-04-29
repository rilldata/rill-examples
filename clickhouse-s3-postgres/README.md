# ClickHouse with S3 and Postgres example

This project contains a boilerplate Rill project with:
- ClickHouse configured as the default OLAP engine
- An incremental source that ingests Hive-partitioned Parquet files from S3
- A source that ingests a lookup table from Postgres and creates it as a ClickHouse [dictionary](https://clickhouse.com/docs/sql-reference/dictionaries)
- A metrics view with a dimension that does a query-time lookup in the dictionary table

## How to configure

1. Copy `.env.example` to `.env` and populate it with S3 and Postgres credentials
2. Adapt the source and metrics definitions to your actual data locations and schemas
3. When you are ready to deploy the project, configure `clickhouse_dsn_prod` in `.env` to the DSN of a production ClickHouse cluster. This setting is not needed in local development because Rill will automatically start Clickhouse as a subprocess.

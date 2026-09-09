# Rill model patterns

A gallery of YAML-only Rill model patterns for Snowflake, BigQuery, S3-to-DuckDB, and S3-to-ClickHouse. The warehouse examples use a small `analytics.events` fact table. Both S3-backed directories use the equivalent Parquet prefix with this logical shape:

| Column                                       | Purpose                                |
| -------------------------------------------- | -------------------------------------- |
| `event_id`                                   | Stable event key                       |
| `event_time`                                 | Business event timestamp               |
| `updated_at`                                 | Last source-side update timestamp      |
| `user_id`, `region`, `event_type`, `revenue` | Example dimensions and measure         |

The S3 examples assume the layout `s3://example-bucket/analytics/events/dt=YYYY-MM-DD/hour=HH/*.parquet`. The ClickHouse examples execute ClickHouse's native `s3()` table function and materialize the selected rows into ClickHouse. Replace the bucket and prefix with your own before running anything.

Every model carries a `# disable: true` line inside its `refresh` block, commented out. A copied example therefore reconciles when its project starts and can run later on its schedule once credentials are present. Starting this gallery root can reconcile many models immediately, independently of their cron schedules. Do not start the gallery root or give it real credentials; copy only the example you intend to use into a scratch project, and uncomment `disable: true` until you are ready to ingest data.

The project default remains DuckDB for the other galleries, so every ClickHouse model explicitly sets `connector: clickhouse` for SQL execution and `output.connector: clickhouse` for materialization. The ClickHouse connector is read-write because Rill creates, inserts into, alters, and replaces model tables.

In each model, the top-level `partitions` and `sql` are the production defaults. The canonical scenarios 01 and 02 also repeat them under explicit `prod.partitions` and `prod.sql` blocks to demonstrate environment overrides. A nested `dev` block narrows ingestion to a single date or fewer buckets.

## The recommended pattern

For a new S3-to-ClickHouse incremental model, start from scenario **01** or **02**. The example below uses daily replacement units:

```yaml
incremental: true
change_mode: patch                       # Adopt definition changes without an automatic full rebuild.
partitions_watermark: updated_on          # Re-queue a prefix when its S3 objects change.

partitions:
  glob:
    connector: s3
    path: s3://example-bucket/analytics/events/dt=*
    partition: directory

sql: |
  SELECT ...
  FROM s3(
    '{{ .partition.uri }}/hour=*/*.parquet',
    '{{ .env.AWS_ACCESS_KEY_ID }}',
    '{{ .env.AWS_SECRET_ACCESS_KEY }}',
    'Parquet'
  )

output:
  connector: clickhouse
  incremental_strategy: partition_overwrite  # Idempotent: a rerun replaces the partition.
  partition_by: event_date
  order_by: (event_date, region, event_type, user_id, event_time, event_id)
  primary_key: (event_date, region, event_type, user_id)
  ttl: event_time + INTERVAL 365 DAY DELETE
  query_settings: use_structure_from_insertion_table_in_table_functions = 0
  columns: |
    (
      event_id UUID,
      event_time DateTime64(3, 'UTC'),
      event_date Date,
      updated_at DateTime64(3, 'UTC'),
      user_id UInt64,
      region LowCardinality(String),
      event_type LowCardinality(String),
      revenue Decimal(18, 4),
      INDEX idx_event_id event_id TYPE bloom_filter(0.01) GRANULARITY 4,
      INDEX idx_user_id user_id TYPE bloom_filter(0.01) GRANULARITY 4
    )
```

The three properties solve three different problems, and they are designed to be used together:

- **`partition_overwrite` gives idempotency.** Rerunning a partition replaces its rows instead of adding to them, so a failed run, a manual retry, and a targeted backfill all converge on the same output. This is the property that makes a pipeline safe to operate.
- **`change_mode: patch` keeps definition changes cheap.** New logic takes effect on the next run without automatically rescanning history. Combined with `partition_overwrite`, you can then backfill exactly the partitions that need the new logic.
- **`partitions_watermark` handles changed objects.** Glob discovery returns `updated_on`; whenever it advances, Rill marks the already-loaded S3 prefix pending again.

For ClickHouse, `output.partition_by` defines both the physical MergeTree partition and the replacement boundary used by `partition_overwrite`. Those boundaries must match the data produced by one Rill partition run. An hourly run must not emit only one hour into a monthly replacement partition, because that would replace the rest of the month.

The overwrite examples derive `event_hour` or `event_date` from the S3 prefix and filter out rows whose `event_time` does not belong to that prefix. This prevents a misplaced row from replacing a different ClickHouse partition. In production, route rejected rows to a quarantine process or fail the upstream partition build rather than silently discarding them.

- Scenario 01 uses hourly physical partitions and a 30-day TTL, bounding active partitions to roughly 720.
- Scenarios 02, 04, 05, and 06 use daily physical partitions and a 365-day TTL, bounding active partitions to roughly 365.
- Merge scenarios use monthly physical partitions because they insert versions instead of replacing an incomplete physical partition.

The `order_by` and primary key assume queries filter first by date, then by region/event type, and sometimes by user. Adapt them to actual query logs before creating production tables because a MergeTree sorting key cannot be changed in place. The bloom-filter indexes demonstrate exact lookups outside the leading key prefix; validate that they skip enough granules on real data before retaining them.

The `query_settings` value makes ClickHouse infer the schema of `s3()` from the Parquet files rather than from the insertion table. This is necessary because the output schema contains derived columns such as `event_date` that do not exist in the files.

Note that Rill spells the strategy `partition_overwrite`; `partition_override` is not a valid value.

## Layout

Each source directory contains the same nine scenarios. Filenames omit the redundant source prefix because their parent directory already identifies the source; each YAML spec declares an explicit globally unique resource `name` so the complete Rill project remains valid.

| #   | Scenario                            | Primary features                                                                          |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| 00  | Full-refresh baseline               | Non-incremental materialization and a dev limit                                            |
| 01  | **Hourly partition overwrite with watermark** | **The recommended pattern: `partition_overwrite` + `patch` + watermark, one hour per partition** |
| 02  | Daily partition overwrite with watermark | The same recommended pattern at a daily grain                                          |
| 03  | Late hourly updates with merge      | Versioned `ReplacingMergeTree` ingestion when rows are updated independently                |
| 04  | Patch schema evolution              | `change_mode: patch`; new logic applies without a history rebuild                          |
| 05  | Reset schema evolution              | `change_mode: reset`; definition changes rebuild history                                   |
| 06  | Schema hook and retries             | Idempotent additive `pre_exec`, output field, post-check, exponential backoff              |
| 07  | Hash buckets                        | Non-time partition key for skewed or flat layouts                                          |
| 08  | State-based incremental             | `state` instead of `partitions`, and why partitions are preferred                          |

Scenarios 00 through 07 use `partitions`. Scenario 08 is the single state-based counterexample per source: it is included so the trade-off is visible, not because it is recommended.

## Cron patterns in the gallery

| Expression     | Meaning                          | Typical scenario                       |
| -------------- | -------------------------------- | -------------------------------------- |
| `5 * * * *`    | Five minutes after every hour    | Hourly closed-window ingestion         |
| `0 1 * * *`    | Daily at 01:00                   | Hash-bucket refresh                    |
| `0 2 * * *`    | Daily at 02:00                   | Daily partition overwrite              |
| `0 3 * * *`    | Daily at 03:00                   | State-based incremental run            |
| `0 6 * * 1-5`  | Weekdays at 06:00                | Controlled schema rollout              |
| `0 3 1 * *`    | Monthly on day 1 at 03:00        | Reset-driven rebuild                   |

Every schedule has an explicit `time_zone`. Cron schedules do not run in local development unless `run_in_dev: true` is set, so `rill start .` on a copied example will not fire the cron by itself.

## Incremental strategies

- `partition_overwrite` replaces every output row belonging to the configured `output.partition_by` value. It is the preferred strategy, and the default in this gallery, because retrying a day, hour, week, or month remains idempotent.
- For ClickHouse, `merge` requires a `ReplacingMergeTree` engine. The ClickHouse executor does not use `output.unique_key`; deduplication is determined by the complete sorting key. These examples use `ReplacingMergeTree(updated_at)` with `(event_date, event_id)`, so `event_time` must remain immutable for an event. Replacement is eventually applied by background merges, and queries requiring immediate deduplication may need `FINAL` selectively.
- `append` is deliberately not demonstrated. It inserts without matching or deleting, so a rerun of the same input duplicates rows. Use `partition_overwrite` instead; it is idempotent even for data you believe is immutable.

## Watermarks and late data

`partitions_watermark` names a timestamp returned by the partition discovery query. The watermark is excluded from the partition identity. When its value advances, Rill marks that existing partition pending again.

- Warehouse examples discover watermarks with SQL.
- S3 glob discovery exposes `updated_on`, so `partitions_watermark: updated_on` re-queues a prefix whose objects were rewritten.

An object-listing watermark is not a deletion manifest. Deleting an object may not advance the directory watermark, and a reprocessed prefix that becomes completely empty produces no temporary ClickHouse partition to replace. If deletes must propagate, publish a monotonically increasing manifest/version for each prefix or run an explicit destination-partition cleanup workflow.

The watermark cannot be assigned the value `manual`; it is a column name, not an execution mode.

For sources whose updates can arrive after a long delay, expand the discovery query's lookback or remove it entirely. A bounded lookback controls source cost but is also the maximum lateness the model can notice automatically.

## Schema-change modes

- `patch` (recommended): adopt later definition changes without automatically rebuilding historical data. Existing rows retain their old shape or logic, so pair it with `partition_overwrite` and backfill the affected partitions explicitly when historical consistency matters.
- `reset`: automatically drop and recreate output after a definition change. This produces consistent history at the cost of a full source scan.

`change_mode: manual` also exists in Rill, but this gallery does not demonstrate it: it pauses reconciliation until an operator chooses a refresh, which is useful for approval gates but obscures the pattern the examples are teaching.

## Running an example

Create a scratch Rill project containing only one connector and one model. This keeps unrelated models from scanning warehouses or producing missing-credential errors:

```bash
example_dir="$(mktemp -d /tmp/rill-model-example.XXXXXX)"
mkdir -p "$example_dir/connectors" "$example_dir/models"
cp rill.yaml .env.example "$example_dir/"
cp connectors/s3.yaml connectors/clickhouse.yaml "$example_dir/connectors/"
cp models/clickhouse/01_hourly_partition_overwrite_watermark.yaml "$example_dir/models/"
cd "$example_dir"
cp .env.example .env
# Populate CLICKHOUSE_DSN and AWS credentials, then replace the example S3 path.
# The cron is live; uncomment refresh.disable if you want to inspect the model without running it.
rill start .
```

Substitute connector and model paths for another scenario. Do not run models from the gallery root; it contains many live example resources and is intended for browsing and copying.

Useful commands:

```bash
rill project partitions --local --model clickhouse_01_hourly_partition_overwrite_watermark
rill project refresh --local --model clickhouse_01_hourly_partition_overwrite_watermark
rill project refresh --local --model clickhouse_01_hourly_partition_overwrite_watermark --full
# Copy a key from the partitions listing, then target only that partition:
rill project refresh --local --model clickhouse_01_hourly_partition_overwrite_watermark --partition <partition-key>
```

## Validation

Run `./scripts/check_examples.sh`. It checks that all nine ClickHouse examples read through `s3()`, write to ClickHouse, define ordering, TTL, schema, and indexes, and that the recommended incremental examples use S3 partitions with `partition_overwrite`. The checks are static; running a model still requires real credentials and the example Parquet prefix.

## Canonical references

- [Rill model runtime guidance](https://github.com/rilldata/rill/blob/main/runtime/ai/instructions/data/resources/model.md)
- [Model YAML reference](https://docs.rilldata.com/reference/project-files/models)
- [Partitioned models](https://docs.rilldata.com/developers/build/models/partitioned-models)
- [Incremental models](https://docs.rilldata.com/developers/build/models/incremental-models)
- [Connector YAML reference](https://docs.rilldata.com/reference/project-files/connectors)
- [ClickHouse primary-key guidance](https://clickhouse.com/docs/best-practices/choosing-a-primary-key)
- [ClickHouse partitioning guidance](https://clickhouse.com/docs/best-practices/choosing-a-partitioning-key)
- [ClickHouse skipping indexes](https://clickhouse.com/docs/best-practices/use-data-skipping-indices-where-appropriate)

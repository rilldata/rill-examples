# Rill model patterns

A source-by-source gallery of YAML-only Rill model patterns for Snowflake, BigQuery, ClickHouse, and S3. The warehouse examples use a small `analytics.events` fact table, and the S3 examples use an equivalent Parquet prefix, with this logical shape:

| Column                                       | Purpose                                |
| -------------------------------------------- | -------------------------------------- |
| `event_id`                                   | Stable event key                       |
| `event_time`                                 | Business event timestamp               |
| `updated_at`                                 | Last source-side update timestamp      |
| `user_id`, `region`, `event_type`, `revenue` | Example dimensions and measure         |

The S3 examples assume the layout `s3://example-bucket/analytics/events/dt=YYYY-MM-DD/hour=HH/*.parquet`. Replace the bucket and prefix with your own before running anything.

Every model carries a `# disable: true` line inside its `refresh` block, commented out. A copied example therefore runs as-is on its cron once credentials are present; uncomment that line whenever you want a resource to stay inactive. Because the schedules are live, do not point the repository root at real credentials unless you intend the models to run.

Current Rill releases do not provide a direct ClickHouse-source-to-DuckDB-output executor. The ClickHouse models document the requested target shape and are marked conceptual; do not enable them without first replacing that connector path with a supported architecture. BigQuery, Snowflake, and S3 exports use supported paths into DuckDB.

## The recommended pattern

For a new incremental model, start from scenario **01** and change only the partition grain:

```yaml
incremental: true
change_mode: patch                       # Adopt definition changes without an automatic full rebuild.
partitions_watermark: watermark_interval # Re-queue a partition while it is still inside its lateness window.

partitions:
  sql: |
    SELECT
      DATE(event_time) AS partition_date,
      LEAST(NOW(), TIMESTAMP(DATE(event_time)) + INTERVAL 1 DAY) AS watermark_interval
    FROM events
    GROUP BY 1

output:
  incremental_strategy: partition_overwrite  # Idempotent: a rerun replaces the partition.
  partition_by: event_date
```

The three properties solve three different problems, and they are designed to be used together:

- **`partition_overwrite` gives idempotency.** Rerunning a partition replaces its rows instead of adding to them, so a failed run, a manual retry, and a targeted backfill all converge on the same output. This is the property that makes a pipeline safe to operate.
- **`change_mode: patch` keeps definition changes cheap.** New logic takes effect on the next run without automatically rescanning history. Combined with `partition_overwrite`, you can then backfill exactly the partitions that need the new logic.
- **`partitions_watermark` handles late data.** It names any timestamp the partition query returns, not necessarily a column. Whenever the value advances, Rill marks that already-loaded partition pending again.

The gallery uses `LEAST(NOW(), <partition start> + INTERVAL n)` rather than a bare `MAX(updated_at)`, because it makes the lateness policy explicit:

- While the partition is younger than the interval, the expression evaluates to `NOW()`, which advances on every discovery pass, so the partition is reprocessed on every refresh. With `partition_overwrite` that is safe, just not free.
- Once the interval has elapsed, the expression freezes at a constant and the partition is never re-queued again.

That is a **declared** lateness window: it needs no reliable `updated_at` in the source and no `MAX()` aggregation to detect change, at the cost of reprocessing partitions that did not change and going blind to corrections arriving after the window. `MAX(updated_at)` is the data-driven alternative — it reprocesses only what actually changed and catches arbitrarily late corrections, but depends on the source maintaining that column. Scenario 03 keeps `MAX(updated_at)` so both are visible, and the S3 examples combine the two with `GREATEST(updated_on, LEAST(...))`.

Note that Rill spells the strategy `partition_overwrite`; `partition_override` is not a valid value.

## Layout

Each source directory contains the same nine scenarios. Filenames omit the redundant source prefix because their parent directory already identifies the source; each YAML spec declares an explicit globally unique resource `name` so the complete Rill project remains valid.

| #   | Scenario                            | Primary features                                                                          |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| 00  | Full-refresh baseline               | Non-incremental materialization and a dev limit                                            |
| 01  | **Hourly partition overwrite with watermark** | **The recommended pattern: `partition_overwrite` + `patch` + watermark, one hour per partition** |
| 02  | Daily partition overwrite with watermark | The same recommended pattern at a daily grain                                          |
| 03  | Late hourly updates with merge      | `merge` by `unique_key` when no output column identifies a whole partition                 |
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
- `merge` updates matching rows and inserts new rows using `output.unique_key`. Use it when the output has no single column that identifies a complete partition. A unique key must be stable, non-null, and genuinely unique; a weak key can update the wrong row, leave duplicates, or produce nondeterministic results. A composite identity can be expressed as multiple key columns. Merge never deletes, so a row dropped from a reprocessed source window stays in the output.
- `append` is deliberately not demonstrated. It inserts without matching or deleting, so a rerun of the same input duplicates rows. Use `partition_overwrite` instead; it is idempotent even for data you believe is immutable.

## Watermarks and late data

`partitions_watermark` names a timestamp returned by the partition discovery query. The watermark is excluded from the partition identity. When its value advances, Rill marks that existing partition pending again.

- For warehouse sources, the discovery query returns `MAX(updated_at)` per day or hour and the model reloads the complete affected window.
- For S3, glob partition discovery already exposes each object's `updated_on`, so `partitions_watermark: updated_on` re-queues a prefix whose files were rewritten.

The watermark cannot be assigned the value `manual`; it is a column name, not an execution mode.

For sources whose updates can arrive after a long delay, expand the discovery query's lookback or remove it entirely. A bounded lookback controls source cost but is also the maximum lateness the model can notice automatically.

## Schema-change modes

- `patch` (recommended): adopt later definition changes without automatically rebuilding historical data. Existing rows retain their old shape or logic, so pair it with `partition_overwrite` and backfill the affected partitions explicitly when historical consistency matters.
- `reset`: automatically drop and recreate output after a definition change. This produces consistent history at the cost of a full source scan.

`change_mode: manual` also exists in Rill, but this gallery does not demonstrate it: it pauses reconciliation until an operator chooses a refresh, which is useful for approval gates but obscures the pattern the examples are teaching.

See [Model behavior and operator control](docs/model-behavior.md) for a focused comparison of watermarks, change modes, refresh schedules, incremental strategies, and partitions versus state.

## Running an example

Create a scratch Rill project containing only one connector and one model. This keeps unrelated models from scanning warehouses or producing missing-credential errors:

```bash
example_dir="$(mktemp -d /tmp/rill-model-example.XXXXXX)"
mkdir -p "$example_dir/connectors" "$example_dir/models"
cp rill.yaml .env.example "$example_dir/"
cp connectors/snowflake.yaml "$example_dir/connectors/"
cp models/snowflake/01_hourly_partition_overwrite_watermark.yaml "$example_dir/models/"
cd "$example_dir"
cp .env.example .env
# Populate SNOWFLAKE_DSN and adjust analytics.events if necessary.
# The cron is live; uncomment refresh.disable if you want to inspect the model without running it.
rill start .
```

Substitute the connector and model paths for BigQuery, ClickHouse, S3, or another scenario. Do not enable models in the repository root; it is intentionally kept as an inactive reference project.

Useful commands:

```bash
rill project partitions --local --model snowflake_01_hourly_partition_overwrite_watermark
rill project refresh --local --model snowflake_01_hourly_partition_overwrite_watermark
rill project refresh --local --model snowflake_01_hourly_partition_overwrite_watermark --full
# Copy a key from the partitions listing, then target only that partition:
rill project refresh --local --model snowflake_01_hourly_partition_overwrite_watermark --partition <partition-key>
```

## Validation

Run `./scripts/check_examples.sh`. It checks YAML parsing, unique resource names, the commented-out `refresh.disable` convention, source-specific connector names, the recommended-pattern properties on scenarios 01 and 02, the absence of `change_mode: manual` and `incremental_strategy: append`, the partitions-or-state split, retry behavior, and schema-hook intent. The checks are static; running a model still requires real credentials and an `analytics.events` table or Parquet prefix.

## Canonical references

- [Rill model runtime guidance](https://github.com/rilldata/rill/blob/main/runtime/ai/instructions/data/resources/model.md)
- [Model YAML reference](https://docs.rilldata.com/reference/project-files/models)
- [Partitioned models](https://docs.rilldata.com/developers/build/models/partitioned-models)
- [Incremental models](https://docs.rilldata.com/developers/build/models/incremental-models)
- [Connector YAML reference](https://docs.rilldata.com/reference/project-files/connectors)

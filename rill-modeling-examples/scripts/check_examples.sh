#!/usr/bin/env bash

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
clickhouse_dir="$project_dir/models/clickhouse"

fail() {
  echo "check_examples: $1" >&2
  exit 1
}

[[ -d "$clickhouse_dir" ]] || fail "missing models/clickhouse"

ruby -e '
  require "yaml"
  ARGV.each do |file|
    YAML.safe_load(File.read(file), [], [], false, filename: file)
  end
' "$project_dir/rill.yaml" "$project_dir"/connectors/*.yaml "$clickhouse_dir"/*.yaml \
  || fail "YAML parsing failed"

if rg -n "connector: duckdb|ClickHouse into a materialized DuckDB|ClickHouse-to-DuckDB" "$clickhouse_dir" "$project_dir/README.md"; then
  fail "found obsolete ClickHouse-to-DuckDB configuration or documentation"
fi

rg -q '^mode: readwrite$' "$project_dir/connectors/clickhouse.yaml" || fail "ClickHouse connector must be readwrite"

model_count=0
while IFS= read -r model; do
  model_count=$((model_count + 1))
  rg -q '^connector: clickhouse' "$model" || fail "$model must execute SQL in ClickHouse"
  rg -q 'FROM s3\(' "$model" || fail "$model must read Parquet through ClickHouse s3()"
  rg -q '^output:$' "$model" || fail "$model must define output properties"
  rg -q '^  connector: clickhouse$' "$model" || fail "$model must write to ClickHouse"
  rg -q '^  order_by:' "$model" || fail "$model must define output.order_by"
  rg -q '^  ttl:' "$model" || fail "$model must define output.ttl"
  rg -q '^  query_settings: use_structure_from_insertion_table_in_table_functions = 0$' "$model" \
    || fail "$model must infer the structure from S3 instead of the insertion table"
  rg -q '^  columns: \|' "$model" || fail "$model must define an explicit ClickHouse schema"
  rg -q 'INDEX idx_event_id' "$model" || fail "$model must define the event_id skipping index"
done < <(find "$clickhouse_dir" -maxdepth 1 -type f -name '*.yaml' | sort)

[[ "$model_count" -eq 9 ]] || fail "expected 9 ClickHouse model examples, found $model_count"

for scenario in 01_hourly_partition_overwrite_watermark 02_daily_partition_overwrite_watermark; do
  model="$clickhouse_dir/$scenario.yaml"
  rg -q '^incremental: true' "$model" || fail "$model must be incremental"
  rg -q '^    connector: s3$' "$model" || fail "$model must discover S3 partitions"
  rg -q '^  incremental_strategy: partition_overwrite' "$model" || fail "$model must use partition_overwrite"
  rg -q '^  partition_by:' "$model" || fail "$model must define the replacement and physical partition key"
done

ruby -e '
  require "yaml"
  ARGV.each do |file|
    model = YAML.safe_load(File.read(file), [], [], false, filename: file)
    raise "#{file}: missing prod.partitions" unless model.dig("prod", "partitions")
    raise "#{file}: missing prod.sql" unless model.dig("prod", "sql")
    raise "#{file}: prod.partitions drifted from the production default" unless model.dig("prod", "partitions") == model["partitions"]
    raise "#{file}: prod.sql drifted from the production default" unless model.dig("prod", "sql") == model["sql"]
  end
' "$clickhouse_dir/01_hourly_partition_overwrite_watermark.yaml" \
  "$clickhouse_dir/02_daily_partition_overwrite_watermark.yaml" \
  || fail "canonical models must define explicit production partitions and SQL"

hourly="$clickhouse_dir/01_hourly_partition_overwrite_watermark.yaml"
daily="$clickhouse_dir/02_daily_partition_overwrite_watermark.yaml"
rg -q '^  partition_by: event_hour$' "$hourly" || fail "hourly overwrite must replace hourly ClickHouse partitions"
rg -q '^  ttl: event_time \+ INTERVAL 30 DAY DELETE$' "$hourly" || fail "hourly partition count must be TTL-bounded"
rg -q '^  partition_by: event_date$' "$daily" || fail "daily overwrite must replace daily ClickHouse partitions"
rg -q "extract\('\{\{ \.partition\.uri \}\}', 'dt=" "$hourly" || fail "hourly partition key must come from the S3 path"
rg -q "extract\('\{\{ \.partition\.uri \}\}', 'dt=" "$daily" || fail "daily partition key must come from the S3 path"

for scenario in 04_schema_patch 05_schema_reset 06_hooks_retry; do
  model="$clickhouse_dir/$scenario.yaml"
  rg -q "extract\('\{\{ \.partition\.uri \}\}', 'dt=" "$model" || fail "$model partition key must come from the S3 path"
done

for scenario in 03_hourly_merge_late 08_state_incremental; do
  model="$clickhouse_dir/$scenario.yaml"
  rg -q '^  engine: ReplacingMergeTree\(updated_at\)$' "$model" || fail "$model must use a versioned ReplacingMergeTree"
done

rg -q "updated_at >= parseDateTime64BestEffort" "$clickhouse_dir/08_state_incremental.yaml" \
  || fail "state ingestion must overlap tied watermark values"
if rg -q '^  unique_key:' "$clickhouse_dir/03_hourly_merge_late.yaml" "$clickhouse_dir/08_state_incremental.yaml"; then
  fail "ClickHouse merge examples must not imply that unique_key controls ReplacingMergeTree deduplication"
fi

rg -q "ADD COLUMN IF NOT EXISTS traffic_source.*AFTER updated_at" "$clickhouse_dir/04_schema_patch.yaml" \
  || fail "schema patch must add traffic_source in SELECT insertion order"
rg -q "ADD COLUMN IF NOT EXISTS ingestion_source.*AFTER event_type" "$clickhouse_dir/06_hooks_retry.yaml" \
  || fail "hook example must add ingestion_source in SELECT insertion order"

echo "check_examples: all static checks passed"

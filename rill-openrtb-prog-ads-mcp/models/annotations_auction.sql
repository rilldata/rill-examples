-- Model SQL
-- Reference documentation: https://docs.rilldata.com/reference/project-files/models
-- @materialize: true

WITH min_max AS (
  SELECT 
    MIN(__time) AS min_time,
    MAX(__time) AS max_time,
    (MAX(__time) - MIN(__time)) AS total_span
  FROM auction_data_model
),
sequence AS (
  SELECT 
    min_time + ((total_span * i::DOUBLE) / 49) + ((random() - 0.5) * total_span * 0.02) AS time,
    i
  FROM min_max, range(50) t(i)
),
descriptions AS (
  SELECT description 
  FROM UNNEST([
    'Programmatic auction started',
    'Bid request sent to DSP',
    'Ad impression logged',
    'Auction timeout occurred',
    'Floor price applied',
    'Bid won by DSP A',
    'Creative served successfully',
    'Ad rendered on device',
    'Invalid traffic detected',
    'Ad click tracked',
    'Viewability threshold met',
    'Brand safety check passed',
    'Geo-targeting matched',
    'Device type classified',
    'Ad not rendered due to timeout',
    'Second price auction applied',
    'Ad slot refreshed',
    'Campaign budget depleted',
    'Frequency cap reached',
    'DSP throttled bid rate',
    'Publisher added new inventory',
    'SSP filtering low-value bids',
    'Demand spike observed',
    'Creative rejected by scanner',
    'Bid caching mechanism used',
    'No eligible bids',
    'Programmatic deal triggered',
    'PMP deal preference applied',
    'Dynamic price floor used',
    'Contextual signal evaluated',
    'Latency spike during bidding',
    'Outstream video ad served',
    'Ad slot collapsed',
    'Native ad rendered',
    'OpenRTB 2.5 used',
    'Header bidding enabled',
    'Ad verification passed',
    'Campaign pacing adjusted',
    'Click-through rate spike',
    'Device ID match successful',
    'Cross-device attribution fired',
    'Lookalike segment matched',
    'Audience extension applied',
    'Server-side auction triggered',
    'Bid shading applied',
    'DSP bidding aggressively',
    'Ad failed brand check',
    'Ad muted by user',
    'Impression fraud prevented',
    'Auction closed'
  ]) AS t(description)
),
annotations AS (
  SELECT 
    s.time, 
    d.description
  FROM sequence s
  JOIN (
    SELECT description, ROW_NUMBER() OVER () - 1 AS rn FROM descriptions
  ) d ON d.rn = s.i
)
SELECT 
  *, 
  --'day' as duration -- Allows you to floor a annotation to a specified duration
FROM annotations
ORDER BY time
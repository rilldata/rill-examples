-- @materialize: true
SELECT * FROM url('https://storage.googleapis.com/rilldata-public/auction_data.parquet', parquet)

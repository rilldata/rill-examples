import requests
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from google.cloud import storage

# Replace with your Triton Digital credentials
USERNAME = "your_username"
PASSWORD = "your_password"

# Triton Digital API Endpoints
AUTH_URL = "https://tap-api.tritondigital.com/login"
DATA_URL = "https://tap-api.tritondigital.com/your_endpoint"  # Replace with actual endpoint

# Google Cloud Storage (GCS) details
GCS_BUCKET_NAME = "your-bucket-name"
GCS_FILE_PATH = "triton_data.parquet"

def get_triton_data():
    """Fetch data from Triton Digital API."""
    # Authenticate and obtain token
    auth_response = requests.post(AUTH_URL, json={"username": USERNAME, "password": PASSWORD})
    auth_response.raise_for_status()
    token = auth_response.json().get("token")

    # Set headers for data request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(DATA_URL, headers=headers)
    response.raise_for_status()

    # Convert JSON response to Pandas DataFrame
    data = response.json()
    df = pd.DataFrame(data)

    return df

def upload_to_gcs(df, bucket_name, file_path):
    """Convert DataFrame to Parquet and upload to GCS."""
    # Convert DataFrame to Parquet format
    table = pa.Table.from_pandas(df)
    pq.write_table(table, "temp_data.parquet")

    # Upload Parquet file to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_filename("temp_data.parquet")

    print(f"File successfully uploaded to gs://{bucket_name}/{file_path}")

# Fetch data from Triton Digital and upload to GCS
df_triton = get_triton_data()
upload_to_gcs(df_triton, GCS_BUCKET_NAME, GCS_FILE_PATH)

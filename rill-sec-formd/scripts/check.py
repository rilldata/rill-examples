from google.cloud import storage
import pandas as pd
import io

# Initialize Google Cloud Storage client
client = storage.Client()
bucket_name = "medriscoll-rill"
prefix = "sec-form-d/"
bucket = client.bucket(bucket_name)

# List files in the bucket
blobs = bucket.list_blobs(prefix=prefix)

# Function to check and enforce column type for OVER100RECIPIENTFLAG
def enforce_boolean_column(blob):
    # Download the file as bytes and read it into a pandas dataframe
    content = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(content), sep='\t')
    
    # Check if the column exists
    if 'OVER100RECIPIENTFLAG' in df.columns:
        col_type = df['OVER100RECIPIENTFLAG'].dtype
        # Convert to BOOLEAN (0/1 or True/False) if it's not already BOOLEAN
        if col_type != 'bool':
            print(f"File {blob.name} has OVER100RECIPIENTFLAG as {col_type}. Converting to BOOLEAN.")
            # Convert VARCHAR or other types to BOOLEAN based on the values
            df['OVER100RECIPIENTFLAG'] = df['OVER100RECIPIENTFLAG'].apply(
                lambda x: True if str(x).strip().lower() in ['true', '1', 'yes'] else False
            )
            
            # Write the updated DataFrame back to GCS
            new_blob = bucket.blob(blob.name)
            new_content = df.to_csv(sep='\t', index=False)
            new_blob.upload_from_string(new_content)
            print(f"File {blob.name} has been updated with BOOLEAN type.")
        else:
            print(f"File {blob.name} already has OVER100RECIPIENTFLAG as BOOLEAN.")
    else:
        print(f"File {blob.name} does not contain the column OVER100RECIPIENTFLAG.")

# Iterate through the files and check each one
for blob in blobs:
    if blob.name.endswith('OFFERING.tsv'):
        enforce_boolean_column(blob)

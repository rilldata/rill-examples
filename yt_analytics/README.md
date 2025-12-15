# YouTube Analytics for Rill

A comprehensive YouTube Channel Analytics tool that extracts demographic, traffic, and performance data from your YouTube channel and uploads it to Google Cloud Storage for use in Rill dashboards.

## Overview

This project helps you:
- Extract detailed analytics from your YouTube channel
- Query viewer demographics (age, gender, geographic location)
- Analyze traffic sources and device usage
- Get per-video performance metrics
- Create video ID to title mappings
- Automatically upload results to Google Cloud Storage (gs://rilldata-public/yt_analytics)
- Visualize all data through interactive Rill dashboards

## Setup

### Prerequisites

- Python 3.7+
- A YouTube channel with YouTube Analytics API access
- Google Cloud Project with YouTube Analytics API and Cloud Storage enabled
- Service account JSON credentials for GCS uploads

### Installation

1. Install required Python packages:
```bash
cd scripts
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install xyz
```

2. Set up YouTube API authentication:
```bash
python yt_analytics.py
# This will prompt you to authenticate with Google and create a token.json file
```

3. Place your GCS service account credentials file in the scripts directory:
```bash
cp path/to/roy-endo-google-svc-acc.json scripts/
```

The credentials file should be a **Service Account JSON key** from Google Cloud Platform. To create one:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Service Accounts** (under IAM & Admin)
3. Create or select your service account
4. Go to **Keys** → **Add Key** → **Create new key**
5. Choose **JSON** format and download the file
6. Ensure the service account has these roles:
   - `roles/storage.admin` (for GCS bucket access)
   - `roles/iam.serviceAccountUser` (for API access)

The JSON file should contain fields like:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## Usage

### Basic Commands

**Get viewer age analytics:**
```bash
python yt_analytics.py --age --start-date 2024-01-01 --end-date 2024-12-31
```

**Get all analytics types:**
```bash
python yt_analytics.py --all --start-date 2024-06-01
```

**Get video-specific analytics:**
```bash
python yt_analytics.py --video --video-id dQw4w9WgXcQ --start-date 2024-12-01
```

**Get analytics for all channel videos:**
```bash
python yt_analytics.py --video --all-videos --max-videos 100
```

**Create video ID to title mapping:**
```bash
python yt_analytics.py --mapping --max-mapping-videos 500
```

**Upload to Google Cloud Storage:**
```bash
python yt_analytics.py --all --upload-gcs
```

### Advanced Options

#### Date Range Options
- `--start-date YYYY-MM-DD` - Start date for analytics (default: today)
- `--end-date YYYY-MM-DD` - End date for analytics (default: today)

#### Video Options
- `--video-id VIDEO_ID` - YouTube video ID for specific video analytics
- `--all-videos` - Get analytics for all channel videos
- `--max-videos N` - Maximum number of videos to analyze (default: 50)
- `--max-mapping-videos N` - Maximum videos for mapping (default: 1000)

#### Analytics Types
- `--age` - Viewer age demographics
- `--gender` - Viewer gender demographics
- `--geo` - Geographic/country analytics
- `--traffic` - Traffic source analytics
- `--device` - Device and OS analytics
- `--video` - Video-specific analytics
- `--all` - Run all analytics types

#### Custom Queries
```bash
python yt_analytics.py --custom \
  --dimensions ageGroup,gender \
  --measures views,estimatedMinutesWatched \
  --sort -views
```

- `--dimensions DIMS` - Comma-separated dimensions (e.g., ageGroup, gender, country)
- `--measures MEASURES` - Comma-separated measures (e.g., views, estimatedMinutesWatched)
- `--filters FILTER` - Filter string (e.g., video==VIDEO_ID)
- `--sort SORT` - Sort order (e.g., -views for descending)

#### Output & Upload Options
- `--output-dir DIR` - Base directory for saving CSV files (default: analytics)
- `--upload-gcs` - Automatically upload CSV files to Google Cloud Storage
- `--gcs-bucket BUCKET` - GCS bucket name (default: rilldata-public)
- `--gcs-prefix PREFIX` - GCS prefix/path within bucket (default: yt_analytics)
- `--service-account PATH` - Path to service account JSON file (default: roy-endo-google-svc-acc.json)

### Examples

**Complete weekly analytics with upload:**
```bash
python yt_analytics.py --all --start-date 2024-12-01 --upload-gcs
```

**Get geo and device analytics with custom output directory:**
```bash
python yt_analytics.py --geo --device --output-dir week_analytics
```

**Query specific video with multiple analytics:**
```bash
python yt_analytics.py --video --video-id dQw4w9WgXcQ --age --gender --geo
```

**Create mapping for first 1000 videos over a date range:**
```bash
python yt_analytics.py --mapping --start-date 2020-01-01 --end-date 2025-01-27 --max-mapping-videos 1000
```

## Output Structure

CSV files are organized by date and analytics type:

```
analytics/
├── YYYY/MM/DD/
│   ├── age_YYYY-MM-DD_YYYY-MM-DD.csv
│   ├── gender_YYYY-MM-DD_YYYY-MM-DD.csv
│   ├── geo_YYYY-MM-DD_YYYY-MM-DD.csv
│   ├── traffic_YYYY-MM-DD_YYYY-MM-DD.csv
│   └── VIDEO_ID/
│       └── analytics.csv
├── YYYY/
│   └── device_YYYY.csv
└── all-time/
    └── video_mapping.csv
```

## GCS Upload

All CSV files are automatically uploaded to:
```
gs://rilldata-public/yt_analytics/
```

The directory structure is preserved in GCS, so files maintain their organization.

## Rill Dashboards

The data feeds into several Rill dashboards:

- **Demographics Dashboard** - Age, gender, and geographic viewer data
- **Traffic Sources Dashboard** - How viewers discover your content
- **Device Analytics Dashboard** - Operating system and device type breakdowns
- **Video Performance Dashboard** - Per-video metrics and engagement
- **Video Mapping Dashboard** - Video ID to title reference with analytics

Source files are in the `sources/` directory:
- `__demographics_age.yaml` - Age analytics source
- `__demographics_gender.yaml` - Gender analytics source
- `__demographics_geo.yaml` - Geographic analytics source
- `__demographics_traffic.yaml` - Traffic source analytics source
- `__demographics_device.yaml` - Device analytics source
- `__metrics.yaml` - Video performance metrics source
- `video_mapping.yaml` - Video title mapping source

## Available Metrics

### Demographics Metrics
- `viewerPercentage` - Percentage of viewers in each demographic category

### Video Metrics
- `views` - Total video views
- `estimatedMinutesWatched` - Total estimated minutes watched
- `averageViewDuration` - Average view duration in seconds
- `averageViewPercentage` - Average percentage of video watched
- `likes` - Total likes
- `subscribersGained` - New subscriber count
- `subscribersLost` - Unsubscriber count
- `engagedViews` - Views that resulted in engagement

### Traffic Metrics
- `views` - Total views from each traffic source
- `estimatedMinutesWatched` - Watch time from each traffic source

## Authentication

The script uses OAuth 2.0 for YouTube API authentication. First run creates a `token.json` file with your credentials.

To re-authenticate:
```bash
# Remove the existing token
rm token.json
# Run the script again to trigger re-authentication
python yt_analytics.py --all
```

## Logging

All operations are logged to `youtube_analytics.log` for debugging and audit purposes.

## Troubleshooting

**"No channels found for authenticated user"**
- Ensure you're authenticated with an account that has a YouTube channel

**"Failed to upload to GCS"**
- Verify service account credentials are valid and have Cloud Storage write permissions
- Check that the bucket `rilldata-public` is accessible

**"API quota exceeded"**
- YouTube Analytics API has rate limits
- Wait a few hours before running again, or spread requests across multiple days

**Authentication token expired**
- Delete `token.json` and re-authenticate

## Support

For issues or questions, refer to:
- [YouTube Analytics API Documentation](https://developers.google.com/youtube/reporting/v1/reports)
- [Rill Documentation](https://docs.rilldata.com/)

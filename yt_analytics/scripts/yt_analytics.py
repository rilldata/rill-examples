#!/usr/bin/env python3
"""
YouTube Analytics - Simplified Weekly Version
Creates weekly analytics for:
- Per episode metrics
- Demographics  
- Video ID to title lookup
Uploads to rilldata-public/yt_analytics
"""

import os
import csv
import json
import argparse
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.cloud import storage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('youtube_analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# YouTube Analytics API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/devstorage.full_control'
]

def get_credentials():
    """Get authenticated credentials for YouTube APIs"""
    token_path = Path("token.json")
    creds = None

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            logger.warning(f"Could not load existing token: {e}")
            # Remove corrupted token
            if token_path.exists():
                token_path.unlink()
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Could not refresh token: {e}")
                # Remove expired token and re-authenticate
                if token_path.exists():
                    token_path.unlink()
                creds = None
        
        if not creds:
            logger.info("Starting new authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())
            logger.info("Authentication completed successfully")

    return creds

def clear_authentication():
    """Clear existing authentication token to force re-authentication"""
    token_path = Path("token.json")
    if token_path.exists():
        token_path.unlink()
        logger.info("Authentication token cleared. Re-authentication will be required on next run.")
        return True
    return False

def query_youtube_analytics(
    dimensions=None,
    measures=None,
    filters=None,
    sort=None,
    max_results=100,
    start_date=None,
    end_date=None,
    ids=None,
    service_account_path="roy-endo-google-svc-acc.json"
):
    """
    Query YouTube Analytics API with flexible parameters
    
    Args:
        dimensions (list): List of dimension names (e.g., ['video', 'country', 'deviceType'])
        measures (list): List of measure names (e.g., ['views', 'estimatedMinutesWatched', 'averageViewDuration'])
        filters (str): Filter string (e.g., 'video==VIDEO_ID')
        sort (str): Sort order (e.g., '-views' for descending, 'views' for ascending)
        max_results (int): Maximum number of results to return (default: 100)
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        ids (str): Channel or content owner ID (default: 'channel==MINE')
        service_account_path (str): Path to service account JSON file
    
    Returns:
        dict: API response data
    """
    try:
        # Get authenticated credentials
        creds = get_credentials()
        
        # Build the YouTube Analytics service
        analytics_service = build('youtubeAnalytics', 'v2', credentials=creds)
        
        # Set default values
        if ids is None:
            ids = 'channel==MINE'
        
        if start_date is None:
            start_date = (datetime.now()).strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Prepare the query parameters
        query_params = {
            'ids': ids,
            'startDate': start_date,
            'endDate': end_date,
            'maxResults': max_results
        }
        
        # Add optional parameters if provided
        if dimensions:
            query_params['dimensions'] = ','.join(dimensions)
        
        if measures:
            query_params['metrics'] = ','.join(measures)
        
        if filters:
            query_params['filters'] = filters
        
        if sort:
            query_params['sort'] = sort
        
        # Execute the query
        logger.info(f"Executing YouTube Analytics query with params: {query_params}")
        
        response = analytics_service.reports().query(**query_params).execute()
        
        logger.info(f"Query successful. Retrieved {len(response.get('rows', []))} rows")
        return response
        
    except Exception as e:
        logger.error(f"Error querying YouTube Analytics: {str(e)}")
        raise

def get_video_analytics(video_id, start_date=None, end_date=None):
    """
    Get analytics for a specific video
    
    Args:
        video_id (str): YouTube video ID
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Video analytics data
    """
    dimensions = ['video', 'day']
    measures = ['views', 'estimatedMinutesWatched', 'averageViewDuration', 'likes', 'dislikes', 'subscribersGained', 'subscribersLost', 'engagedViews']
    filters = f'video=={video_id}'
    sort = 'day'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        filters=filters,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def get_age_analytics(start_date=None, end_date=None):
    """
    Get viewer age analytics
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Age group analytics data
    """
    dimensions = ['ageGroup']
    measures = ['viewerPercentage']  # Only viewerPercentage is supported for demographics
    sort = '-viewerPercentage'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def get_gender_analytics(start_date=None, end_date=None):
    """
    Get viewer gender analytics
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Gender analytics data
    """
    dimensions = ['gender']
    measures = ['viewerPercentage']  # Only viewerPercentage is supported for demographics
    sort = '-viewerPercentage'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def get_geo_analytics(start_date=None, end_date=None):
    """
    Get geographic (country) analytics with performance metrics
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Geographic analytics data with performance metrics
    """
    # Limit date range to what YouTube Analytics API supports
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        days_diff = (end_obj - start_obj).days
        
        # If date range is too long, limit to last 365 days
        if days_diff > 365:
            logger.warning(f"Date range {days_diff} days is too long for YouTube Analytics API. Limiting to last 365 days.")
            start_date = (end_obj - timedelta(days=365)).strftime('%Y-%m-%d')
    
    dimensions = ['country']
    measures = ['views', 'estimatedMinutesWatched', 'averageViewDuration', 'averageViewPercentage', 'subscribersGained']
    sort = '-estimatedMinutesWatched'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def get_traffic_source_analytics(start_date=None, end_date=None):
    """
    Get traffic source analytics
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Traffic source analytics data
    """
    dimensions = ['insightTrafficSourceType']
    measures = ['views', 'estimatedMinutesWatched']
    sort = '-views'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def get_device_analytics(start_date=None, end_date=None):
    """
    Get device analytics (operating system and device type)
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format (if not provided, will use full year from start_date)
    
    Returns:
        dict: Device analytics data
    """
    # For device analytics, if end_date is not provided, set it to full year from start_date
    if start_date:
        start_year = datetime.strptime(start_date, '%Y-%m-%d').year
        end_date = f"{start_year}-12-31"
        start_date = f"{start_year}-01-01"
    
    dimensions = ['day', 'operatingSystem', 'deviceType']
    measures = ['views']
    sort = '-views'
    
    return query_youtube_analytics(
        dimensions=dimensions,
        measures=measures,
        sort=sort,
        start_date=start_date,
        end_date=end_date
    )

def save_analytics_to_csv(data, analytics_type, start_date, end_date, base_dir="analytics", video_id=None):
    """
    Save analytics data to CSV file in organized directory structure
    
    Args:
        data (dict): Analytics data from YouTube API
        analytics_type (str): Type of analytics (age, gender, geo, traffic, custom, video)
        start_date (str): Start date for filename
        end_date (str): End date for filename
        base_dir (str): Base directory for saving files
        video_id (str): Video ID for video analytics (creates unique folder)
    
    Returns:
        str: Path to saved CSV file
    """
    try:
        # Create directory structure: analytics/YYYY/MM/DD/
        date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        year_dir = str(date_obj.year)
        month_dir = f"{date_obj.month:02d}"
        day_dir = f"{date_obj.day:02d}"
        
        # Create full directory path
        if analytics_type == 'video' and video_id:
            # For video analytics: analytics/YYYY/MM/DD/VIDEO_ID/
            full_dir = Path(base_dir) / year_dir / month_dir / day_dir / video_id
        elif analytics_type == 'device':
            # For device analytics: analytics/YYYY/device/ (since it covers full year)
            start_year = datetime.strptime(start_date, '%Y-%m-%d').year
            full_dir = Path(base_dir) / str(start_year)
        elif analytics_type == 'mapping':
            # For mapping analytics: analytics/all-time/ (since it covers full date range)
            full_dir = Path(base_dir) / 'all-time'
        else:
            # For other analytics: analytics/YYYY/MM/DD/
            full_dir = Path(base_dir) / year_dir / month_dir / day_dir
        
        full_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if analytics_type == 'video' and video_id:
            # For video analytics: analytics.csv (in video ID folder)
            filename = "analytics.csv"
        elif analytics_type == 'device':
            # For device analytics: device_YYYY.csv (since it covers full year)
            start_year = datetime.strptime(start_date, '%Y-%m-%d').year
            filename = f"device_{start_year}.csv"
        elif analytics_type == 'mapping':
            # For mapping analytics: mapping_YYYY.csv (since it covers full date range)
            start_year = datetime.strptime(start_date, '%Y-%m-%d').year
            filename = f"mapping.csv"
        else:
            # For other analytics: type_startdate_enddate_timestamp.csv
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"{analytics_type}_{start_date}_{end_date}.csv"
        
        filepath = full_dir / filename
        
        # Extract headers and data
        headers = data.get('columnHeaders', [])
        rows = data.get('rows', [])
        
        if not headers or not rows:
            logger.warning(f"No data to save for {analytics_type}")
            return None
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            header_names = [h.get('name', '') for h in headers]
            writer.writerow(header_names)
            
            # Write data rows
            for row in rows:
                writer.writerow(row)
        
        logger.info(f"Saved {analytics_type} analytics to {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Failed to save {analytics_type} analytics to CSV: {e}")
        return None

def get_video_titles(video_ids):
    """
    Get video titles for a list of video IDs
    
    Args:
        video_ids (list): List of YouTube video IDs
    
    Returns:
        dict: Dictionary mapping video IDs to titles
    """
    try:
        # Get authenticated credentials
        creds = get_credentials()
        
        # Build the YouTube service
        youtube_service = build('youtube', 'v3', credentials=creds)
        
        video_titles = {}
        
        # Process videos in batches of 50 (YouTube API limit)
        batch_size = 50
        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i + batch_size]
            
            # Get video details
            videos_response = youtube_service.videos().list(
                part='id,snippet',
                id=','.join(batch)
            ).execute()
            
            # Extract video titles
            for video in videos_response.get('items', []):
                video_id = video['id']
                title = video['snippet']['title']
                video_titles[video_id] = title
                logger.info(f"Retrieved title for video {video_id}: {title[:50]}...")
        
        logger.info(f"Successfully retrieved titles for {len(video_titles)} videos")
        return video_titles
        
    except Exception as e:
        logger.error(f"Failed to get video titles: {e}")
        return {}

def create_video_mapping(start_date=None, end_date=None, max_videos=1000):
    """
    Create a comprehensive mapping of video IDs to titles with analytics data
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        max_videos (int): Maximum number of videos to process
    
    Returns:
        dict: Dictionary with video mapping and analytics summary
    """
    try:
        logger.info("Creating comprehensive video mapping...")
        
        # Get all video IDs from channel
        video_ids = get_channel_videos(max_videos)
        if not video_ids:
            logger.error("No videos found in channel")
            return {}
        
        # Get video titles
        video_titles = get_video_titles(video_ids)
        
        # Get analytics for each video
        video_analytics = {}
        for video_id in video_ids:
            try:
                analytics_data = get_video_analytics(video_id, start_date, end_date)
                if analytics_data and analytics_data.get('rows'):
                    # Extract key metrics
                    rows = analytics_data['rows']
                    total_views = sum(row[2] for row in rows if len(row) > 2)  # views column
                    total_watch_time = sum(row[3] for row in rows if len(row) > 3)  # watch time column
                    video_analytics[video_id] = {
                        'title': video_titles.get(video_id, 'Unknown Title'),
                        'total_views': total_views,
                        'total_watch_time': total_watch_time,
                        'data_points': len(rows)
                    }
                else:
                    video_analytics[video_id] = {
                        'title': video_titles.get(video_id, 'Unknown Title'),
                        'total_views': 0,
                        'total_watch_time': 0,
                        'data_points': 0
                    }
            except Exception as e:
                logger.warning(f"Failed to get analytics for video {video_id}: {e}")
                video_analytics[video_id] = {
                    'title': video_titles.get(video_id, 'Unknown Title'),
                    'total_views': 0,
                    'total_watch_time': 0,
                    'data_points': 0
                }
        
        logger.info(f"Created video mapping for {len(video_analytics)} videos")
        return video_analytics
        
    except Exception as e:
        logger.error(f"Failed to create video mapping: {e}")
        return {}

def save_video_mapping_to_csv(video_mapping, start_date, end_date, base_dir="analytics"):
    """
    Save video mapping to CSV file
    
    Args:
        video_mapping (dict): Video mapping data
        start_date (str): Start date for filename
        end_date (str): End date for filename
        base_dir (str): Base directory for saving files
    
    Returns:
        str: Path to saved CSV file
    """
    try:
        # Create directory structure: analytics/YYYY/ (since mapping covers full date range)
        date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        year_dir = str(date_obj.year)
        
        full_dir = Path(base_dir) / 'all-time'
        full_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"video_mapping.csv"
        filepath = full_dir / filename
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            writer.writerow(['Video ID', 'Title', 'Total Views', 'Total Watch Time (minutes)', 'Data Points'])
            
            # Write data rows
            for video_id, data in video_mapping.items():
                writer.writerow([
                    video_id,
                    data['title'],
                    data['total_views'],
                    data['total_watch_time'],
                    data['data_points']
                ])
        
        logger.info(f"Saved video mapping to {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Failed to save video mapping to CSV: {e}")
        return None

def get_channel_videos(max_results=50):
    """
    Get all videos from the authenticated channel
    
    Args:
        max_results (int): Maximum number of videos to retrieve
    
    Returns:
        list: List of video IDs
    """
    try:
        # Get authenticated credentials
        creds = get_credentials()
        
        # Build the YouTube service
        youtube_service = build('youtube', 'v3', credentials=creds)
        
        # Get channel ID for authenticated user
        channels_response = youtube_service.channels().list(
            part='id',
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            logger.error("No channels found for authenticated user")
            return []
        
        channel_id = channels_response['items'][0]['id']
        logger.info(f"Found channel ID: {channel_id}")
        
        # Get videos from the channel
        videos_response = youtube_service.search().list(
            part='id',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=max_results
        ).execute()
        
        video_ids = [item['id']['videoId'] for item in videos_response.get('items', [])]
        logger.info(f"Retrieved {len(video_ids)} video IDs from channel")
        
        return video_ids
        
    except Exception as e:
        logger.error(f"Failed to get channel videos: {e}")
        return []

def get_all_videos_analytics(start_date=None, end_date=None, max_videos=50):
    """
    Get analytics for all videos in the channel
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        max_videos (int): Maximum number of videos to analyze
    
    Returns:
        dict: Dictionary mapping video IDs to their analytics data
    """
    video_ids = get_channel_videos(max_videos)
    all_video_analytics = {}
    
    for video_id in video_ids:
        try:
            logger.info(f"Getting analytics for video: {video_id}")
            analytics_data = get_video_analytics(video_id, start_date, end_date)
            all_video_analytics[video_id] = analytics_data
        except Exception as e:
            logger.error(f"Failed to get analytics for video {video_id}: {e}")
            all_video_analytics[video_id] = None
    
    return all_video_analytics

def upload_to_gcs(local_file_path, gcs_bucket, gcs_prefix="rill_yt_test", service_account_path="roy-endo-google-svc-acc.json"):
    """
    Upload a file to Google Cloud Storage and remove local file if successful
    
    Args:
        local_file_path (str): Path to local file to upload
        gcs_bucket (str): GCS bucket name
        gcs_prefix (str): GCS prefix/path within bucket
        service_account_path (str): Path to service account JSON file
    
    Returns:
        str: GCS URI of uploaded file, or None if failed
    """
    try:
        # Load service account credentials directly for GCS
        from google.oauth2 import service_account
        
        creds = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/devstorage.full_control']
        )
        
        # Build the storage client
        storage_client = storage.Client(credentials=creds)
        bucket = storage_client.bucket(gcs_bucket)
        
        # Create GCS blob path
        file_name = Path(local_file_path).name
        gcs_blob_path = f"{gcs_prefix}/{file_name}"
        blob = bucket.blob(gcs_blob_path)
        
        # Upload the file
        blob.upload_from_filename(local_file_path)
        
        gcs_uri = f"gs://{gcs_bucket}/{gcs_blob_path}"
        logger.info(f"Successfully uploaded {local_file_path} to {gcs_uri}")
        
        # Remove local file after successful upload
        try:
            os.remove(local_file_path)
            logger.info(f"Removed local file: {local_file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove local file {local_file_path}: {e}")
        
        return gcs_uri
        
    except Exception as e:
        logger.error(f"Failed to upload {local_file_path} to GCS: {e}")
        return None

def upload_analytics_folder_to_gcs(analytics_dir, gcs_bucket, gcs_prefix="rill_yt_test", service_account_path="roy-endo-google-svc-acc.json"):
    """
    Upload entire analytics folder to Google Cloud Storage
    
    Args:
        analytics_dir (str): Local analytics directory path
        gcs_bucket (str): GCS bucket name
        gcs_prefix (str): GCS prefix/path within bucket
        service_account_path (str): Path to service account JSON file
    
    Returns:
        dict: Summary of upload results
    """
    try:
        analytics_path = Path(analytics_dir)
        if not analytics_path.exists():
            logger.error(f"Analytics directory {analytics_dir} does not exist")
            return {}
        
        # Find all CSV files
        csv_files = list(analytics_path.rglob("*.csv"))
        if not csv_files:
            logger.warning(f"No CSV files found in {analytics_dir}")
            return {}
        
        logger.info(f"Found {len(csv_files)} CSV files to upload")
        
        # Load service account credentials once for all uploads
        from google.oauth2 import service_account
        
        creds = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/devstorage.full_control']
        )
        
        storage_client = storage.Client(credentials=creds)
        bucket = storage_client.bucket(gcs_bucket)
        
        upload_results = {
            'successful': [],
            'failed': [],
            'total_files': len(csv_files)
        }
        
        # Upload each CSV file
        for csv_file in csv_files:
            try:
                # Create GCS path that preserves directory structure
                relative_path = csv_file.relative_to(analytics_path)
                gcs_path = f"{gcs_prefix}/{relative_path}"
                
                # Create blob and upload
                blob = bucket.blob(gcs_path)
                blob.upload_from_filename(str(csv_file))
                
                gcs_uri = f"gs://{gcs_bucket}/{gcs_path}"
                upload_results['successful'].append({
                    'local_file': str(csv_file),
                    'gcs_uri': gcs_uri
                })
                
                logger.info(f"Uploaded {csv_file.name} to {gcs_uri}")
                
                # Remove local file after successful upload
                try:
                    os.remove(csv_file)
                    logger.info(f"Removed local file: {csv_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove local file {csv_file}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to upload {csv_file}: {e}")
                upload_results['failed'].append({
                    'local_file': str(csv_file),
                    'error': str(e)
                })
        
        logger.info(f"Upload complete: {len(upload_results['successful'])} successful, {len(upload_results['failed'])} failed")
        return upload_results
        
    except Exception as e:
        logger.error(f"Failed to upload analytics folder: {e}")
        return {}

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='YouTube Analytics - Query YouTube channel analytics data and save to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yt_analytics.py --age --start-date 2024-01-01 --end-date 2024-12-31
  python yt_analytics.py --gender --geo --device --max-results 50
  python yt_analytics.py --all --start-date 2024-06-01
  python yt_analytics.py --custom --dimensions ageGroup,gender --measures views,estimatedMinutesWatched
  python yt_analytics.py --all --output-dir my_analytics
  python yt_analytics.py --video --video-id dQw4w9WgXcQ --start-date 2024-12-01
  python yt_analytics.py --video --video-id dQw4w9WgXcQ --age --gender --geo
  python yt_analytics.py --video --all-videos --max-videos 100
  python yt_analytics.py --video --all-videos --start-date 2024-12-01 --output-dir video_analytics
  python yt_analytics.py --mapping --max-mapping-videos 500
  python yt_analytics.py --mapping --start-date 2020-01-01 --end-date 2025-01-27
  python yt_analytics.py --all --upload-gcs
  python yt_analytics.py --geo --upload-gcs --gcs-bucket my-bucket --gcs-prefix my-prefix

CSV Output:
  Files are automatically saved to: analytics/YYYY/MM/DD/type_startdate_enddate_timestamp.csv
  Video analytics: analytics/YYYY/MM/DD/VIDEO_ID/analytics.csv
  Video mapping: analytics/YYYY/video_mapping_startdate_enddate.csv
  Use --output-dir to specify a different base directory

GCS Upload:
  Use --upload-gcs to automatically upload all CSV files to Google Cloud Storage
  Default bucket: ws1-listeningparty.rilldata.com/rill_yt_test
  Use --gcs-bucket and --gcs-prefix to customize the destination
        """
    )
    
    # Analytics type options
    parser.add_argument('--age', action='store_true', help='Get viewer age analytics')
    parser.add_argument('--gender', action='store_true', help='Get viewer gender analytics')
    parser.add_argument('--geo', action='store_true', help='Get geographic/country analytics')
    parser.add_argument('--traffic', action='store_true', help='Get traffic source analytics')
    parser.add_argument('--device', action='store_true', help='Get device analytics (OS and device type). If only start_date provided, will use full year range (YYYY-01-01 to YYYY-12-31)')
    parser.add_argument('--video', action='store_true', help='Get video-specific analytics')
    parser.add_argument('--all-videos', action='store_true', help='Get analytics for all videos in channel')
    parser.add_argument('--mapping', action='store_true', help='Create video ID to title mapping with analytics')
    parser.add_argument('--all', action='store_true', help='Get all analytics types')
    
    # Video-specific options
    parser.add_argument('--video-id', type=str, help='YouTube video ID for video analytics (required with --video)')
    parser.add_argument('--max-videos', type=int, default=50, help='Maximum number of videos to analyze (default: 50)')
    parser.add_argument('--max-mapping-videos', type=int, default=1000, help='Maximum videos for mapping (default: 1000)')
    
    # Custom query options
    parser.add_argument('--custom', action='store_true', help='Run custom analytics query')
    parser.add_argument('--dimensions', type=str, help='Comma-separated dimensions (e.g., ageGroup,gender)')
    parser.add_argument('--measures', type=str, help='Comma-separated measures (e.g., views,estimatedMinutesWatched)')
    parser.add_argument('--filters', type=str, help='Filter string (e.g., video==VIDEO_ID)')
    parser.add_argument('--sort', type=str, help='Sort order (e.g., -views)')
    
    # Date and result options
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-results', type=int, default=100, help='Maximum results (default: 100)')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='analytics', help='Base directory for saving CSV files (default: analytics)')
    
    # GCS upload options
    parser.add_argument('--upload-gcs', action='store_true', help='Upload CSV files to Google Cloud Storage')
    parser.add_argument('--gcs-bucket', type=str, default='ws1-listeningparty.rilldata.com', help='GCS bucket name (default: ws1-listeningparty.rilldata.com)')
    parser.add_argument('--gcs-prefix', type=str, default='rill_yt_test', help='GCS prefix/path within bucket (default: rill_yt_test)')
    
    # Authentication options
    parser.add_argument('--service-account', type=str, default='roy-endo-google-svc-acc.json', help='Path to service account JSON file (default: roy-endo-google-svc-acc.json)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no specific analytics type is selected, show help
    if not any([args.age, args.gender, args.geo, args.traffic, args.device, args.video, args.all_videos, args.mapping, args.all, args.custom]):
        parser.print_help()
        exit(1)
    
    # Validate video ID if video analytics is requested (but not for all-videos or mapping)
    if args.video and not args.video_id and not args.all_videos:
        print("ERROR: --video-id is required when using --video flag (unless using --all-videos)")
        print("Example: python yt_analytics.py --video --video-id dQw4w9WgXcQ")
        print("Example: python yt_analytics.py --video --all-videos")
        exit(1)
    
    # Start execution
    start_time = datetime.now()
    logger.info("Starting YouTube Analytics Project")
    print("=" * 60)
    print(f"YouTube Analytics Project - Started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Set default dates if not provided
    if not args.start_date:
        args.start_date = datetime.now().strftime('%Y-%m-%d')
    if not args.end_date:
        args.end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Date range: {args.start_date} to {args.end_date}")
    print(f"Max results: {args.max_results}")
    if args.video:
        if args.all_videos:
            print(f"Video mode: All videos (max: {args.max_videos})")
        else:
            print(f"Video ID: {args.video_id}")
    if args.mapping:
        print(f"Mapping mode: Creating video ID to title mapping (max: {args.max_mapping_videos} videos)")
    print("=" * 60)
    
    # Run selected analytics
    if args.all:
        print("Running ALL analytics types...")
        analytics_to_run = ['age', 'gender', 'geo', 'traffic', 'device']
    else:
        analytics_to_run = []
        if args.age: analytics_to_run.append('age')
        if args.gender: analytics_to_run.append('gender')
        if args.geo: analytics_to_run.append('geo')
        if args.traffic: analytics_to_run.append('traffic')
        if args.device: analytics_to_run.append('device')
        if args.video: analytics_to_run.append('video')
        if args.mapping: analytics_to_run.append('mapping')
    
    # Execute selected analytics
    for analytics_type in analytics_to_run:
        try:
            if analytics_type == 'age':
                logger.info("Fetching viewer age analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching viewer age analytics...")
                data = get_age_analytics(args.start_date, args.end_date)
                row_count = len(data.get('rows', []))
                logger.info(f"Successfully retrieved age data: {row_count} rows")
                print(f"SUCCESS: Retrieved age data: {row_count} rows")
                
                # Save age data
                save_path = save_analytics_to_csv(data, 'age', args.start_date, args.end_date, args.output_dir)
                if save_path:
                    print(f"SUCCESS: Age data saved to {save_path}")
                
            elif analytics_type == 'gender':
                logger.info("Fetching viewer gender analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching viewer gender analytics...")
                data = get_gender_analytics(args.start_date, args.end_date)
                row_count = len(data.get('rows', []))
                logger.info(f"Successfully retrieved gender data: {row_count} rows")
                print(f"SUCCESS: Retrieved gender data: {row_count} rows")
                
                # Save gender data
                save_path = save_analytics_to_csv(data, 'gender', args.start_date, args.end_date, args.output_dir)
                if save_path:
                    print(f"SUCCESS: Gender data saved to {save_path}")
                
            elif analytics_type == 'geo':
                logger.info("Fetching geographic (country) analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching geographic (country) analytics...")
                data = get_geo_analytics(args.start_date, args.end_date)
                row_count = len(data.get('rows', []))
                logger.info(f"Successfully retrieved geo data: {row_count} rows")
                print(f"SUCCESS: Retrieved geo data: {row_count} rows")
                
                # Save geo data
                save_path = save_analytics_to_csv(data, 'geo', args.start_date, args.end_date, args.output_dir)
                if save_path:
                    print(f"SUCCESS: Geo data saved to {save_path}")
                
            elif analytics_type == 'traffic':
                logger.info("Fetching traffic source analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching traffic source analytics...")
                data = get_traffic_source_analytics(args.start_date, args.end_date)
                row_count = len(data.get('rows', []))
                logger.info(f"Successfully retrieved traffic source data: {row_count} rows")
                print(f"SUCCESS: Retrieved traffic source data: {row_count} rows")
                
                # Save traffic data
                save_path = save_analytics_to_csv(data, 'traffic', args.start_date, args.end_date, args.output_dir)
                if save_path:
                    print(f"SUCCESS: Traffic data saved to {save_path}")
                
            elif analytics_type == 'device':
                logger.info("Fetching device analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching device analytics...")
                data = get_device_analytics(args.start_date, args.end_date)
                row_count = len(data.get('rows', []))
                logger.info(f"Successfully retrieved device data: {row_count} rows")
                print(f"SUCCESS: Retrieved device data: {row_count} rows")
                
                # Save device data
                save_path = save_analytics_to_csv(data, 'device', args.start_date, args.end_date, args.output_dir)
                if save_path:
                    print(f"SUCCESS: Device data saved to {save_path}")
                
            elif analytics_type == 'video':
                logger.info("Fetching video-specific analytics...")
                print(f"\n{len(analytics_to_run)}. Fetching video-specific analytics...")
                if args.all_videos:
                    all_videos_data = get_all_videos_analytics(args.start_date, args.end_date, args.max_videos)
                    logger.info(f"Successfully retrieved all video data: {len(all_videos_data)} videos")
                    print(f"SUCCESS: Retrieved all video data: {len(all_videos_data)} videos")
                    
                    # Save analytics for each video individually
                    saved_count = 0
                    failed_count = 0
                    for video_id, video_data in all_videos_data.items():
                        if video_data is not None:
                            # Debug: Check if video data has rows
                            rows = video_data.get('rows', [])
                            if not rows:
                                logger.warning(f"Video {video_id} has no rows of data")
                                failed_count += 1
                                continue
                                
                            try:
                                save_path = save_analytics_to_csv(video_data, 'video', args.start_date, args.end_date, args.output_dir, video_id)
                                if save_path:
                                    saved_count += 1
                                    logger.info(f"Saved analytics for video {video_id} ({len(rows)} rows)")
                                else:
                                    failed_count += 1
                                    logger.warning(f"Failed to save analytics for video {video_id}")
                            except Exception as e:
                                failed_count += 1
                                logger.error(f"Error saving analytics for video {video_id}: {e}")
                        else:
                            failed_count += 1
                            logger.warning(f"No analytics data available for video {video_id}")
                    
                    print(f"SUCCESS: Saved analytics for {saved_count} videos")
                    if failed_count > 0:
                        print(f"WARNING: Failed to save analytics for {failed_count} videos")
                        logger.warning(f"Failed to save analytics for {failed_count} videos")
                    
                else:
                    data = get_video_analytics(args.video_id, args.start_date, args.end_date)
                    row_count = len(data.get('rows', []))
                    logger.info(f"Successfully retrieved video data: {row_count} rows")
                    print(f"SUCCESS: Retrieved video data: {row_count} rows")
                    
                    # Save single video data
                    save_path = save_analytics_to_csv(data, 'video', args.start_date, args.end_date, args.output_dir, args.video_id)
                    if save_path:
                        print(f"SUCCESS: Video data saved to {save_path}")
                        
            elif analytics_type == 'mapping':
                logger.info("Creating video ID to title mapping...")
                print(f"\n{len(analytics_to_run)}. Creating video ID to title mapping...")
                
                video_mapping = create_video_mapping(args.start_date, args.end_date, args.max_mapping_videos)
                
                if video_mapping:
                    # Save video mapping to CSV
                    save_path = save_video_mapping_to_csv(video_mapping, args.start_date, args.end_date, args.output_dir)
                    if save_path:
                        print(f"SUCCESS: Video mapping saved to {save_path}")
                        print(f"SUCCESS: Created mapping for {len(video_mapping)} videos")
                        
                        # Show sample of mapping
                        print("\nSample video mapping:")
                        count = 0
                        for video_id, data in video_mapping.items():
                            if count < 5:  # Show first 5 videos
                                print(f"  {video_id}: {data['title'][:60]}...")
                                count += 1
                            else:
                                break
                        if len(video_mapping) > 5:
                            print(f"  ... and {len(video_mapping) - 5} more videos")
                else:
                    print("ERROR: Failed to create video mapping")
                    
        except Exception as e:
            logger.error(f"Failed to fetch {analytics_type} data: {e}")
            print(f"ERROR: Error fetching {analytics_type} data: {e}")
    
    # Handle custom query
    if args.custom:
        try:
            logger.info("Executing custom analytics query...")
            print(f"\nExecuting custom analytics query...")
            
            # Parse comma-separated strings
            dimensions = args.dimensions.split(',') if args.dimensions else None
            measures = args.measures.split(',') if args.measures else None
            
            data = query_youtube_analytics(
                dimensions=dimensions,
                measures=measures,
                filters=args.filters,
                sort=args.sort,
                max_results=args.max_results,
                start_date=args.start_date,
                end_date=args.end_date
            )
            
            row_count = len(data.get('rows', []))
            logger.info(f"Successfully executed custom query: {row_count} rows")
            print(f"SUCCESS: Custom query returned {row_count} rows")
            
            # Save custom query data
            save_path = save_analytics_to_csv(data, 'custom', args.start_date, args.end_date, args.output_dir)
            if save_path:
                print(f"SUCCESS: Custom query data saved to {save_path}")
                
        except Exception as e:
            logger.error(f"Failed to execute custom query: {e}")
            print(f"ERROR: Custom query failed: {e}")
    
    # Handle GCS upload
    if args.upload_gcs:
        try:
            logger.info("Attempting to upload analytics to GCS...")
            print(f"\nAttempting to upload analytics to GCS to {args.gcs_bucket}/{args.gcs_prefix}...")
            
            # Upload the entire output directory to GCS
            upload_results = upload_analytics_folder_to_gcs(args.output_dir, args.gcs_bucket, args.gcs_prefix, args.service_account)
            
            if upload_results:
                successful_count = len(upload_results['successful'])
                failed_count = len(upload_results['failed'])
                total_count = upload_results['total_files']
                
                print(f"SUCCESS: Uploaded {successful_count}/{total_count} files to GCS")
                
                if successful_count > 0:
                    print("\nSuccessfully uploaded files:")
                    for success_item in upload_results['successful'][:5]:  # Show first 5
                        print(f"  ✅ {success_item['gcs_uri']}")
                    if successful_count > 5:
                        print(f"  ... and {successful_count - 5} more files")
                
                if failed_count > 0:
                    print(f"\nWARNING: Failed to upload {failed_count} files:")
                    for failed_item in upload_results['failed'][:3]:  # Show first 3 failures
                        print(f"  ❌ {failed_item['local_file']}: {failed_item['error']}")
                    if failed_count > 3:
                        print(f"  ... and {failed_count - 3} more failures")
                        
            else:
                print("ERROR: Failed to upload analytics folder to GCS")
                
        except Exception as e:
            logger.error(f"Failed to upload analytics to GCS: {e}")
            print(f"ERROR: Failed to upload analytics to GCS: {e}")
    
    # Summary of saved files
    print("\n" + "=" * 60)
    print("CSV FILES SAVED:")
    print("=" * 60)
    
    # List all CSV files in the output directory
    output_path = Path(args.output_dir)
    if output_path.exists():
        csv_files = list(output_path.rglob("*.csv"))
        if csv_files:
            for csv_file in csv_files:
                # Get relative path from base directory
                rel_path = csv_file.relative_to(output_path)
                file_size = csv_file.stat().st_size
                print(f"📁 {rel_path} ({file_size} bytes)")
        else:
            print("No CSV files found in output directory")
    else:
        print(f"Output directory '{args.output_dir}' does not exist")
    
    print("=" * 60)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"YouTube Analytics Project completed in {duration.total_seconds():.2f} seconds")
    
    print("\n" + "=" * 60)
    print(f"Core YouTube Analytics Functions Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {duration.total_seconds():.2f} seconds")
    print("=" * 60)
    print("Available functions:")
    print("- get_age_analytics() - Viewer age breakdown")
    print("- get_gender_analytics() - Viewer gender breakdown") 
    print("- get_geo_analytics() - Geographic/country breakdown")
    print("- get_traffic_source_analytics() - How viewers find your content")
    print("- get_device_analytics() - Device and operating system breakdown")
    print("- get_video_analytics() - Video-specific analytics")
    print("- get_all_videos_analytics() - Analytics for all channel videos")
    print("- create_video_mapping() - Video ID to title mapping with analytics")
    print("- get_views_watchtime_analytics() - Views and watch time data")
    print("=" * 60)
    print(f"CSV files saved to: {args.output_dir}/")
    print("Log file: youtube_analytics.log")
    print("=" * 60)
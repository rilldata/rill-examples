#!/usr/bin/env python3
"""
YouTube Analytics Wrapper Script
Handles historical backfill and daily updates for YouTube analytics data collection.

Features:
- Historical backfill: Run analytics for a date range with daily granularity
- Daily updater: Run analytics for the current day or specified date
- Configurable date ranges and analytics types
- Progress tracking and error handling
- Resume capability for interrupted backfills
"""

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('yt_analytics_wrapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeAnalyticsWrapper:
    def __init__(self, script_path="yt_analytics.py", output_dir="analytics"):
        self.script_path = script_path
        self.output_dir = output_dir
        self.progress_file = "backfill_progress.json"
        
    def run_analytics_for_date(self, date, analytics_type="--all", additional_args=None):
        """
        Run the YouTube analytics script for a specific date
        
        Args:
            date (datetime): Date to run analytics for
            analytics_type (str): Type of analytics to run (default: --all)
            additional_args (list): Additional command line arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        date_str = date.strftime('%Y-%m-%d')
        
        # Build command
        cmd = [
            sys.executable, self.script_path,
            analytics_type,
            '--start-date', date_str,
            '--end-date', date_str,
            '--output-dir', self.output_dir
        ]
        
        # Add additional arguments if provided
        if additional_args:
            cmd.extend(additional_args)
        
        logger.info(f"Running analytics for {date_str}: {' '.join(cmd)}")
        print(f"🔄 Running analytics for {date_str}...")
        
        try:
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully completed analytics for {date_str}")
                print(f"✅ Completed analytics for {date_str}")
                return True
            else:
                logger.error(f"Failed to run analytics for {date_str}: {result.stderr}")
                print(f"❌ Failed analytics for {date_str}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout running analytics for {date_str}")
            print(f"⏰ Timeout running analytics for {date_str}")
            return False
        except Exception as e:
            logger.error(f"Error running analytics for {date_str}: {e}")
            print(f"💥 Error running analytics for {date_str}: {e}")
            return False
    
    def historical_backfill(self, start_date, end_date, analytics_type="--all", 
                          additional_args=None, resume=True):
        """
        Run historical backfill for a date range
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            analytics_type (str): Type of analytics to run
            additional_args (list): Additional command line arguments
            resume (bool): Whether to resume from previous progress
            
        Returns:
            dict: Summary of backfill results
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Calculate total days
        total_days = (end_dt - start_dt).days + 1
        current_date = start_dt
        
        # Load progress if resuming
        progress = self.load_progress(start_date, end_date) if resume else {}
        
        successful_dates = []
        failed_dates = []
        skipped_dates = []
        
        # Smart optimization: If running --all, run device analytics once for the entire range
        # and other analytics daily
        if analytics_type == "--all":
            print(f"🚀 Starting historical backfill from {start_date} to {end_date}")
            print(f"📅 Total days to process: {total_days}")
            print(f"🔧 Analytics type: {analytics_type}")
            print(f"💡 Smart optimization: Device analytics will run once, others daily")
            
            # First, run device analytics once for the entire range
            print(f"\n📱 Running device analytics once for entire range...")
            device_success = self.run_analytics_for_date(
                start_dt, 
                "--device", 
                additional_args
            )
            
            if device_success:
                print(f"✅ Device analytics completed successfully for entire range")
            else:
                print(f"❌ Device analytics failed for entire range")
            
            # Then run other analytics daily (excluding device since it's already done)
            print(f"\n📊 Running other analytics daily...")
            
            if resume and progress:
                print(f"📋 Resuming from previous progress: {len(progress.get('completed_dates', []))} dates already completed")
            
            day_count = 0
            
            while current_date <= end_dt:
                date_str = current_date.strftime('%Y-%m-%d')
                day_count += 1
                
                # Check if already completed
                if resume and date_str in progress.get('completed_dates', []):
                    print(f"⏭️  Skipping {date_str} (already completed)")
                    skipped_dates.append(date_str)
                    current_date += timedelta(days=1)
                    continue
                
                print(f"\n📊 Processing day {day_count}/{total_days}: {date_str}")
                
                # Run analytics for this date (excluding device by using --all and then removing device data)
                success = self.run_analytics_for_date(
                    current_date, 
                    "--all", 
                    additional_args
                )
                
                if success:
                    successful_dates.append(date_str)
                    # Update progress
                    self.update_progress(start_date, end_date, date_str)
                else:
                    failed_dates.append(date_str)
                
                # Small delay to avoid overwhelming the API
                time.sleep(2)
                
                current_date += timedelta(days=1)
        else:
            # Regular daily processing for specific analytics types
            print(f"🚀 Starting historical backfill from {start_date} to {end_date}")
            print(f"📅 Total days to process: {total_days}")
            print(f"🔧 Analytics type: {analytics_type}")
            
            if resume and progress:
                print(f"📋 Resuming from previous progress: {len(progress.get('completed_dates', []))} dates already completed")
            
            day_count = 0
            
            while current_date <= end_dt:
                date_str = current_date.strftime('%Y-%m-%d')
                day_count += 1
                
                # Check if already completed
                if resume and date_str in progress.get('completed_dates', []):
                    print(f"⏭️  Skipping {date_str} (already completed)")
                    skipped_dates.append(date_str)
                    current_date += timedelta(days=1)
                    continue
                
                print(f"\n📊 Processing day {day_count}/{total_days}: {date_str}")
                
                # Run analytics for this date
                success = self.run_analytics_for_date(
                    current_date, 
                    analytics_type, 
                    additional_args
                )
                
                if success:
                    successful_dates.append(date_str)
                    # Update progress
                    self.update_progress(start_date, end_date, date_str)
                else:
                    failed_dates.append(date_str)
                
                # Small delay to avoid overwhelming the API
                time.sleep(2)
                
                current_date += timedelta(days=1)
        
        # Summary
        print(f"\n🎯 Historical backfill completed!")
        print(f"✅ Successful: {len(successful_dates)} dates")
        print(f"❌ Failed: {len(failed_dates)} dates")
        print(f"⏭️  Skipped: {len(skipped_dates)} dates")
        
        if failed_dates:
            print(f"\n❌ Failed dates: {', '.join(failed_dates[:10])}")
            if len(failed_dates) > 10:
                print(f"   ... and {len(failed_dates) - 10} more")
        
        return {
            'total_days': total_days,
            'successful': len(successful_dates),
            'failed': len(failed_dates),
            'skipped': len(skipped_dates),
            'successful_dates': successful_dates,
            'failed_dates': failed_dates,
            'skipped_dates': skipped_dates
        }
    
    def daily_update(self, date=None, analytics_type="--all", additional_args=None):
        """
        Run daily update for a specific date or today
        
        Args:
            date (str): Date in YYYY-MM-DD format (default: today)
            analytics_type (str): Type of analytics to run
            additional_args (list): Additional command line arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        if date is None:
            target_date = datetime.now()
        else:
            target_date = datetime.strptime(date, '%Y-%m-%d')
        
        date_str = target_date.strftime('%Y-%m-%d')
        
        print(f"📅 Running daily update for {date_str}")
        
        success = self.run_analytics_for_date(
            target_date,
            analytics_type,
            additional_args
        )
        
        if success:
            print(f"✅ Daily update completed successfully for {date_str}")
        else:
            print(f"❌ Daily update failed for {date_str}")
        
        return success
    
    def load_progress(self, start_date, end_date):
        """Load progress from progress file"""
        if not os.path.exists(self.progress_file):
            return {}
        
        try:
            with open(self.progress_file, 'r') as f:
                progress_data = json.load(f)
            
            # Check if this is the same backfill job
            if (progress_data.get('start_date') == start_date and 
                progress_data.get('end_date') == end_date):
                return progress_data
            else:
                return {}
        except Exception as e:
            logger.warning(f"Could not load progress file: {e}")
            return {}
    
    def update_progress(self, start_date, end_date, completed_date):
        """Update progress file with completed date"""
        progress_data = self.load_progress(start_date, end_date)
        
        if not progress_data:
            progress_data = {
                'start_date': start_date,
                'end_date': end_date,
                'completed_dates': [],
                'last_updated': datetime.now().isoformat()
            }
        
        if completed_date not in progress_data['completed_dates']:
            progress_data['completed_dates'].append(completed_date)
            progress_data['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save progress file: {e}")
    
    def clear_progress(self):
        """Clear progress file"""
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
            print("🗑️  Progress file cleared")

def main():
    parser = argparse.ArgumentParser(
        description='YouTube Analytics Wrapper - Historical backfill and daily updates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear authentication token (standalone)
  python yt_analytics_wrapper.py --clear-auth
  
  # Historical backfill from 2020-01-01 to 2021-01-01
  python yt_analytics_wrapper.py --historical --start-date 2020-01-01 --end-date 2021-01-01
  
  # Daily update for today
  python yt_analytics_wrapper.py --daily
  
  # Daily update for specific date
  python yt_analytics_wrapper.py --daily --date 2024-12-25
  
  # Daily update with GCS upload
  python yt_analytics_wrapper.py --daily --upload
  
  # Historical backfill with custom analytics type
  python yt_analytics_wrapper.py --historical --start-date 2023-01-01 --end-date 2023-12-31 --analytics-type --device
  
  # Historical backfill with GCS upload
  python yt_analytics_wrapper.py --historical --start-date 2022-01-01 --end-date 2022-12-31 --upload
  
  # Clear progress and start fresh
  python yt_analytics_wrapper.py --historical --start-date 2020-01-01 --end-date 2021-01-01 --no-resume
  
  # Clear authentication and re-authenticate
  python yt_analytics_wrapper.py --clear-auth
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('--historical', action='store_true', help='Run historical backfill')
    mode_group.add_argument('--daily', action='store_true', help='Run daily update')
    
    # Date options
    parser.add_argument('--start-date', type=str, help='Start date for historical backfill (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for historical backfill (YYYY-MM-DD)')
    parser.add_argument('--date', type=str, help='Specific date for daily update (YYYY-MM-DD, default: today)')
    
    # Analytics options
    parser.add_argument('--analytics-type', type=str, default='--all', 
                       help='Analytics type to run (default: --all)')
    parser.add_argument('--additional-args', nargs='*', 
                       help='Additional arguments to pass to yt_analytics.py')
    
    # Upload options
    parser.add_argument('--upload', action='store_true', 
                       help='Upload CSV files to Google Cloud Storage (automatically adds --upload-gcs)')
    
    # Control options
    parser.add_argument('--no-resume', action='store_true', 
                       help='Do not resume from previous progress (start fresh)')
    parser.add_argument('--clear-progress', action='store_true', 
                       help='Clear progress file before starting')
    parser.add_argument('--clear-auth', action='store_true',
                       help='Clear authentication token to force re-authentication')
    parser.add_argument('--script-path', type=str, default='yt_analytics.py',
                       help='Path to yt_analytics.py script (default: yt_analytics.py)')
    parser.add_argument('--output-dir', type=str, default='analytics',
                       help='Output directory for analytics (default: analytics)')
    
    args = parser.parse_args()
    
    # Handle upload flag - automatically add --upload-gcs to additional args
    if args.upload:
        if args.additional_args is None:
            args.additional_args = []
        if '--upload-gcs' not in args.additional_args:
            args.additional_args.append('--upload-gcs')
        print(f"📤 Upload enabled: automatically adding --upload-gcs to arguments")
    
    # Validation
    if args.historical:
        if not args.start_date or not args.end_date:
            parser.error("--historical requires both --start-date and --end-date")
        
        try:
            start_dt = datetime.strptime(args.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(args.end_date, '%Y-%m-%d')
            if start_dt > end_dt:
                parser.error("Start date must be before end date")
        except ValueError:
            parser.error("Dates must be in YYYY-MM-DD format")
    
    # Check if any operation is requested
    if not any([args.historical, args.daily, args.clear_auth, args.clear_progress]):
        print("ℹ️  No operation specified. Use --help to see available options.")
        print("💡 Common operations:")
        print("   --clear-auth                    # Clear authentication token")
        print("   --historical --start-date X --end-date Y  # Historical backfill")
        print("   --daily                         # Daily update")
        parser.print_help()
        sys.exit(0)
    
    # Check if script exists
    if not os.path.exists(args.script_path):
        print(f"❌ Error: Script not found at {args.script_path}")
        print(f"   Please ensure {args.script_path} exists in the current directory")
        sys.exit(1)
    
    # Create wrapper instance
    wrapper = YouTubeAnalyticsWrapper(
        script_path=args.script_path,
        output_dir=args.output_dir
    )
    
    # Clear progress if requested
    if args.clear_progress:
        wrapper.clear_progress()
    
    try:
        # Handle utility operations first
        if args.clear_auth or args.clear_progress:
            if args.clear_auth:
                print("🔐 Clearing authentication token...")
                try:
                    # Import the clear_authentication function from the main script
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("yt_analytics", args.script_path)
                    yt_analytics_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(yt_analytics_module)
                    
                    if hasattr(yt_analytics_module, 'clear_authentication'):
                        yt_analytics_module.clear_authentication()
                        print("✅ Authentication token cleared successfully")
                    else:
                        print("⚠️  clear_authentication function not found in script")
                except Exception as e:
                    print(f"❌ Failed to clear authentication: {e}")
                    print("💡 You can manually delete the token.json file to clear authentication")
            
            if args.clear_progress:
                wrapper.clear_progress()
            
            # If only utility operations were requested, exit here
            if not args.historical and not args.daily:
                print("✅ Utility operations completed")
                print("💡 You can now run your analytics commands with fresh authentication")
                return
        
        # Handle analytics operations
        if args.historical:
            print("🚀 Starting historical backfill...")
            print(f"📅 Date range: {args.start_date} to {args.end_date}")
            print(f"🔧 Analytics type: {args.analytics_type}")
            
            if args.additional_args:
                print(f"⚙️  Additional args: {' '.join(args.additional_args)}")
            
            print(f"📁 Output directory: {args.output_dir}")
            print(f"📋 Resume from progress: {not args.no_resume}")
            print()
            
            # Calculate estimated time
            start_dt = datetime.strptime(args.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(args.end_date, '%Y-%m-%d')
            total_days = (end_dt - start_dt).days + 1
            estimated_minutes = total_days * 2  # Rough estimate: 2 minutes per day
            
            print(f"⏱️  Estimated time: {estimated_minutes} minutes ({estimated_minutes/60:.1f} hours)")
            print()
            
            # Run historical backfill
            result = wrapper.historical_backfill(
                start_date=args.start_date,
                end_date=args.end_date,
                analytics_type=args.analytics_type,
                additional_args=args.additional_args,
                resume=not args.no_resume
            )
            
            print(f"\n🎯 Historical backfill completed!")
            print(f"📊 Summary: {result['successful']}/{result['total_days']} days successful")
            
        elif args.daily:
            print("📅 Starting daily update...")
            
            result = wrapper.daily_update(
                date=args.date,
                analytics_type=args.analytics_type,
                additional_args=args.additional_args
            )
            
            if result:
                print("✅ Daily update completed successfully!")
            else:
                print("❌ Daily update failed!")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

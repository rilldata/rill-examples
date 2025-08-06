import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fill_missing_dates(input_file="treasury_exchange_rates_2001_present.csv"):
    """
    Read the CSV file and fill missing dates with the last known exchange rate
    for each country-currency combination.
    """
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Convert record_date to datetime
    df['record_date'] = pd.to_datetime(df['record_date'])
    
    print(f"Original dataset has {len(df)} rows")
    print(f"Date range: {df['record_date'].min()} to {df['record_date'].max()}")
    
    # Get unique country-currency combinations
    country_currency_combos = df[['country', 'currency']].drop_duplicates()
    print(f"Found {len(country_currency_combos)} unique country-currency combinations")
    
    # Create a complete date range from min date to today
    min_date = df['record_date'].min()
    max_date = datetime.now().date()  # Use today's date
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    print(f"Creating complete date range from {min_date} to {max_date} ({len(all_dates)} days)")
    
    # Create a complete dataset with all dates for all country-currency combinations
    complete_data = []
    
    for _, combo in country_currency_combos.iterrows():
        country = combo['country']
        currency = combo['currency']
        
        # Get data for this country-currency combination
        combo_data = df[(df['country'] == country) & (df['currency'] == currency)].copy()
        
        # Create a complete date range for this combination
        combo_dates = pd.DataFrame({'record_date': all_dates})
        combo_dates['country'] = country
        combo_dates['currency'] = currency
        
        # Merge with existing data
        merged = pd.merge(combo_dates, combo_data, 
                         on=['record_date', 'country', 'currency'], 
                         how='left')
        
        # Forward fill missing values (use last known exchange rate)
        merged = merged.sort_values('record_date')
        merged['exchange_rate'] = merged['exchange_rate'].ffill()
        merged['country_currency_desc'] = merged['country_currency_desc'].ffill()
        
        # Remove rows where we couldn't fill the exchange rate (before first known date)
        merged = merged.dropna(subset=['exchange_rate'])
        
        complete_data.append(merged)
    
    # Combine all data
    filled_df = pd.concat(complete_data, ignore_index=True)
    
    print(f"Filled dataset has {len(filled_df)} rows")
    print(f"Added {len(filled_df) - len(df)} rows with filled exchange rates")
    
    # Save the filled dataset
    output_file = "treasury_exchange_rates_filled.csv"
    filled_df.to_csv(output_file, index=False)
    print(f"Saved filled dataset to {output_file}")
    
    # Show some statistics
    print("\nStatistics:")
    print(f"Original unique dates: {df['record_date'].nunique()}")
    print(f"Filled unique dates: {filled_df['record_date'].nunique()}")
    print(f"Original unique country-currency pairs: {df[['country', 'currency']].drop_duplicates().shape[0]}")
    print(f"Filled unique country-currency pairs: {filled_df[['country', 'currency']].drop_duplicates().shape[0]}")
    
    return filled_df

if __name__ == "__main__":
    filled_data = fill_missing_dates() 
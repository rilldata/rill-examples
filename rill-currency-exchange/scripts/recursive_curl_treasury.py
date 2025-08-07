import requests
import pandas as pd
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import json

BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
ENDPOINT = "v1/accounting/od/rates_of_exchange"
FULL_ENDPOINT = BASE_URL + ENDPOINT
PARAMS = {
    "fields": "country,currency,country_currency_desc,exchange_rate,record_date",
    "filter": "record_date:gte:2001-03-31",
    "page[size]": 1000
}

def fetch_api_data():
    """Fetch all pages from the API starting March 31, 2001."""
    all_data = []
    url = FULL_ENDPOINT
    params = PARAMS.copy()

    while url:
        print(f"Fetching: {url}")
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        json_data = resp.json()
        all_data.extend(json_data.get("data", []))

        next_link = json_data.get("links", {}).get("next")
        if next_link:
            if next_link.startswith("http"):
                # Absolute URL
                url = next_link
                params = {}
            else:
                # Relative query string - append to base URL
                if next_link.startswith("&"):
                    # Remove the leading & and append to base URL
                    url = FULL_ENDPOINT + "?" + next_link[1:]
                else:
                    url = FULL_ENDPOINT + next_link
                params = {}
        else:
            url = None

    df_api = pd.DataFrame(all_data)
    print(f"Fetched {len(df_api)} rows from API.")
    return df_api

if __name__ == "__main__":
    df = fetch_api_data()
    output_file = "treasury_exchange_rates_2001_present.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved dataset to {output_file}")

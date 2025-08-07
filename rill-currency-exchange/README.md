## Rill Demo Currency Project

In this project, we are calculating the equivalent USD costs for motor vehicle imports across the globe. Given how flucuating the currency exchange rate is, instead of using a flat table of couuntry amd rate. We also add date which is extracted from the [US Treasury API](https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/treasury-reporting-rates-of-exchange)


### Prerequisites

Install Python and install the requirements.txt package.


### How to use:

A sample script is provided in scripts/ to:
1. recursively curl the treasury API to get all dates from March 31, 2001 to present for all countries.
2. Since the data is not a complete time range, we run the `fill_missing_dates.py` to fill in the dates.


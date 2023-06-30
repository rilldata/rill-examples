# App Engagement

This is a demo project designed to illustrate how Rill can be used for use cases on troubleshooting app downloads and measuring user behavior. The dataset is from synthetic data spanning 5M+ total events for one month of data.

If you have added the full Rill Example project, run `rill start` from this directory to get started.

To run this example specifically:

```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-app-engagement
rill start
```

Start `rill start` from this directory to jump into this example.

Rill will build your project from data sources to dashboard and then launch in a new browser window.

## Overview
This dataset is an example of how an organization would use product analytics to understand user behavior. This specific data measures mobile app conversion data across the funnel, from view to download to sign-up. Typical users would include both marketing (spend improvement) and product (funnel optimization). Metrics include both summaries and conversion stats across key funnel steps.

## Data Model
In this dataset, you’ll see:

Key Dimensions:
 - App Version (internal SDK)
 - New vs. Existing for funnel step
   
Key Metrics: 
  - Page Views
  - Downloads
  - Site Conversion
  - Funnel Completion Rate

## Dashboard Details
Below are example analyses for ways marketers, mobile advertisers/gaming companies or product analytics teams might utilize this data:

  - Troubleshoot App Versions to see if a software update is impacting conversion
  - Evaluate drop-off at each funnel step, including New vs. Returning visitors 
  - Identify differences between different Carriers and Devices to see if one format is lagging versus another. Marry this data with marketing spend to improve campaign performance. 

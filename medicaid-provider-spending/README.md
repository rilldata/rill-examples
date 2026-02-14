# Medicaid Provider Spending

An interactive dashboard for exploring the [Medicaid provider spending dataset](https://opendata.hhs.gov/) open-sourced by HHS. Covers outpatient and professional claims from January 2018 through December 2024.

## Live dashboard

**[Explore the dashboard on Rill Cloud](https://ui.rilldata.com/demo/medicaid-provider-spending/explore/medicaid_provider_spending)**

You can also connect your AI tool (Claude, ChatGPT, Cursor, etc.) to the public MCP server:

```
https://api.rilldata.com/v1/orgs/demo/projects/medicaid-provider-spending/runtime/mcp
```

## What's in the dataset

The raw CMS data has NPI numbers and HCPCS billing codes but no human-readable descriptions. This project enriches it with:

- **Provider names and locations** from the CMS NPPES directory (maps NPI numbers to names, types, addresses, and specialties)
- **Procedure descriptions** from the HCPCS code set and RBCS service classifications (maps billing codes to readable descriptions and categories)
- **Exclusion flags** from the OIG LEIE list (identifies providers excluded from federal healthcare programs for fraud, abuse, or other misconduct)

## Data sources

| Model | Source | Description |
|---|---|---|
| `medicaid_provider_spending` | [HHS Open Data](https://opendata.hhs.gov/) (Parquet) | Raw claims: provider, procedure, month, payments |
| `npi_providers` | [CMS NPPES](https://download.cms.gov/nppes/NPI_Files.html) (CSV in ZIP) | Provider directory: names, types, locations |
| `hcpcs_codes` | [Tuva Project](https://tuvahealth.com/) (S3 CSV) | HCPCS procedure code descriptions |
| `rbcs_codes` | [Tuva Project](https://tuvahealth.com/) (S3 CSV) | RBCS service category classifications |
| `leie_exclusions` | [OIG HHS](https://oig.hhs.gov/exclusions/) (CSV) | Excluded provider list |

## Running locally

```bash
rill start medicaid-provider-spending
```

Dev limits apply automatically: 500K spending records, 10K NPI providers. Full data loads on deploy to Rill Cloud.

## Contributing

Ideas for additional enrichments? Open a PR or file an issue. Some possibilities:

- Taxonomy code descriptions (map specialty codes to readable names)
- Geographic enrichments (ZIP to county/region mapping)
- More comprehensive procedure classification for Medicaid-specific T-codes

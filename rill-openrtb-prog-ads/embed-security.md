# Test embedded dashboard security

The demo supports opt-in security scenarios through the signed `embed_security_mode` user attribute. The existing public demo remains accessible when that attribute is absent. Once a mode is present, an unknown mode, a non-string mode, or missing required attributes denies access.

| Mode | Required attributes | Bids metrics | Auction metrics |
| --- | --- | --- | --- |
| Attribute absent | None | Existing access and field rules | Existing access |
| `user_domain` | `domain: rilldata.com` | All permitted rows | All permitted rows |
| `advertiser` | Nonempty string `advertiser_name` | Matching advertiser rows | Denied: auctions have no advertiser dimension |
| `site_domain` | Nonempty string `domain` | Matching `app_site_domain` rows | Matching `app_site_domain` rows |
| `advertiser_domain` | Both advertiser and domain | Rows matching both | Denied: auctions have no advertiser dimension |

The policies run in the metrics views, so metrics API calls and dashboards inherit them. Site-domain filtering uses the underlying `app_site_domain` column; its bids dimension is named `sites_domain`. `user_domain` controls overall access based on the user's email domain, whereas `site_domain` filters dataset rows. These are separate scenarios.

SQL literals escape apostrophes. An explicitly empty mode does not fall back to public access. Existing email-based field exclusions remain in effect.

## Pass attributes from the embed backend

After merging and deploying this branch, send the following body to the project's iframe endpoint from a trusted backend:

```json
{
  "resource": "bids_explore",
  "type": "explore",
  "navigation": false,
  "external_user_id": "damedetrefle.com:grocery-outlet:viewer",
  "attributes": {
    "email": "viewer@damedetrefle.com",
    "domain": "damedetrefle.com",
    "admin": false,
    "embed_security_mode": "advertiser_domain",
    "advertiser_name": "Grocery Outlet"
  }
}
```

`Grocery Outlet` and `damedetrefle.com` are values in the demo dataset. The viewer email is a synthetic test identity. Change the mode and required attributes together to exercise another scenario. To test denial, use `user_domain` with `domain: outside.example`, or omit a required attribute from an explicit mode.

Use `attributes` rather than `user_email` when passing the mode: the iframe API permits only one identity source. The backend must derive and sign the attributes from its trusted identity context. Never accept an untrusted visitor's choice of mode as authorization. Use a separate stable external user ID for each security context.

Public access without a mode is intentional for this demo, not a complete multi-tenant security design. Production applications should enforce their default restrictions independently of an optional test selector.

## Verify before deployment

With Python 3 and the Rill CLI available, run from the repository root:

```sh
python3 rill-openrtb-prog-ads/tests/verify_embed_security.py
```

The script copies the exact security blocks from every metrics view into a temporary project with synthetic data and queries a local Rill backend. It checks unrestricted access, allowed and denied user domains, advertiser and site filters, combined filters, malformed and missing attributes, quoted values, SQL-injection attempts, and cross-metrics access. On branches with the existing email-based field exclusion, it checks that exclusion too.

The fixture verifies policy behavior, not the original project's full ingestion, charts, or cloud deployment. It does not use cloud credentials or modify a deployed project. The local attributes token is a Rill Developer testing mechanism and is not accepted by Rill Cloud.

You can also start this project locally and select the new identities in `mock_users`. Each mock identity selects one policy scenario.

## Policy reference

These policies follow the metrics-view security contract in `runtime-metrics-view.md` and `project-files-metrics-views.md`. See [Rill security policies](https://docs.rilldata.com/developers/build/metrics-view/security), [metrics view YAML](https://docs.rilldata.com/reference/project-files/metrics-views), and [iframe identity parameters](https://docs.rilldata.com/developers/embed/iframe).

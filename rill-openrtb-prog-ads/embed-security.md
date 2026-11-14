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

Each metrics view pairs its `access` condition with an explicit `deny` rule using the negated condition. An `access` condition only adds access, so on its own it cannot remove the access that a dashboard-scoped embed token grants to that dashboard's metrics view. The deny rule makes the denial hold for scoped and unscoped tokens alike.

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

## Open the AI sidebar

`dashboard_chat` falls back to `true`, which enables the dashboard AI sidebar in embeds. The default runtime behavior disables this capability for embedded users even when general project chat is enabled. The host page can then use `setAiPane(true)` and `setAiPane(false)` to open and close it. Those calls control visibility only: `getAiPane` reports the requested pane state, and the sidebar renders only when `dashboardChat` also resolves to true for that embed.

## Override feature flags per embed

Every flag under `features` keeps its fallback value unless the trusted embed backend signs a boolean `feature_<flag>` user attribute. The override applies only to that embed token. It does not change the project for anyone else. For example, these attributes disable exports and enable dashboard chat for one embed:

```json
{
  "email": "viewer@damedetrefle.com",
  "domain": "damedetrefle.com",
  "admin": false,
  "feature_exports": false,
  "feature_dashboard_chat": true
}
```

Only the boolean `true` (or the string `"true"`) enables a flag; any other value disables it. Rill still forces `dashboard_chat` and `chat_memory` off when `chat` is off. Overrides travel in `attributes`, so they cannot be combined with `user_email` or `user_id`.

Without an override, each flag resolves exactly as its previous untemplated value or runtime default did. Production fallbacks match the deployed v0.91.3 runtime defaults, so `alerts` and `reports` stay enabled for embeds. That runtime does not define `mcp_charts`, `embedded_bookmarks`, or `canvas_excel_export`, so they are not templated here. Because the fallbacks are written into `rill.yaml`, a later runtime default change will not apply to this project until the fallback is updated.

Feature flags mainly control the UI; backend permissions and security policies are enforced independently. Like the security mode, override attributes must be decided by a trusted backend, never by an untrusted visitor.

## Verify before deployment

With Python 3 and the Rill CLI available, run from the repository root:

```sh
python3 rill-openrtb-prog-ads/tests/verify_embed_security.py
```

The script copies the exact security blocks from every metrics view into a temporary project with synthetic data and queries a local Rill backend. It checks unrestricted access, allowed and denied user domains, advertiser and site filters, combined filters, malformed and missing attributes, quoted values, SQL-injection attempts, and cross-metrics access. On branches with the existing email-based field exclusion, it checks that exclusion too. Every case also runs against a copy of each metrics view with an extra allow rule, reproducing the grant in a dashboard-scoped Rill Cloud embed token, so denials must come from explicit deny rules. It also resolves every templated feature flag for embedded and signed-in identities, with and without signed overrides, including malformed override values.

The fixture verifies policy behavior, not the original project's full ingestion, charts, or cloud deployment. It does not use cloud credentials or modify a deployed project. The local attributes token is a Rill Developer testing mechanism and is not accepted by Rill Cloud.

You can also start this project locally and select the new identities in `mock_users`. Each mock identity selects one policy scenario.

## Policy reference

These policies follow the metrics-view security contract in `runtime-metrics-view.md` and `project-files-metrics-views.md`. See [Rill security policies](https://docs.rilldata.com/developers/build/metrics-view/security), [metrics view YAML](https://docs.rilldata.com/reference/project-files/metrics-views), and [iframe identity parameters](https://docs.rilldata.com/developers/embed/iframe).

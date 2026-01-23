# Rill Partner Filtered Dashboards

A demonstration project showcasing Rill's dashboard security policies. This project contains five metrics views, each demonstrating a different security pattern for controlling access to data.

## Security Policy Examples

### 1. Admin Access Only (`admin_access_only_metrics`)
Restricts dashboard access to admin users only.

```yaml
security:
  access: "{{ .user.admin }}"
```

**Use case:** Executive dashboards, sensitive financial data, or internal metrics that should only be visible to administrators.

### 2. Exclude Columns (`exclude_columns_metrics`)
Column-level security that hides specific dimensions from users outside a trusted domain.

```yaml
security:
  access: "true"
  exclude:
    - if: "'{{ .user.domain }}' != 'rilldata.com'"
      names:
        - company
        - plan_name
        - environment
        - pipeline
```

**Use case:** Sharing dashboards with external partners while hiding sensitive business dimensions like customer names or internal classifications.

### 3. Custom Attributes (`custom_attributes_metrics`)
Row-level filtering using custom user attributes defined in the identity provider.

```yaml
security:
  access: true
  row_filter: >
    company = '{{ .user.company }}' AND
    plan_name = '{{ .user.plan_name }}' AND
    location= '{{ .user.location}}'
```

**Use case:** Multi-tenant dashboards where each user should only see data matching their assigned attributes (e.g., their company, region, or department).

### 4. Mapped Row Access Policy (`mapped_row_access_policy_metrics`)
Row-level filtering using a mapping table that links user emails to allowed data.

```yaml
security:
  access: true
  row_filter: "company IN (SELECT company FROM mapping WHERE email = '{{ .user.email }}' )"
```

**Use case:** Partner portals where access permissions are managed via a database table, allowing flexible many-to-many relationships between users and data segments.

### 5. Restricted by Groups (`restricted_by_groups_metrics`)
Access restricted to users belonging to specific groups or with admin privileges.

```yaml
security:
  access: >
    {{ has "marketing" .user.groups }} OR {{ .user.admin }}
```

**Use case:** Department-specific dashboards where access is controlled by group membership in your identity provider.

## Project Structure

```
rill-partner-filtered-dashboards/
├── sources/
│   ├── margins_source.yaml    # Main data source
│   └── mapping.yaml           # User-to-company mapping table
├── metrics/
│   ├── admin_access_only_metrics.yaml
│   ├── exclude_columns_metrics.yaml
│   ├── custom_attributes_metrics.yaml
│   ├── mapped_row_access_policy_metrics.yaml
│   └── restricted_by_groups_metrics.yaml
├── dashboards/
│   ├── admin_access_only_metrics_explore.yaml
│   ├── exclude_columns_metrics_explore.yaml
│   ├── custom_attributes_metrics_explore.yaml
│   ├── mapped_row_access_policy_metrics_explore.yaml
│   └── restricted_by_groups_metrics_explore.yaml
└── connectors/
    └── duckdb.yaml
```

## Available User Attributes

The security policies in this project reference the following user attributes:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `.user.email` | User's email address | `user@company.com` |
| `.user.domain` | Domain from user's email | `company.com` |
| `.user.admin` | Boolean indicating admin status | `true` / `false` |
| `.user.groups` | List of groups the user belongs to | `["marketing", "sales"]` |
| `.user.company` | Custom attribute for company | `Acme Corp` |
| `.user.plan_name` | Custom attribute for plan | `Enterprise` |
| `.user.location` | Custom attribute for location | `US-West` |

## Learn More

- [Rill Security Policies Documentation](https://docs.rilldata.com/manage/security)
- [Row-Level Security](https://docs.rilldata.com/manage/security#row-level-security)
- [Column-Level Security](https://docs.rilldata.com/manage/security#column-level-security)

# Row Access Policies in Rill Cloud

In this demo project, we go over a few examples of typical usages of row access policies that our users have found useful and have requested.

To run this example specifically: 
```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-row-access-policies
rill start
```

## Testing row access policies
The row access policy can be tested in both Rill Developer and Rill Cloud via the [`view as` functionality](https://docs.rilldata.com/manage/security#testing-your-policies). If you are viewing this project in our demo page, you will not be able to use the "view as" feature as this is available for admins in Rill Cloud only. Please clone the project locally to try in Rill Developer.

### Metrics View Layer
1. **Basic row access policies.**

_metrics/basic_row_access_policy_metrics.yaml_

In our most basic example, we map an existing column in such as email_domain to the `{{ .user.domain }}` of the visting user. By default we provide a few [user attributes](https://docs.rilldata.com/manage/security#user-attributes) that can be used out of box in Rill Cloud.


Don't forget to add a clause in your row access policy to allow your admins or your company domain to see the full dashboard! 

2. **Mapping row access policies.**

_metrics/mapping_policy_metrics_domains.yaml_
_metrics/mapping_policy_metrics_product.yaml_

A common use case for our users is that a certain domain must be required to see several domains or a specific dimension value. In this case, you will need to create and manage a mapping file. In this case we created a simple .csv and mapped user domains to other domains and categories.


3. **Custom attributes used in row policies.**

_metrics/custom_attributes_metrics.yaml_

An advanced used case for row access policies is passing custom attributes into Rill and using this to filter the dashboard. 

Note custom attributes are only available in embed dasboards. 


### Explore Dashboard layer
_metrics/restricted_access_metrics.yaml_
_explore/restricted_access_explore.yaml_

In the explore dashboard, you can only set access true or false for the dashboards. This can be set up in either the metrics view layer or the explore layer. If set at the explore layer, the metrics view will still be accessible via APIs, etc. 
```
security:
  access: "{{ .user.admin }} OR '{{ .user.domain }}' == 'rilldata.com'"
  #access: true / false
```
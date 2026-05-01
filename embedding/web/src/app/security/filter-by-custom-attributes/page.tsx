"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const ATTRIBUTES = [
  { app_site_name: "FuboTV", pub_name: "Taboola" },
  { app_site_name: "Sling", pub_name: "Taboola" },
];

const FilterByCustomAttributesPage = () => {
  const org = "demo";
  const project = "rill-embed";
  const [attributes, setAttributes] = useState(ATTRIBUTES[0]);
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore_security_custom_attributes",
    attributes: attributes,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Filter by custom attributes</h2>

      <p>
        If the built-in user attributes based on <code>user_email</code> aren't
        enough, you can instead pass arbitrary custom attributes in the iframe
        request using the <code>attributes</code> property. Each key becomes a
        user attribute that the metrics view's security policy can reference.
      </p>

      <p>
        In this example, the metrics view has a security policy that applies a
        row filter based on custom <code>app_site_name</code> and{" "}
        <code>pub_name</code> user attributes. Switch between the presets below
        to change the values passed in the iframe request.
      </p>

      <CodeWithSource
        title="Metrics view security policy"
        code={`security:
  # Show the dashboard only to users with the "app_site_name" and "pub_name" custom attributes.
  access: '{{ hasKey .user "app_site_name" }} AND {{ hasKey .user "pub_name" }}'

  # Filter data by the user's custom attributes.
  row_filter: >
    app_site_name = '{{ .user.app_site_name }}'
    AND pub_name = '{{ .user.pub_name }}'`}
        sourceLabel="embedding/rill-project/metrics/auctions_security_custom_attributes.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/metrics/auctions_security_custom_attributes.yaml"
      />

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Select attributes
        </h3>
        <div className="flex gap-2">
          {ATTRIBUTES.map((attr) => (
            <button
              key={attr.app_site_name}
              onClick={() => setAttributes(attr)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border ${
                attributes === attr
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {attr.app_site_name} / {attr.pub_name}
            </button>
          ))}
        </div>
      </div>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/security/filter-by-custom-attributes/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/security/filter-by-custom-attributes/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default FilterByCustomAttributesPage;

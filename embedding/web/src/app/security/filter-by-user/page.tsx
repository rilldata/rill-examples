"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const USER_EMAILS = ["user1@fubo.tv", "user2@sling.com"];

const FilterByUserPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [userEmail, setUserEmail] = useState(USER_EMAILS[0]);
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore_security_domain",
    user_email: userEmail,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Filter by user</h2>

      <p>
        If your project uses Rill's security policies to filter dashboard
        access, you need to pass information about the end user in the iframe
        request. The simplest way to do this is using the{" "}
        <code>user_email</code> attribute.
      </p>

      <p>
        In this example, the metrics view has a security policy that limits
        access to users with a valid email domain, then applies a row filter to
        only show data for the user's email domain. Switch between the users
        below to change the value passed in the iframe request, the dashboard
        will reflect the matching domain.
      </p>

      <CodeWithSource
        title="Metrics view security policy"
        code={`security:
  # Show the dashboard only to users with a valid email domain.
  access: "{{ if .user.domain }} true {{ else }} false {{ end }}"

  # Filter data by the requesting user's email domain.
  row_filter: app_site_domain = '{{ .user.domain }}'`}
        sourceLabel="embedding/rill-project/metrics/auctions_security_domain.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/metrics/auctions_security_domain.yaml"
      />

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Select user
        </h3>
        <div className="flex gap-2">
          {USER_EMAILS.map((email) => (
            <button
              key={email}
              onClick={() => setUserEmail(email)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border ${
                userEmail === email
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {email}
            </button>
          ))}
        </div>
      </div>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/security/filter-by-user/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/security/filter-by-user/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default FilterByUserPage;

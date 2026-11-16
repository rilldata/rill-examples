"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import UserIdentityPicker, {
  DEMO_USER_IDS,
} from "@/components/UserIdentityPicker";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const FEATURES_YAML = `features:
  embedded_bookmarks: true`;

const BookmarksPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [userId, setUserId] = useState(DEMO_USER_IDS[0]);
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore",
    external_user_id: userId,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Bookmarks</h2>

      <p>
        Embed users can save the current state of a dashboard, such as its
        filters and time range, as a bookmark, and reopen it later. Bookmarks
        in embeds are disabled by default; enable them with the{" "}
        <code>embedded_bookmarks</code> feature flag in <code>rill.yaml</code>.
        Each bookmark is owned by the user who created it, so the iframe
        request must include an <code>external_user_id</code>.
      </p>

      <ul className="list-disc pl-6 space-y-1">
        <li>
          Bookmarks are managed from the bookmarks menu in the navigation bar,
          or the top-right corner of the dashboard when the bar is hidden.
        </li>
        <li>
          Only the owner can see their bookmarks. Embed users don't see the
          shared and home bookmarks that project admins create in Rill Cloud.
        </li>
        <li>
          When the iframe is limited to one dashboard with{" "}
          <code>resource</code>, as in this example, users can only create and
          see bookmarks for that dashboard.
        </li>
        <li>
          A bookmark only stores the dashboard state, so opening it still shows
          only the data the viewer can access through security policies.
        </li>
      </ul>

      <p>
        Apply some filters and save a bookmark as one user, then switch to the
        other to see that it isn't listed there.
      </p>

      <UserIdentityPicker userId={userId} onUserIdChange={setUserId} />

      <CodeWithSource
        title="Feature flag"
        code={FEATURES_YAML}
        sourceLabel="embedding/rill-project/rill.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/rill.yaml"
      />

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/user-features/bookmarks/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/user-features/bookmarks/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default BookmarksPage;

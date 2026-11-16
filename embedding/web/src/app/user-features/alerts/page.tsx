"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import OpenLinksNote from "@/components/OpenLinksNote";
import RillEmbed from "@/components/RillEmbed";
import UserIdentityPicker, {
  DEMO_USER_IDS,
} from "@/components/UserIdentityPicker";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const FEATURES_YAML = `features:
  alerts: true`;

const AlertsPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [userId, setUserId] = useState(DEMO_USER_IDS[0]);
  const [email, setEmail] = useState("");
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore",
    external_user_id: userId,
    ...(email ? { user_email: email } : {}),
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Alerts</h2>

      <p>
        Embed users can create alerts on the explore dashboards they can see,
        to get an email when a measure crosses a threshold. Alerts are disabled
        in embeds by default; enable them with the <code>alerts</code> feature
        flag in <code>rill.yaml</code>. Like reports, each alert is owned by the
        user who created it, so the iframe request must include an{" "}
        <code>external_user_id</code>.
      </p>

      <ul className="list-disc pl-6 space-y-1">
        <li>
          Create and manage alerts from the alert menu in the navigation bar
          while viewing an explore dashboard.
        </li>
        <li>
          Alerts are sent by email. Attaching the rows that triggered the alert
          is optional.
        </li>
        <li>
          Alerts run as the owner's latest identity, pause after 90 days
          without an iframe request for the owner, and can only be managed by
          the owner in the embed.
        </li>
      </ul>

      <p>
        Create an alert as one user, then switch to the other to see that it
        isn't listed there.
      </p>

      <UserIdentityPicker
        userId={userId}
        onUserIdChange={setUserId}
        email={email}
        onEmailChange={setEmail}
        emailHint="If set, passed as user_email and used as the default alert recipient. If it belongs to a Rill Cloud project member, their access applies."
      />

      <CodeWithSource
        title="Feature flag"
        code={FEATURES_YAML}
        sourceLabel="embedding/rill-project/rill.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/rill.yaml"
      />

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/user-features/alerts/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/user-features/alerts/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />

      <OpenLinksNote kind="alert" />
    </div>
  );
};

export default AlertsPage;

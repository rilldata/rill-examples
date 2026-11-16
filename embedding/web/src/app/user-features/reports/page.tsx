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
  reports: true`;

const ReportsPage = () => {
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
      <h2 className="text-2xl font-bold">Scheduled reports</h2>

      <p>
        Embed users can schedule email reports of the explore dashboards they
        can see. Reports are disabled in embeds by default; enable them with the{" "}
        <code>reports</code> feature flag in <code>rill.yaml</code>. Each report
        is owned by the user who created it, so the iframe request must include
        an <code>external_user_id</code>.
      </p>

      <ul className="list-disc pl-6 space-y-1">
        <li>
          Reports are sent by email with the export attached. If you pass{" "}
          <code>user_email</code>, it is the default recipient.
        </li>
        <li>
          Reports run as the owner's latest identity: the{" "}
          <code>user_email</code> or <code>attributes</code> from the most
          recent iframe request for that user.
        </li>
        <li>
          Reports pause if no iframe is requested for the owner for 90 days,
          and resume on the next request.
        </li>
        <li>Only the owner can manage their reports in the embed.</li>
      </ul>

      <p>
        Create a report as one user, then switch to the other to see that it
        isn't listed there.
      </p>

      <UserIdentityPicker
        userId={userId}
        onUserIdChange={setUserId}
        email={email}
        onEmailChange={setEmail}
        emailHint="If set, passed as user_email and used as the default report recipient. If it belongs to a Rill Cloud project member, their access applies."
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
        sourceLabel="embedding/web/src/app/user-features/reports/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/user-features/reports/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />

      <OpenLinksNote kind="report" />
    </div>
  );
};

export default ReportsPage;

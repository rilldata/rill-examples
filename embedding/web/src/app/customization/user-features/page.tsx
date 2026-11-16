"use client";

import { useState } from "react";
import Link from "next/link";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import UserIdentityPicker, {
  DEMO_USER_IDS,
} from "@/components/UserIdentityPicker";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const RILL_YAML = `features:
  # Disabled in embeds by default
  reports: true
  alerts: true
  embedded_bookmarks: true
  personal_canvases: true

# Page that opens the "Open" link in report and alert emails
embeds:
  open_url: https://rill-embedding-example.netlify.app/customization/user-features/open`;

const UserFeaturesPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [userId, setUserId] = useState(DEMO_USER_IDS[0]);
  const [email, setEmail] = useState("");
  // Personal canvases require navigation, so this embeds the whole project
  // rather than a single dashboard (no `resource`).
  const iframeBody = {
    navigation: true,
    external_user_id: userId,
    ...(email ? { user_email: email } : {}),
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">User features</h2>

      <p>
        Embed users can create their own scheduled reports, alerts, bookmarks
        and personal canvases. Enable each with a feature flag in{" "}
        <code>rill.yaml</code>, and pass an <code>external_user_id</code> in the
        iframe request: everything a user creates is owned by that ID and hidden
        from other users. Report and alert emails link to the{" "}
        <Link
          href="/customization/user-features/open"
          className="text-indigo-600 underline hover:text-indigo-800"
        >
          open page
        </Link>{" "}
        configured in <code>embeds.open_url</code>. See the{" "}
        <a
          href="https://docs.rilldata.com/developers/embed/iframe#user-identity-in-embeds"
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 underline hover:text-indigo-800"
        >
          embedding docs
        </a>{" "}
        for details.
      </p>

      <p>
        Create something as one user, then switch to the other to see that it
        isn't listed there.
      </p>

      <UserIdentityPicker
        userId={userId}
        onUserIdChange={setUserId}
        email={email}
        onEmailChange={setEmail}
        emailHint="If set, passed as user_email and used as the default report and alert recipient."
      />

      <CodeWithSource
        title="rill.yaml"
        code={RILL_YAML}
        sourceLabel="embedding/rill-project/rill.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/rill.yaml"
      />

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/customization/user-features/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/customization/user-features/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default UserFeaturesPage;

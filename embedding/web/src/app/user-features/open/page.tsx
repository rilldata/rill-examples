"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import UserIdentityPicker, {
  DEMO_USER_IDS,
} from "@/components/UserIdentityPicker";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

// Landing page for the "Open" link in report and alert emails. Rill builds the
// link from `embeds.open_url` in rill.yaml and appends a `rill_open` query
// parameter, which we forward to Rill unchanged as `open`.
const OpenEmbed = () => {
  const org = "demo";
  const project = "rill-embedding";
  const rillOpen = useSearchParams().get("rill_open");
  // This demo has no login, so the visitor picks which demo user they are. In
  // a real app, use the logged-in user's ID. Only the creator of the report or
  // alert can open it, so Rill rejects the request for any other user.
  const [userId, setUserId] = useState(DEMO_USER_IDS[0]);
  const [email, setEmail] = useState("");

  if (!rillOpen) {
    return (
      <p>
        This page opens dashboards from the <strong>Open</strong> link in
        report and alert emails, and expects a <code>rill_open</code> query
        parameter. To try it, create a{" "}
        <Link
          href="/user-features/reports"
          className="text-indigo-600 underline hover:text-indigo-800"
        >
          report
        </Link>{" "}
        or an{" "}
        <Link
          href="/user-features/alerts"
          className="text-indigo-600 underline hover:text-indigo-800"
        >
          alert
        </Link>{" "}
        and click the link in the email.
      </p>
    );
  }

  // Don't pass `resource`: Rill resolves the dashboard from `open`.
  const iframeBody = {
    open: rillOpen,
    external_user_id: userId,
    ...(email ? { user_email: email } : {}),
  };

  return (
    <>
      <p>
        Select the user who created the report or alert. In a real app, you'd
        pass the logged-in user's <code>external_user_id</code>; Rill only lets
        the creator open the link, so the request fails for other users.
      </p>

      <UserIdentityPicker
        userId={userId}
        onUserIdChange={setUserId}
        email={email}
        onEmailChange={setEmail}
        emailHint="If set, passed as user_email, as for the original iframe."
      />

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/user-features/open/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/user-features/open/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </>
  );
};

const OpenPage = () => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold">Open report or alert</h2>
    {/* useSearchParams requires a Suspense boundary for static builds. */}
    <Suspense fallback={<p>Loading...</p>}>
      <OpenEmbed />
    </Suspense>
  </div>
);

export default OpenPage;

"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import UserIdentityPicker, {
  DEMO_USER_IDS,
} from "@/components/UserIdentityPicker";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const FEATURES_YAML = `features:
  personal_canvases: true`;

const PersonalCanvasesPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [userId, setUserId] = useState(DEMO_USER_IDS[0]);
  // Personal canvases require navigation, so this embeds the whole project
  // rather than a single dashboard (no `resource`).
  const iframeBody = {
    navigation: true,
    external_user_id: userId,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Personal canvases</h2>

      <p>
        Embed users can create, edit and delete their own canvas dashboards,
        called personal canvases. Personal canvases are disabled by default;
        enable them with the <code>personal_canvases</code> feature flag in{" "}
        <code>rill.yaml</code>.
      </p>

      <ul className="list-disc pl-6 space-y-1">
        <li>
          The iframe request must include an <code>external_user_id</code> and
          set <code>navigation: true</code>. Iframes limited to a single
          dashboard don't show personal canvases.
        </li>
        <li>
          The navigation bar has a menu to open, create and delete personal
          canvases, and the project home page lists them above the other
          dashboards.
        </li>
        <li>
          Only the owner can see their personal canvases; they can't be shared
          with other embed users. Rill project admins can also access them.
        </li>
        <li>
          Like any dashboard, a personal canvas only shows the data the viewer
          can access through security policies.
        </li>
      </ul>

      <p>
        Create a personal canvas as one user, then switch to the other to see
        that it isn't listed there.
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
        sourceLabel="embedding/web/src/app/user-features/personal-canvases/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/user-features/personal-canvases/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default PersonalCanvasesPage;

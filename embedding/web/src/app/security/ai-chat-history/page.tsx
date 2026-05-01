"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const USER_IDS = ["user-alice-123", "user-bob-456"];

const AiChatHistoryPage = () => {
  const org = "demo";
  const project = "rill-embed";
  const [userId, setUserId] = useState(USER_IDS[0]);
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore",
    external_user_id: userId,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">AI chat history</h2>

      <p>
        Embedded dashboards can persist per-user state, currently AI chat
        history, by passing an <code>external_user_id</code> in the iframe
        request. If <code>external_user_id</code> is omitted, the embed has no
        persistent state and each new iframe starts fresh.
      </p>

      <p>
        In this example, two users have distinct <code>external_user_id</code>{" "}
        values. Switch between them to see how each user's AI chat history is
        preserved independently.
      </p>

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Select user
        </h3>
        <div className="flex gap-2">
          {USER_IDS.map((id) => (
            <button
              key={id}
              onClick={() => setUserId(id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border ${
                userId === id
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/security/ai-chat-history/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/security/ai-chat-history/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default AiChatHistoryPage;

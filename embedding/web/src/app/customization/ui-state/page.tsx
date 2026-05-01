"use client";

import { useEffect, useRef, useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const PRESETS = [
  {
    label: "Pivot view (24H)",
    value:
      "view=pivot&rows=app_site_domain&cols=device_os%2Crequests%2Cavg_bid_floor%2C1d_qps&sort_by=&table_mode=nest",
  },
  {
    label: "Chart view (24H)",
    value:
      "view=tdd&grain=day&compare_dim=auction_type&measure=avg_bid_floor&chart_type=line",
  },
  {
    label: "Compare by state (7D)",
    value:
      "view=table&tr=P7D&grain=day&compare_dim=device_state&f=device_state+IN+%28%27NY%27%2C%27NJ%27%2C%27ME%27%29",
  },
  {
    label: "Filter for 'FuboTV' (7D)",
    value:
      "tr=P7D&grain=day&compare_dim=auction_type&f=app_site_name+IN+('FuboTV')",
  },
  {
    label: "Filter for 'Solitaire' or 'Sharethrough' (7D)",
    value:
      "tr=P7D&grain=day&compare_dim=auction_type&f=app_site_name+IN+('Solitaire+Ⓨ','Sharethrough+Outstream+Video')",
  },
];

const UiStatePage = () => {
  const org = "demo";
  const project = "rill-embed";
  const iframeBody = { type: "explore", resource: "auctions_explore" };

  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [currentState, setCurrentState] = useState<string | null>(null);

  // Listens for responses from the dashboard.
  // getState replies with `{ state: "..." }`.
  // setState replies with a boolean.
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const result = event.data?.result;
      if (result && typeof result === "object") {
        setCurrentState((result as { state: string }).state);
      }
    };
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  // Sends a postMessage to the iframe with the given method (getState or setState) and optional params.
  const sendRequest = (method: string, params?: string) => {
    const id = Math.random().toString(36).slice(2, 11);
    iframeRef.current?.contentWindow?.postMessage(
      { id, method, ...(params && { params }) },
      "*",
    );
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">UI state</h2>

      <p>
        Once an iframe has loaded, the parent page can interact directly with it
        to get and set UI state (such as filters, time ranges, view types, and
        more). The Rill iframe exposes two functions for this,{" "}
        <code>setState</code> and <code>getState</code>, which you call using
        the <code>postMessage</code> JavaScript function. See the{" "}
        <a
          href="https://docs.rilldata.com/developers/embed/postmessage"
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 underline hover:text-indigo-800"
        >
          docs
        </a>
        , or this page's source, for details.
      </p>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/customization/ui-state/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/customization/ui-state/page.tsx"
      />

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">setState</h3>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button
              key={p.label}
              onClick={() => sendRequest("setState", p.value)}
              className="px-4 py-2 rounded-lg text-sm font-medium border bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">getState</h3>
        <button
          onClick={() => sendRequest("getState")}
          className="px-4 py-2 rounded-lg text-sm font-medium border bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
        >
          Get current state
        </button>
        {currentState && (
          <pre className="mt-3 bg-gray-100 text-gray-800 p-3 rounded font-mono text-xs overflow-x-auto border border-gray-200">
            {currentState}
          </pre>
        )}
      </div>

      <RillEmbed
        ref={iframeRef}
        org={org}
        project={project}
        body={iframeBody}
      />
    </div>
  );
};

export default UiStatePage;

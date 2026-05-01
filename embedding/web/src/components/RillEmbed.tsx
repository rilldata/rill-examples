"use client";

import { Ref, useEffect, useState } from "react";

interface RillEmbedProps {
  org: string;
  project: string;
  body: {
    resource?: string;
    attributes?: Record<string, string | number | boolean>;
    [key: string]: unknown;
  };
  // Optional ref to the underlying iframe element, e.g. for postMessage calls.
  ref?: Ref<HTMLIFrameElement>;
}

// RillEmbed fetches a short-lived iframe URL from the backend (which proxies
// the Rill API to keep the service token server-side) and renders the iframe.
const RillEmbed = ({ org, project, body, ref }: RillEmbedProps) => {
  const [iframeUrl, setIframeUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Stringify once so the effect's dep is a stable, value-comparable key.
  // Callers can pass a fresh `body` object on every render without looping.
  const requestBody = JSON.stringify({ org, project, body });

  // Fetches the iframe URL on mount and whenever the request changes.
  // The `cancelled` flag prevents a stale response from overwriting a newer
  // one if props change mid-flight. In a real app you'd typically delegate
  // this to a data-fetching library (e.g. SWR or TanStack Query), which
  // handles cancellation, deduping, and caching for you.
  useEffect(() => {
    let cancelled = false;

    fetch("/api/get-iframe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: requestBody,
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Failed to fetch iframe");
        if (!cancelled) setIframeUrl(data.iframeUrl);
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Unknown error");
      });

    return () => {
      cancelled = true;
    };
  }, [requestBody]);

  if (error) {
    return <p className="text-red-500">Error loading iframe: {error}</p>;
  }
  if (!iframeUrl) return <p>Loading...</p>;

  return (
    <iframe
      ref={ref}
      src={iframeUrl}
      width="100%"
      height="1000px"
      allowFullScreen
    />
  );
};

export default RillEmbed;

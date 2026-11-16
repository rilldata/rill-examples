import Link from "next/link";
import CodeWithSource from "@/components/CodeWithSource";

const OPEN_URL_YAML = `embeds:
  open_url: https://rill-embedding-example.netlify.app/user-features/open`;

// Explains the "Open" link that Rill adds to report and alert emails created
// from an embed. Shared by the reports and alerts example pages.
const OpenLinksNote = ({ kind }: { kind: "report" | "alert" }) => (
  <section className="space-y-3">
    <h3 className="text-lg font-semibold">Open links in emails</h3>
    <p>
      The emails don't link to Rill Cloud, since recipients may not have access
      to it. Instead, the {kind}'s creator gets an <strong>Open</strong> link
      to a page in this app, configured with <code>embeds.open_url</code> in{" "}
      <code>rill.yaml</code>. Rill appends a <code>rill_open</code> query
      parameter to that URL, and the{" "}
      <Link
        href="/user-features/open"
        className="text-indigo-600 underline hover:text-indigo-800"
      >
        open page
      </Link>{" "}
      forwards it to Rill to render the dashboard in the state captured by the{" "}
      {kind}.
    </p>
    <CodeWithSource
      title="rill.yaml"
      code={OPEN_URL_YAML}
      sourceLabel="embedding/rill-project/rill.yaml"
      sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/rill.yaml"
    />
  </section>
);

export default OpenLinksNote;

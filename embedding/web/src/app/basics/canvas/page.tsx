import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const CanvasPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const iframeBody = {
    type: "canvas",
    resource: "auctions_canvas",
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Canvas</h2>

      <p>Basic example of embedding a canvas dashboard.</p>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/basics/canvas/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/basics/canvas/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default CanvasPage;

import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const ExplorePage = () => {
  const org = "demo";
  const project = "rill-embed";
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore",
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Explore</h2>

      <p>Basic example of embedding an explore dashboard.</p>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/basics/explore/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/basics/explore/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default ExplorePage;

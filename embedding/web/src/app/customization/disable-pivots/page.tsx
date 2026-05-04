import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const DisablePivotsPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore_hide_pivot",
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Disable pivots</h2>

      <p>
        It is possible to disable the pivot table on an Explore dashboard. This
        is configured using the <code>embeds.hide_pivot</code> field in the
        explore dashboard YAML, not as part of the iframe request.
      </p>

      <CodeWithSource
        title="Dashboard YAML"
        code={`embeds:
  hide_pivot: true`}
        sourceLabel="embedding/rill-project/dashboards/auctions_explore_hide_pivot.yaml"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/rill-project/dashboards/auctions_explore_hide_pivot.yaml"
      />

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/customization/disable-pivots/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/customization/disable-pivots/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default DisablePivotsPage;

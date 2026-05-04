import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const NavigationPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const iframeBody = {
    navigation: true,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Navigation</h2>

      <p>
        When enabling navigation on your embed iframe, your users can navigate
        to other dashboards in the project. The dashboards they can navigate to
        can be limited using security policies (see the Security section of this
        page for more details).
      </p>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/basics/navigation/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/basics/navigation/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default NavigationPage;

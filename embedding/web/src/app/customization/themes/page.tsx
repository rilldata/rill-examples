"use client";

import { useState } from "react";
import CodeWithSource from "@/components/CodeWithSource";
import RillEmbed from "@/components/RillEmbed";
import { prettyIframeRequest } from "@/lib/prettyIframeRequest";

const THEMES = ["forest", "ocean", "sunset"];

const ThemesPage = () => {
  const org = "demo";
  const project = "rill-embedding";
  const [theme, setTheme] = useState(THEMES[0]);
  const iframeBody = {
    type: "explore",
    resource: "auctions_explore",
    theme,
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Themes</h2>

      <p>
        You can customize the appearance of your dashboards by defining custom
        theme YAML files in your Rill project. You can then apply these themes
        either directly in your dashboard's YAML file, or dynamically when
        generating an embed iframe. The example below shows how to apply themes
        dynamically by passing a theme name in the request when generating an
        iframe.
      </p>

      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Select theme
        </h3>
        <div className="flex gap-2">
          {THEMES.map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border ${
                theme === t
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Source:{" "}
          <a
            href={
              "https://github.com/rilldata/rill-examples/tree/main/embedding/rill-project/themes"
            }
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 underline hover:text-indigo-800"
          >
            embedding/rill-project/themes<span aria-hidden="true">↗</span>
          </a>
        </p>
      </div>

      <CodeWithSource
        title="Iframe request"
        code={prettyIframeRequest(org, project, iframeBody)}
        sourceLabel="embedding/web/src/app/customization/themes/page.tsx"
        sourceUrl="https://github.com/rilldata/rill-examples/blob/main/embedding/web/src/app/customization/themes/page.tsx"
      />

      <RillEmbed org={org} project={project} body={iframeBody} />
    </div>
  );
};

export default ThemesPage;

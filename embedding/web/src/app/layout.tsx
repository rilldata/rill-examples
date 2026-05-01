import "./globals.css";
import Link from "next/link";
import Logo from "@/components/Logo";

type NavItem = { href: string; label: string; external?: boolean };

const NAV_ITEMS: { header: string; items: NavItem[] }[] = [
  {
    header: "Basics",
    items: [
      { href: "/basics/explore", label: "Explore" },
      { href: "/basics/canvas", label: "Canvas" },
      { href: "/basics/navigation", label: "Navigation" },
    ],
  },
  {
    header: "Customization",
    items: [
      { href: "/customization/themes", label: "Themes" },
      { href: "/customization/disable-pivots", label: "Disable pivots" },
      { href: "/customization/ui-state", label: "UI state" },
    ],
  },
  {
    header: "Security",
    items: [
      { href: "/security/filter-by-user", label: "Filter by user" },
      {
        href: "/security/filter-by-custom-attributes",
        label: "Filter by custom attributes",
      },
      { href: "/security/ai-chat-history", label: "AI chat history" },
    ],
  },
  {
    header: "Reference",
    items: [
      {
        href: "https://docs.rilldata.com/developers/embed/iframe",
        label: "Embedding docs",
        external: true,
      },
      {
        href: "https://github.com/rilldata/rill-examples/tree/main/embedding/web",
        label: "Source code",
        external: true,
      },
    ],
  },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <title>Embedding Examples</title>
        <link rel="icon" href="/favicon.png" type="image/png" />
      </head>
      <body className="flex flex-col h-screen">
        <header className="bg-gray-100 text-gray-600 p-4 flex items-center space-x-4 border-b border-gray-300 ">
          <Link href="/" className="flex items-center space-x-2">
            <Logo />
          </Link>
          <h1 className="text-xl font-bold">Embedding Examples</h1>
        </header>
        <div className="flex flex-1">
          <nav className="w-64 bg-gray-100 border-r border-gray-300 p-4">
            {NAV_ITEMS.map((group, groupIndex) => (
              <div key={groupIndex} className="mb-4">
                <h2 className="text-gray-600 font-semibold mb-2">
                  {group.header}
                </h2>
                <div className="space-y-1">
                  {group.items.map((item) =>
                    item.external ? (
                      <a
                        key={item.href}
                        href={item.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-gray-200 text-gray-700"
                      >
                        {item.label}
                        <span
                          className="ml-1 text-xs text-gray-400"
                          aria-hidden="true"
                        >
                          ↗
                        </span>
                      </a>
                    ) : (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="block w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-gray-200 text-gray-700"
                      >
                        {item.label}
                      </Link>
                    ),
                  )}
                </div>
              </div>
            ))}
          </nav>
          <main className="flex-1 p-6 overflow-y-auto bg-white text-gray-800">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

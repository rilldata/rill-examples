export async function POST(req: Request) {
  const { org, project, body } = await req.json();

  const apiUrl = process.env.RILL_API_URL || "https://api.rilldata.com";
  const apiToken = process.env.RILL_SERVICE_TOKEN;

  const iframeUrl = `${apiUrl}/v1/orgs/${org}/projects/${project}/iframe`;

  const response = await fetch(iframeUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiToken}`,
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    return new Response(
      JSON.stringify({ error: data.message || "Failed to fetch iframe URL" }),
      { status: 500 },
    );
  }

  console.log("Received iframe URL:", JSON.stringify(data));

  return new Response(JSON.stringify({ iframeUrl: data.iframeSrc }));
}

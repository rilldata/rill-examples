// Formats an iframe API request as a printable HTTP request, for use in
// example pages. The shape matches the request that
// src/app/api/get-iframe/route.ts sends on the user's behalf.
export function prettyIframeRequest(
  org: string,
  project: string,
  body: unknown,
): string {
  return `POST https://api.rilldata.com/v1/orgs/${org}/projects/${project}/iframe

Authorization: Bearer <RILL_SERVICE_TOKEN>
Content-Type: application/json

${JSON.stringify(body, null, 2)}`;
}

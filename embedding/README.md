# Rill embedding example

This directory contains a complete example of embedding Rill dashboards in a web app. It has two parts:

- `rill-project/`: A Rill project defining dashboards that we'll be embedding, derived from the `rill-openrtb-prog-ads` example. Deployed to Rill Cloud at [ui.rilldata.com/demo/rill-embed](https://ui.rilldata.com/demo/rill-embed).
- `web/`: A Next.js app that demonstrates how to embed dashboards from the Rill project in a web app. Each page is a self-contained example covering a different aspect of the embedding capabilities.

## Links

- Web app on Netlify: [rill-embedding-example.netlify.app](https://rill-embedding-example.netlify.app/)
- Rill project on Rill Cloud: [ui.rilldata.com/demo/rill-embed](https://ui.rilldata.com/demo/rill-embed)
- Embedding documentation: [Embed Dashboards](https://docs.rilldata.com/developers/embed/iframe)

## Development (internal)

To develop the examples here, you must have a service token for the `demo/rill-embed` project on Rill Cloud.

To start a development server on `https://localhost:3000`:
```bash
cd web
RILL_SERVICE_TOKEN=<token> npm run dev
```

You can also run against another environment. For example, to target the `test` environment, run:
```bash
cd web
RILL_API_URL=https://api.rilldata.in RILL_SERVICE_TOKEN=<token> npm run dev
```

Note that the dev server runs over HTTPS (via Next.js's `--experimental-https`) because Rill's iframe's CSP does not allow embedding on non-HTTP websites.

### Testing

For convenience for (manual) testing of embedded dashboards, the example site has been deployed to Netlify for several environments:
- Production (uses `ui.rilldata.com/demo/rill-embed`): [rill-embedding-example.netlify.app](https://rill-embedding-example.netlify.app) [![Netlify Status](https://api.netlify.com/api/v1/badges/fb82df0c-351e-4b2b-9e7c-30ff5418ff79/deploy-status)](https://app.netlify.com/projects/rill-embedding-example/deploys)
- Test (uses `ui.rilldata.in/demo/rill-embed`): [rill-embedding-example-test.netlify.app]() [![Netlify Status](https://api.netlify.com/api/v1/badges/13cef1d4-e51b-404e-ac5f-e4f4e93808f3/deploy-status)](https://app.netlify.com/projects/rill-embed-test/deploys)

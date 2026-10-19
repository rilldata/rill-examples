# OpenRTB Programmatic Advertising with External MCP Servers

This is the [OpenRTB example](../rill-openrtb-prog-ads) with external MCP servers connected to Rill's AI assistant, so it can combine the bid stream data with Linear, Notion, Atlassian, GitHub, Hugging Face and Slack.

The servers are declared in `connectors/`. See [External MCP Servers](https://docs.rilldata.com/guide/ai/external-mcp) for the connector reference.

## Set up

Deploy the project to Rill Cloud:

```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-openrtb-prog-ads-mcp
rill deploy
```

- **Linear, Notion, Atlassian, Hugging Face** use per-user OAuth, which is available in Rill Cloud only. Each user clicks **Connect** in the chat's **External tools** menu.
- **GitHub** uses a personal access token. Set it before chatting:
  ```
  rill env set GITHUB_PAT <token>
  ```
- **Slack** uses per-user OAuth with a Slack app you create, because Slack doesn't support dynamic client registration:
  1. Create an app at [api.slack.com/apps](https://api.slack.com/apps) and keep it internal to your workspace. Slack only allows internal and Marketplace apps to use its MCP server.
  2. Under **OAuth & Permissions**, add the redirect URL `https://admin.rilldata.com/connectors/oauth/callback` and the user token scopes listed in `oauth_scopes` in `connectors/slack.yaml`.
  3. Under **Agents & AI Apps**, enable MCP access.
  4. Set the app's credentials from **Basic Information**:
     ```
     rill env set SLACK_MCP_CLIENT_ID <client id>
     rill env set SLACK_MCP_CLIENT_SECRET <client secret>
     ```

The Linear and Notion connectors expose only a subset of their tools through `security.include`, which keeps the assistant under the limit of 128 tools per request.

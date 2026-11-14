# 11 — Connectors: use, buy, build or host

A twin can only reach systems that have a connector (an MCP server). This page covers what exists today for our primary systems, how to add a connector that isn't in the directory, how to build or host our own, and how to review a connector before buying it.

## What exists for our systems

| System | Claude directory connector | Vendor's own remote MCP server | Identity | Can write? | Notes |
|---|---|---|---|---|---|
| **Salesforce** | ⚠ Not confirmed | Salesforce Hosted MCP Servers; Anthropic's Desktop guide gives the URL | Per user, via OAuth through an External Client App | Yes | ⚠ Enterprise Edition or higher (from a secondary source). Claude Tag uses an integration user. |
| **HubSpot** | ⚠ Not confirmed (page blocked) | `mcp.hubspot.com`; HubSpot's own Claude connectors run on it | Per user, via OAuth | Yes: contacts, companies, deals, tickets | ⚠ Required HubSpot tier not stated |
| **Microsoft Dynamics / Dataverse** | **None** | `{org}.crm.dynamics.com/api/mcp` | Custom Entra app with tenant admin consent | Yes: full read, write and delete | **Metered in Copilot Credits.** Claude Desktop and Claude Code are named as supported clients. |
| **Google Drive / Sheets** | **Yes**, built and run by Google | Google Workspace MCP servers (developer preview), e.g. a Sheets server that can write cells | Per user, via OAuth; an Owner adds it first on Team/Enterprise | Directory connector: reads, and creates files. Sheets MCP: edits values and formulas. | About 10 MB export cap. ⚠ Shared-drive support unconfirmed. |
| **SharePoint / OneDrive** | **Yes**, the Microsoft 365 connector (work accounts on Team/Enterprise) | Microsoft Work IQ MCP (⚠ support and licensing for non-Microsoft clients unconfirmed) | Per user (delegated); a Global Admin must consent for the tenant | Read by default; admins can turn on writes | |
| **Teams** | **Yes**, part of the Microsoft 365 connector | Work IQ (as above) | Same as SharePoint | Reads chat and calendar; admins can turn on sending | |
| **Slack** | **Yes** (Team/Enterprise; the Claude in Slack app must be installed first) | `mcp.slack.com/mcp` | OAuth with a client secret; Slack admin approval required | Yes: send and schedule messages, canvases, files | Claude Tag is the separate "Claude as a Slack teammate" product, acting as a shared identity |

Sources: [Directory](https://claude.com/docs/connectors/directory.md), [Salesforce on Desktop](https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md), [HubSpot MCP](https://developers.hubspot.com/docs/build-with-ai/remote-mcp-server), [Dataverse MCP](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp), [Dataverse with other clients](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp-other-clients), [Google Drive connector](https://claude.com/docs/connectors/google/drive.md), [Google Workspace MCP](https://developers.google.com/workspace/guides/configure-mcp-servers), [Microsoft 365 connector](https://claude.com/docs/connectors/microsoft/365.md), [Work IQ](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/work-iq/mcp/overview), [Slack MCP](https://docs.slack.dev/ai/slack-mcp-server.md), [Slack connector](https://claude.com/docs/connectors/slack/index.md), [Claude Tag connections](https://claude.com/docs/claude-tag/admins/connections/overview.md).

## Adding a connector that isn't in the directory

- **Who can add one:** on Team and Enterprise, an Owner (or, on Enterprise, a custom role with the Libraries permission). Members then sign in with their own accounts. Free plans get one custom connector.
- **Authentication:** OAuth is the default.
  - Anthropic recommends Claude's published client identity (CIMD). Dynamic client registration and your own client ID also work.
  - There is also "no sign-in", and static request headers (beta, limited).
  - **Authentication settings can't be changed after the connector is added.** Choose carefully.
- **Enterprise managed auth:** members connect automatically through your identity provider, for example Okta Cross App Access. A removed user keeps access until their current token expires.
- **Systems on a private network:** use an **MCP tunnel** (Enterprise, by request, research preview with no SLA, up to 10 tunnels, Cloudflare is a subprocessor). Or run Claude Code or the Agent SDK inside the network.
- **Admin restrictions:**
  - Set each tool to Always allow, Needs approval or Blocked.
  - In Claude Code, use managed MCP allow and deny lists; `disableClaudeAiConnectors` blocks claude.ai connectors.
  - Gap: connectors in Desktop local and SSH sessions arrive in a form managed MCP settings don't reach.
- **Claude Tag** uses remote servers only, declared in a plugin's `.mcp.json`, with a credential per server host (bearer, OAuth client credentials, JWT, or one admin's sign-in).

Sources: [Adding unlisted connectors](https://claude.com/docs/connectors/custom/add-unlisted.md), [Authentication](https://claude.com/docs/connectors/building/authentication.md), [Enterprise managed auth](https://claude.com/docs/connectors/building/enterprise-managed-auth.md), [MCP tunnels](https://claude.com/docs/connectors/mcp-tunnels/overview.md), [Claude Code MCP](https://code.claude.com/docs/en/mcp.md), [Managed MCP](https://code.claude.com/docs/en/managed-mcp.md), [Claude Tag custom connections](https://claude.com/docs/claude-tag/admins/connections/custom.md).

## Building our own MCP server

**Protocol requirements (MCP spec):**

- OAuth 2.1 with PKCE and protected resource metadata.
- The server must check that each token was issued *for it*, and must never pass the user's token through to upstream APIs.
- Transport is Streamable HTTP.

([MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization), [MCP security](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices))

**Claude-specific requirements:**

- Allow Anthropic's outbound IP range `160.79.104.0/21` on both the server and the authorization server.
- Callback URL: `https://claude.ai/api/mcp/auth_callback`.
- Timeouts of 10 seconds, or 30 seconds for token refresh.
- Output limits: about 150,000 characters on claude.ai and Desktop; 25,000 tokens in Claude Code.

([Building connectors](https://claude.com/docs/connectors/building/index.md))

**Design the tools for an agent, not as a copy of the API:**

- Use fewer, combined tools, with names that say which system they belong to.
- Return names rather than raw IDs.
- Paginate and truncate results, and return errors that say what to do next.

([Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents))

**Hosting:**

- Anthropic recommends **remote** servers, but gives no guidance on which platform to host them on.
- **(Our recommendation)** Host on infrastructure you already run and secure: your cloud account, behind your identity provider, with logging.
- The MCP Registry only lists metadata. It isn't for private servers, and it doesn't make a server appear in Claude.

**Agent SDK:** the SDK doesn't run OAuth itself. Your app fetches the token and passes it in. Allow tools explicitly by name (`mcp__server__tool`). ([Agent SDK MCP](https://code.claude.com/docs/en/agent-sdk/mcp.md))

## Buying a connector, and reviewing it

**"Verified" in the directory doesn't mean safe.** It "isn't a security audit": the developer can change tools after review, and Anthropic doesn't control how the server handles your data ([Verification](https://claude.com/docs/connectors/verification.md)). Anthropic "does not security-audit or manage any MCP server" ([Security](https://code.claude.com/docs/en/security.md)).

**Order of preference (our recommendation):**

1. The vendor's own server.
2. The Claude directory listing.
3. An aggregator (such as CData or Composio), only where no vendor server exists. An aggregator puts a third party in the data path.
4. Community servers: avoid for company data.

**Review checklist:**

1. Is the publisher the vendor itself (vendor domain, vendor docs)?
2. Does it use a per-user or a shared identity, and does it ask only for the scopes it needs?
3. Does the server validate who each token was issued for, and never pass tokens through?
4. Are write tools set to Needs approval or Blocked by default?
5. Is the tool list pinned, or watched for changes? Servers can change their tools after you approve them.
6. Who are the subprocessors, and where is the data processed (including any aggregator)?
7. Does the source system keep audit logs of the twin's actions?
8. Is Anthropic's IP range allowlisted, and nothing broader?
9. How long does a token stay valid after someone is offboarded?
10. **Don't give one twin both untrusted content and a way to send it out** (for example, reading inbound email and posting to Slack) unless a person approves each send. This is the main prompt-injection route.

## Connectors and sensitive data

- **Connector data passes through Anthropic.** claude.ai and API connectors call your server from Anthropic's IP range. Tool results go into the conversation and follow normal retention.
- **Not eligible for ZDR or HIPAA:**
  - the API's MCP connector
  - MCP tunnels
  - hosted Managed Agents.

  The plain Messages API, with your own MCP client and servers, is eligible.
- **The claude.ai BAA doesn't cover data sent to third parties through connectors.** It doesn't cover local MCP servers either. Each system vendor needs its own BAA or data agreement with you.

Sources: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention.md), [BAA article](https://support.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers), [API MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector.md).

## Decision matrix: use, buy, build or host

| Situation | Choice | Why |
|---|---|---|
| A directory connector exists, per-user identity is fine, internal or confidential data | **Use** the directory connector | Least work; the vendor maintains it |
| The vendor has a remote MCP server, but it isn't in the directory | **Use** it as a custom connector (an Owner adds it) | Still vendor-maintained. Decide the auth type up front, because it can't be changed later. |
| The twin acts as a shared role in Slack | **Claude Tag** with one dedicated service account per system | Shared identity that survives staff turnover. Limit which channels each credential reaches. |
| Need redaction, field allowlists, write guards or extra audit (private-equity data) | **Build** a thin wrapper server over the vendor's API, and **host** it ourselves | We control what reaches the model. Use Enterprise managed auth. |
| PHI | **Build** our own MCP client and servers on the Messages API, in the HIPAA org | Connectors, tunnels and Managed Agents aren't eligible ([10](10-sensitive-data.md)) |
| The system is only on a private network | **MCP tunnel** (Enterprise, preview), or run the agent inside the network | Don't expose the system to the internet |
| Dynamics | **Use** the vendor server after pricing Copilot Credits and setting up Entra; otherwise **build** | No directory connector, and use is metered |
| No vendor server, and building costs too much | **Buy** an aggregator, after a subprocessor and security review | A third party enters the data path |
| An in-house tool with no API | **Build**, or defer | The twin can't use what it can't reach |

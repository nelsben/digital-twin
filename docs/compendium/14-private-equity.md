# 14 — Private equity: designing for walls and no walls

Private equity is the primary use case. Some firms or teams need **information barriers** (walls) between deal teams, and some don't. We design once so either can be deployed.

## Three facts that shape everything

1. **Enterprise ZDR covers Claude Code only.** Chat, Cowork and artifacts aren't covered, so private-equity work in claude.ai chat follows custom retention (at least 30 days). ([Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention)) We have two ways to handle this:
   - **(a)** Accept 30-day retention for chat, and keep deal-specific material and MNPI to ZDR surfaces (Claude Code, and hosted agents in the ZDR Platform org). **(Our recommendation)**
   - **(b)** Offer private-equity twins only through ZDR surfaces.

   Raise this with Anthropic too ([12](12-orgs-and-ownership.md), question 3).

   **Decided (2026-11-14):** (a), with 30-day retention as the starting point. Because Anthropic's copy is gone after 30 days, our own governance log is the long-term audit record ([15](15-governance-and-performance.md)).
2. **The Compliance API doesn't see ZDR sessions.** Private-equity twins need **our own audit log**:
   - Locally: a hook in Claude Code records each tool call to a central log.
   - Hosted: the agent's server logs each tool call.
3. **Turn web search and fetch off.** Even under ZDR, search queries and the sites fetched can reveal what a deal team is looking at.

## What a wall has to guarantee

1. People on one side can't see the other side's data.
2. **The twin can't carry data across the wall.**
3. An audit can prove both.

## Where a twin can leak across a wall

| Leak route | Why it's a risk | Control |
|---|---|---|
| **Shared-identity connectors** (service accounts, Claude Tag integration users, HubSpot private-app tokens) | The twin sees everything the service account can, so the wall is gone | **Per-user OAuth only.** Each person's Salesforce, HubSpot and SharePoint permissions then apply to their twin. |
| **Skills that contain deal data** | Skills are shared across the org or a group | Skills hold **methods, never deal data**. Deal facts come from connectors at run time. |
| **Projects, shared chats, artifacts** | They can be shared across teams | Turn off or limit sharing. ⚠ Per-group sharing controls are unverified: ask Anthropic. |
| **Memory** | Claude.ai memory is per user, which is fine. Project memory is shared with the project's members. | One Project per deal team, with members from that team only |
| **Hosted agents** | One agent serving several deal teams mixes their contexts | **One deployment per wall.** Anthropic recommends one self-hosted deployment per tenant or trust level ([Self-hosted Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access)). |
| **Admins** | Org Owners can see across teams | Keep Owners few; separation of duties; our own audit |
| **Local transcripts** | They sit on the laptop | Managed devices only, with purge and encryption ([13](13-devices.md)) |

## Salesforce and HubSpot behind a wall

- **Salesforce:** with per-user OAuth (through an External Client App), the twin acts as the user. Salesforce's own record sharing (roles, sharing rules, account and opportunity teams) should then decide what it sees.
  - ⚠ Confirm with a test user on each side of the wall before relying on it.
  - ⚠ Salesforce Hosted MCP may require Enterprise Edition or higher (from a secondary source).
- **HubSpot:** `mcp.hubspot.com` uses per-user OAuth, so HubSpot's team and record permissions should apply. ⚠ Confirm the same way.
- **Avoid Claude Tag connections** to these systems for walled teams. They use an integration user (Salesforce) or a private-app token (HubSpot), and both bypass per-user permissions.

Sources: [Salesforce on Desktop](https://claude.com/docs/third-party/claude-desktop/connectors-salesforce.md), [HubSpot MCP](https://developers.hubspot.com/docs/build-with-ai/remote-mcp-server), [Claude Tag connections](https://claude.com/docs/claude-tag/admins/connections/overview.md).

## Three designs

| Design | How it works | Strength of the wall | Admin cost | When to use |
|---|---|---|---|---|
| **A. No walls** | One private-equity org; skills, Projects and hosted agents shared | Only what the source systems enforce | Low | Teams without barrier requirements; firm-wide work that isn't deal-specific |
| **B. Soft walls** (our recommended starting point) | One private-equity org. The source systems enforce the walls, through per-user identity. Enterprise groups per team decide which plugins each sees. No shared identities. One Project per deal team. One hosted deployment per wall, as separate workspaces in the Platform org. | Relies on source-system permissions plus disciplined configuration | Medium | Most firms, especially where walls already exist in Salesforce and SharePoint |
| **C. Hard walls** | A separate Claude org (and a separate hosted deployment) per walled team | Strongest: separate admin, retention and audit | High, and it grows with each wall | When a regulator or LP requires provable separation, or for MNPI on public-company deals |

**Decided (2026-11-14):** start with **B, soft walls.** Salesforce, HubSpot and SharePoint already enforce walls through role-based access, in the usual Salesforce governance model. Hard walls (C) remain an upgrade path.

## Designing for both

Build so that soft walls (B) can become hard walls (C) without rework:

- **One Git repo** holds the plugins, skills, persona and evals. The same plugin is deployed to one org or to many.
- **Org settings as code:** keep managed settings, connector lists and plugin policy in files in the repo. Then a new walled org is a copy plus new IDs, not a rebuild.
- **Never put deal data in shared parts** (skills, persona, CLAUDE.md). Everything deal-specific arrives at run time through per-user connectors.
- **Per-user identity everywhere** private equity is involved, so that adding a wall never changes how the twin authenticates.
- **Our own audit log from day one,** because hard walls need proof and ZDR hides sessions from the Compliance API.

## The private-equity twin at a glance (our recommendation)

| Part | Choice |
|---|---|
| Orgs | Org 2 (Enterprise, ZDR) for people; org 3 (Platform, ZDR) for hosted agents, on self-hosted Managed Agents ([12](12-orgs-and-ownership.md)). On HIPAA, the Agent SDK signs in with an API key, and the [HIPAA setup page](https://code.claude.com/docs/en/hipaa-setup.md) says a session on "A Claude Console API key or federation credentials" is not eligible for the HIPAA configuration ([10](10-sensitive-data.md#what-hipaa-covers)). **⚠ Unverified:** whether the Agent SDK is covered under ZDR; get written confirmation from Anthropic before using it |
| Surfaces | Highly sensitive deal work: Claude Code on a ZDR sign-in on a managed device, with no Desktop (ZDR doesn't cover chat or Cowork). A hosted twin for unmanaged devices ([13](13-devices.md)); chat for work that isn't deal-specific |
| Connectors | Salesforce and HubSpot (per-user OAuth); SharePoint and Google Drive (per-user); no shared identities |
| Autonomy | Level 1 (drafts) to start; nothing leaves the firm without a person approving it ([06](06-autonomy.md)) |
| Data handling | Scripts return results, not records; redaction hooks for names of targets and LPs; web tools off ([10](10-sensitive-data.md)) |
| Audit | Our own tool-call log |

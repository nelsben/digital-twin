# 08 — Open decisions and questions you might not know to ask

## Decisions needed before building

| # | Decision | Why it matters | Who decides |
|---|---|---|---|
| D1 | **Team or Enterprise plan on claude.ai?** | Group targeting, security scanning, the usage Analytics API and the Compliance API are Enterprise-only; Team has a usage dashboard ([09](09-plans-and-it-controls.md)) | Admin / IT |
| D2 | **Who are the Owners**, and who gets the "Libraries" permission? | Only Owners and Primary Owners manage org skills; the Admin role isn't enough | Admin / IT |
| D3 | **Does any role touch regulated data** (data needing ZDR, HIPAA, CMEK)? | Skills used through the API or Managed Agents aren't eligible, and the Agent SDK signs in with an API key, and the [HIPAA setup page](https://code.claude.com/docs/en/hipaa-setup.md) says a session on "A Claude Console API key or federation credentials" is not eligible for the HIPAA configuration ([10](10-sensitive-data.md#what-hipaa-covers)). **⚠ Unverified:** whether the Agent SDK is covered under ZDR; this changes the runtime choice ([10](10-sensitive-data.md)) | Security / legal |
| D4 | **Direct Anthropic, or AWS / Google Cloud?** | **⚠ Unverified:** hosted features (Skills API, Managed Agents, Claude Tag) may not be offered through the cloud providers | IT / procurement |
| D5 | **Which systems are the source of truth for each role** (CRM, ticketing, ERP), and is there an MCP connector for each? | The twin can only reach systems that have a connector; a missing one means building or buying it | Each role's ops lead |
| D6 | **What we measure** (time saved, adoption, quality) | The usage Analytics API needs Enterprise, and API-workspace skills have no usage data. A Team customer can still measure: users and activity per plugin and skill over 30 days ([Plugin admin](https://claude.com/docs/plugins/admin)); the usage dashboard ([Pricing](https://claude.com/pricing)); the Claude Code analytics dashboard and its CSV export ([Claude Code analytics](https://code.claude.com/docs/en/analytics)); and our own evals and governance log ([15](15-governance-and-performance.md)) | Sponsor |
| D7 | **Who writes skills, who reviews them, who owns evals** | Authors shouldn't review their own work; evals need re-running when models change | Program owner |
| D8 | **Autonomy ceiling per role** | See [06](06-autonomy.md) | Each role's leader, with security |

### Status after the second round (2026-11-14)

- **D1 (plan):** users span every tier, individual plans included. See [09](09-plans-and-it-controls.md). Recommendation: Team as the minimum for company data, and Enterprise for sensitive roles.
- **D3 (regulated data):** yes, both HIPAA and highly sensitive private-equity data. See [10](10-sensitive-data.md).
- **D4 (cloud route):** decided. We use Claude directly from Anthropic, and Anthropic-hosted agents. AWS and Google Cloud are parked for later.
- **D5 (systems):** CRM, Google Sheets and Drive, SharePoint and shared drives, Slack and Teams. See [11](11-connectors.md).
- **New, D9:** how many Claude orgs (one per data class), and who owns each.
- **New, D10:** whether to accept flagged content kept up to 2 years even under ZDR; in orgs without ZDR, `/feedback` transcripts kept 5 years (feedback is off under ZDR, see [10](10-sensitive-data.md)); and the 6-year default for Compliance API sessions.

### Status after the third round (2026-11-14)

- **D5:** the CRMs are **Salesforce and HubSpot.** Dynamics is out of scope.
- **Devices:** plan for both managed and unmanaged. See [13](13-devices.md).
- **D9 (orgs):** we're an Anthropic partner, so we can get separate instances. The starting ask is three orgs, plus HIPAA later, plus one per hard wall. See [12](12-orgs-and-ownership.md).
- **Private equity** is the primary use case. We design for both walls and no walls. See [14](14-private-equity.md).
- The open questions for Anthropic are collected in [12](12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).

### Status after the fourth round (2026-11-14)

- **Private-equity chat retention:** 30 days to start. Auditability and performance visibility are requirements for every twin. See [15](15-governance-and-performance.md).
- **Walls:** soft walls, enforced by role-based access in Salesforce, HubSpot and SharePoint ([14](14-private-equity.md)).
- **Owners:** the Director of IT is the technical owner and the RevOps manager is the business owner ([12](12-orgs-and-ownership.md)). Still open: a backup Owner for each org.
- **Log destination:** a discussion point with each customer, including any logging that already exists between Salesforce and Anthropic ([15](15-governance-and-performance.md)).
- **IT owns tooling and spend.**
- **The brief for Anthropic is on hold.** The questions stay in [12](12-orgs-and-ownership.md#questions-to-bring-to-anthropic-as-a-partner).

## Questions most first-time builders miss

**Identity and access**

1. Whose name is on each action, and does it change between a Slack channel and a DM? (In a channel or a group DM that includes Claude, Claude Tag acts as its own service account; work done with a user's own claude.ai connectors, after they allow it, is recorded under that user's name; in a one-to-one DM it runs as the user. [Tag identity](https://claude.com/docs/claude-tag/concepts/agent-identity.md))
2. When an employee leaves, which twin jobs stop and which keep running?
   - Stop: personal scheduled tasks and DM routines.
   - Keep running: channel routines and anything they shared.
3. Can one API key reach every user's stored credentials? With Managed Agents vaults, yes: any key with access to the workspace can. Plan workspaces with that in mind.
4. Can we offer "sign in with claude.ai" in something we build? Not without Anthropic's approval: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products" ([Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md)).

**Skills lifecycle**

5. Which Git repo is the source of truth, and who publishes from it to each surface? There is no single pipeline.
6. Pinned versions or "latest"? With "latest" on the API, anyone with access to the workspace can change what production runs.
7. How many skills before the right one stops firing reliably? Keep each role plugin small.
8. When someone leaves, who takes over the skills they wrote? The knowledge they captured shouldn't leave with them.

**Safety**

9. Can untrusted input (emails, tickets, web pages) write to the twin's memory and plant instructions?
10. What permissions does a skill inherit? In Claude Code, a skill's scripts run with the session's full access, and repo skills are trusted on sight.
11. Who approves tool calls when nobody is watching?

**Reliability and cost**

12. How do we know a run did the task, and not just that it finished?
13. What catches missed or failed runs? Managed Agents doesn't re-run missed schedules, and its webhooks give up after 3 delivery attempts.
14. Multi-agent designs use about 15 times the tokens of a chat. Is the task worth that?
15. Which costs grow per seat (client) and which per run (hosted)?

## Things to research next

- How claude.ai Project instructions relate to org plugins (as a way to carry the persona on claude.ai).
- Which features are available on Bedrock and Vertex (D4).
- The Agent SDK's permissions, hooks and cost-tracking pages, and the Managed Agents permission-policy and budget pages. The first research pass didn't fetch these.
- The Claude Tag security page, and Enterprise Managed Auth for connectors.
- Which connectors already exist for the pilot roles' systems (D5).

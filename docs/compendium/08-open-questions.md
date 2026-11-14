# 08 — Open decisions and questions you might not know to ask

## Decisions needed before building

| # | Decision | Why it matters | Who decides |
|---|---|---|---|
| D1 | **Team or Enterprise plan on claude.ai?** | Group targeting, security scanning, usage analytics and the Compliance API are Enterprise-only | Admin / IT |
| D2 | **Who are the Owners**, and who gets the "Libraries" permission? | Only Owners and Primary Owners manage org skills; the Admin role isn't enough | Admin / IT |
| D3 | **Does any role touch regulated data** (data needing ZDR, HIPAA, CMEK)? | Skills and Managed Agents aren't eligible; this changes the runtime choice | Security / legal |
| D4 | **Direct Anthropic, or AWS / Google Cloud?** | Hosted features (Skills API, Managed Agents, Claude Tag) may not be offered through the cloud providers ⚠ Unverified | IT / procurement |
| D5 | **Which systems are the source of truth for each role** (CRM, ticketing, ERP), and is there an MCP connector for each? | The twin can only reach systems that have a connector; a missing one means building or buying it | Each role's ops lead |
| D6 | **What we measure** (time saved, adoption, quality) | Usage analytics need Enterprise; API-workspace skills have none | Sponsor |
| D7 | **Who writes skills, who reviews them, who owns evals** | Authors shouldn't review their own work; evals need re-running when models change | Program owner |
| D8 | **Autonomy ceiling per role** | See [06](06-autonomy.md) | Each role's leader, with security |

## Questions most first-time builders miss

**Identity and access**

1. Whose name is on each action, and does it change between a Slack channel and a DM? (In a channel, Claude Tag acts as a service account; in a DM, as the user.)
2. When an employee leaves, which twin jobs stop and which keep running?
   - Stop: personal scheduled tasks and DM routines.
   - Keep running: channel routines and anything they shared.
3. Can one API key reach every user's stored credentials? With Managed Agents vaults, yes: any key with access to the workspace can. Plan workspaces with that in mind.
4. Can we offer "sign in with claude.ai" in something we build? Not without Anthropic's approval.

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

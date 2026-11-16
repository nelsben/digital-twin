# 15 — Governance, audit and performance

Governance has to answer three questions for every twin:

1. **What did it do?** (audit)
2. **Did it do it well?** (quality)
3. **Is it worth it?** (adoption and value)

No single Anthropic feature answers all three, and none covers every org. ZDR sessions are invisible to the Compliance API, and with 30-day retention in the private-equity org, Anthropic's copy of the records is gone after 30 days. So **we keep our own governance log** and feed every other source into it.

## What each source records

| Source | Covers | Gaps | Plan |
|---|---|---|---|
| **Audit logs** | Admin and sharing events, for 180 days | The page doesn't list skill, plugin, connector or Claude Code events; no export in CMEK orgs | Enterprise |
| **Compliance API** | Chats, files, Projects, and Cowork, Claude Code and Claude Tag sessions, including tool results | **Doesn't capture ZDR sessions** | Enterprise (a Console org gets the activity feed only) |
| **Skills analytics API** | Skill use by user, group and product, a day behind | Skills uploaded to an API workspace | Enterprise |
| **Plugins & skills inventory** | Users and activity over 30 days | No export | Team, Enterprise |
| **Claude Code / Agent SDK OpenTelemetry** | Per-session metrics and events, exported to our monitoring | Prompts and tool inputs are off by default. **⚠ Unverified:** the exact metric list. | Any (configured through managed settings) |
| **Managed Agents events and webhooks** | A stream of session events | Webhooks give up after 3 attempts and "aren't a durable log" | Platform |
| **Scheduled task run history** | Each run and its transcript | "Succeeded" means the session ended, not that the task got done | Team, Enterprise |
| **Source-system audit** (Salesforce, HubSpot, Microsoft 365) | Every change the twin made in that system | The twin acts *as the user*, so its changes look like the user's | Per vendor |

Sources: [Audit logs](https://support.claude.com/en/articles/9970975), [Compliance API](https://platform.claude.com/docs/manage-claude/compliance-api), [Compliance sessions](https://platform.claude.com/docs/en/manage-claude/compliance-sessions), [Skills analytics](https://platform.claude.com/docs/en/api/organization/analytics/skills.md), [Claude Code org plugins](https://code.claude.com/docs/en/plugins/org.md), [Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting.md), [Webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks.md), [Scheduled tasks](https://code.claude.com/docs/en/routines.md).

**Tell twin actions apart from human ones.** With per-user identity, a Salesforce update by the twin appears under the rep's name. (Our recommendation) Have every write tool add a marker, such as a "Last updated by twin" field or a note prefix. Then the CRM's own history shows what the twin did. This also lets the RevOps manager report on it.

## One governance log for all twins (our recommendation)

```
Local Claude Code ─ managed hook (after each tool call) ─┐
Hosted agents ───── server logs each tool call ──────────┤
OpenTelemetry (Claude Code, Agent SDK) ──────────────────┼──► governance log
Nightly pulls: Compliance API (non-ZDR orgs), ───────────┤    (our SIEM or data warehouse,
  skills analytics, audit logs                           │     our own retention period)
Source-system audit (Salesforce, HubSpot, M365) ─────────┘
```

**Each record holds:** when; who; which twin and skill; which tool; which system and record IDs; whether it was approved, and by whom; the outcome; tokens and cost.

**Private equity: log metadata, not content.** Record that the twin read a given opportunity, not what was in it. Otherwise the log becomes a way around the walls. Restrict access to the log as tightly as the deal data, and keep a reviewed record of who reads it.

The hook lives in managed settings, so users can't remove it on managed devices. Hosted agents log on the server, so unmanaged devices are covered too ([13](13-devices.md)).

**Where the hook fires.** The [hooks page](https://code.claude.com/docs/en/hooks) says "Claude Code fires the same hook events wherever it runs: sessions in the terminal, IDE extensions, the Desktop app, and cloud sessions". Its "Desktop app" link goes to Claude Code's [Desktop quickstart](https://code.claude.com/docs/en/desktop-quickstart.md), which puts Claude Code "in the **Code** tab" of the desktop app: the Code tab, not a chat in Claude Desktop. In a self-hosted environment Claude Code also runs the hooks the operator seeded from the runner host. (Our reading): the governance hook covers none of claude.ai chat, Cowork, Claude in Slack or Claude Tag, or Teams, because the hooks page names none of them.

**A Claude Tag routine has no per-action log.** No hook covers it (above), and Claude Tag's audit page says "There is no per-action log of every task and who asked". Its trails are the **Activity** page (each routine's **Created by** on the Scheduled work tab, memory, and a best-effort network events export), each connected service's own audit log, and on Enterprise with the Compliance API, the session transcript with Claude's tool calls ([Claude Tag audit](https://claude.com/docs/claude-tag/admins/audit.md)).

**Agent SDK sessions.** The Agent SDK loads plugins by path, and a plugin can carry hooks (`hooks/hooks.json`) with its skills, agents and MCP servers: "Load custom plugins to extend Claude Code with skills, agents, hooks, and MCP servers through the Agent SDK" ([Agent SDK plugins](https://code.claude.com/docs/en/agent-sdk/plugins.md)). (Our reading): an Agent SDK session that loads the twin's plugin by path brings the plugin's hooks with it, so the governance hook can travel in the plugin.

### Where the log lives: settle it with each customer

**Decided (2026-11-14):** we don't prescribe the destination. It is a **discussion point with each customer**, and IT owns the tooling choice. The design above stays fixed: what gets recorded, metadata only for private equity, and one log for all twins. Only the destination changes.

Points to cover in that discussion:

- **What the customer already runs:** a security log system (SIEM), a data warehouse, or an observability tool. Use theirs if possible.
- **Logging on the Salesforce side.** If the customer already captures API and record activity in Salesforce, that may cover the source-system part of the log. Check this per customer. Examples: Event Monitoring, Field Audit Trail, Setup Audit Trail.
- **Logging that already exists between Salesforce and Anthropic.** If the customer uses Claude through a Salesforce integration, find out what that path already logs, and where.
- **Who can read the log,** and how long it is kept, set with the customer's compliance team.

## Retention, decided

- **Private-equity org:** 30-day custom retention for chat, as a starting point. Claude Code and hosted agents run under ZDR.
- **Our governance log** is the long-term audit record. Set its retention with compliance.
- **Keep in view:**
  - Even under ZDR, flagged content can be kept for up to 2 years ([Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention)). In orgs without ZDR, `/feedback` transcripts are kept 5 years; under ZDR feedback is off ([10](10-sensitive-data.md)).
  - The general org keeps Compliance API sessions for 6 years by default unless a custom period is set ([10](10-sensitive-data.md)). Set it to match policy.

## Team plan with no device management

A Team customer with no MDM runs its twin in claude.ai on the web ([13](13-devices.md#team-plan-with-no-device-management) lists what that surface gets). For governance this means:

- **What we can record:** the usage dashboard and the per-plugin and per-skill Users and Activity counts over 30 days ([Pricing](https://claude.com/pricing), [Plugin admin](https://claude.com/docs/plugins/admin)); and source-system audit in the customer's own tools.
- **What we can't:** there's no audit log and no Compliance API on Team ([Audit logs](https://support.claude.com/en/articles/9970975), [Pricing](https://claude.com/pricing)). The governance log above depends on a Claude Code hook in managed settings ([Hooks](https://code.claude.com/docs/en/hooks)), which doesn't exist in claude.ai on the web, and server-managed settings alone are "not a security boundary" ([Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md)).
- **So the twin cannot meet a requirement to log every action.** (Our reading) of the sources above. Raise this in discovery. If the requirement stands, the customer needs Claude Code on MDM-managed devices with the managed hook ([13](13-devices.md)).

## Measuring performance

| Layer | What to measure | Where it comes from |
|---|---|---|
| **Adoption** | Active users per twin and skill; sessions per week; which skills never trigger | Skills analytics, the inventory, OpenTelemetry |
| **Quality** | Eval pass rate per skill and model version; **how much people edit drafts** before using them; approve and reject rates on approval-gated actions; escalations and errors | Evals in the repo (run in CI); our log; sampled reviews |
| **Value** | Time saved per task, against a baseline from role interviews; tasks completed; **cost per task** (tokens plus runtime) | Interviews ([07](07-pilot-roles.md)); our log; OpenTelemetry |
| **Safety** | Tool calls denied or blocked by hooks; attempts to reach data across a wall; injection attempts caught | Our log; hooks |

**A scorecard per twin, monthly,** reviewed with the business owner. Moving a task up an autonomy level ([06](06-autonomy.md)) requires scorecard evidence: a stable eval pass rate, a low edit rate and few rejections.

## Who does what, and how often

| Cadence | What | Who |
|---|---|---|
| Every skill change | Pull-request review by someone other than the author; evals must pass | Skill owner, reviewer |
| Every model release | Rerun all evals before switching models | Technical owner |
| Monthly | Twin scorecards; decisions to promote or demote autonomy | **RevOps manager** (business owner), with the Director of IT |
| Quarterly | Access review: Owners, group membership, connector scopes; retention review | **Director of IT** (technical owner), with compliance for the private-equity org |
| Ongoing | **Tooling and spend:** choosing the log destination and monitoring tools; budgets, Claude spend controls and per-user limits, usage alerts ([what each plan offers](09-plans-and-it-controls.md#spend-and-usage-limits)); cost per task on the scorecard | **IT** (Director of IT) |
| On offboarding | Revoke access, "Stop sharing" items they shared, purge the laptop, reassign skills they owned | Director of IT |

**Later phase:** build a governance dashboard on top of the log.

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
| **Claude Code / Agent SDK OpenTelemetry** | Per-session metrics and events, exported to our monitoring | Prompts and tool inputs are off by default. ⚠ Check the exact metric list. | Any (configured through managed settings) |
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

## Retention, decided

- **Private-equity org:** 30-day custom retention for chat, as a starting point. Claude Code and hosted agents run under ZDR.
- **Our governance log** is the long-term audit record. Set its retention with compliance.
- **Keep in view:**
  - Even under ZDR, flagged content can be kept for up to 2 years, and `/feedback` transcripts for 5 years.
  - The general org keeps Compliance API sessions for 6 years by default unless a custom period is set ([10](10-sensitive-data.md)). Set it to match policy.

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
| On offboarding | Revoke access, "Stop sharing" items they shared, purge the laptop, reassign skills they owned | Director of IT |

**Later phase:** build a governance dashboard on top of the log.

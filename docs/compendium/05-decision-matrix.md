# 05 — Hosted agent or client skill?

## The options

| Option | Who runs it | Acts as | Started by | Status |
|---|---|---|---|---|
| **Client skill or plugin** (claude.ai, Desktop, Claude Code) | Anthropic's client | **The employee**: their own permissions, with connectors each person signs in to | A person, in a conversation | Generally available |
| **Claude Code scheduled task** | Anthropic's cloud, or your own environment | **The employee**: "appears as you", with all their connectors, write access included | A schedule (hourly at most often), an API call, a GitHub event | Research preview |
| **Claude Tag** (Claude in Slack) | Anthropic | **In channels and in group DMs that include Claude: Claude's own service account**, the same whoever asks. A user can let Claude use their own claude.ai connectors for a task in a channel; that work runs with the user's permissions, under their name. In a one-to-one DM: the user's own account | An @mention, or a channel routine (scheduled no more than hourly, or watching the channel) | Public beta, Team and Enterprise |
| **Managed Agents** | Anthropic hosts the harness and sandbox; self-hosting is available | An API key plus a per-user **vault** of credentials | An API call, or a scheduled deployment (cron) | Beta |
| **Agent SDK** | **You**: each session runs in your container | Your API key, plus credentials you pass in | Whatever you build (webhook, cron, bot) | Generally available |
| **Messages API + tools** | You | Your API key | Whatever you build | Generally available (the Tool Runner is beta) |

**Watch the word "scheduled".** It names three different features, and each runs as a different identity:

- A Claude Code scheduled task runs **as the user**.
- A Claude Tag channel routine runs **as the channel** and keeps running after its creator leaves.
- A Managed Agents scheduled deployment runs **as an API key plus a vault**, pinned to one agent version.

Sources: [Scheduled tasks](https://code.claude.com/docs/en/routines.md), [Claude Tag](https://claude.com/docs/claude-tag/overview.md), [Tag identity](https://claude.com/docs/claude-tag/concepts/agent-identity.md), [Tag proactivity](https://claude.com/docs/claude-tag/users/proactivity.md), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview.md), [Vaults](https://platform.claude.com/docs/en/managed-agents/vaults.md), [Scheduled deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments.md), [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md), [Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting.md).

## Decision criteria

| Criterion | Points to **hosted** | Points to **client** |
|---|---|---|
| **Trigger** | An event, webhook, schedule or Slack mention, with nobody at a keyboard | A person starts the work |
| **Autonomy** | Approvals can be decided in advance through policy and hooks | Each action needs a person's judgment |
| **Identity** | Shared team work, done as a service account or a vaulted user credential | Must act *as the employee*, with their permissions and their audit trail |
| **Continuity** | Must keep running when the person is away or has left | Tied to one person |
| **Data sensitivity** | Needs ZDR: the Messages API with eligible features, or a fully self-hosted Managed Agents deployment (**not** hosted Managed Agents or API skills). Needs HIPAA (PHI): no hosted agent runtime. Managed Agents is blocked under HIPAA readiness, and the Agent SDK's cover is unverified (below). The API route with HIPAA readiness covers only your own code on the Messages API with the eligible features ([10](10-sensitive-data.md#what-hipaa-covers)). (Our recommendation) Don't build a twin on it until Anthropic confirms a hosted route in writing. ⚠ **Unverified:** whether the Agent SDK is covered under HIPAA or ZDR. No page says so ([10](10-sensitive-data.md)). | Data the user can already see in the client |
| **Cost** | Mostly tokens, plus runtime: Managed Agents charges $0.08 per session-hour while running; containers cost about $0.05 per hour | Covered by seats and usage limits; no infrastructure to run |
| **Who maintains it** | An engineering team that owns deploys, secrets and on-call | Admins publish; domain experts write skills |
| **Reach** | One endpoint can serve many channels and systems | One copy per surface, since skills don't sync to the API |
| **Shape of the work** | Long-running, many steps, fanning out | Short and interactive, with a person checking each step |

Sources: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), [Pricing](https://platform.claude.com/docs/en/about-claude/pricing.md), [Agent SDK hosting](https://code.claude.com/docs/en/agent-sdk/hosting.md), [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview.md).

## Decision flow (our recommendation)

```
1. Does a person start the task in a conversation and review the result?
      yes → CLIENT SKILL in the role plugin. Stop here.
2. Does the task need to happen without the person present (schedule or event)?
      ├─ It's one person's own recurring task, done as them
      │     → Claude Code scheduled task (acts as them; stops if they leave)
      ├─ It's shared team work that lives in Slack
      │     → Claude Tag channel routine (service account; survives turnover)
      └─ It's wired into systems (CRM webhook, ticket queue, nightly job)
            ├─ PHI (HIPAA)       → no hosted agent runtime; see 10 (HIPAA, the API route)
            ├─ Needs ZDR         → Messages API with eligible features, or fully
            │                      self-hosted Managed Agents. Agent SDK only once
            │                      Anthropic confirms ZDR cover in writing (⚠ Unverified)
            └─ Otherwise         → Managed Agents
3. Whichever you choose: keep the skills the same, change only the runtime.
```

The last step is the key design idea. **Write a skill once and run it anywhere.** A skill such as "prepare an account brief" can be used in chat today and called by a hosted agent later. Only the runtime, identity and guardrails change.

## What this means for the pilots (our recommendation)

- **Phase 1:** a client-side role plugin for each pilot group, at "draft and recommend" autonomy ([06](06-autonomy.md)). This needs no infrastructure, uses the employee's own permissions, and gives the fastest feedback.
- **Phase 2:** at most one hosted job per role, chosen where a schedule or event really adds value. Examples are a Monday pipeline digest in a team Slack channel, or a nightly account-health scan. Prove the skill in the client first.
- **Phase 3:** Managed Agents or the Agent SDK, only for integrations that run in systems with no person in the loop.

**Decided (2026-11-14):** we use Claude directly from Anthropic, and Anthropic-hosted agents. AWS Bedrock and Google Vertex AI are parked for later. Whether the Skills API, Managed Agents and Claude Tag are available through those clouds is unverified.

For sensitive data, the runtime choice is further limited by data class. See [10](10-sensitive-data.md).

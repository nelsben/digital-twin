# 10 — Handling sensitive data

Some twins will handle HIPAA data (PHI). Others will handle highly sensitive data that isn't HIPAA, such as private-equity deal data or material non-public information (MNPI). This page explains what actually leaves the machine, what ZDR and HIPAA cover, and which setup fits which kind of data.

## First: "running locally" doesn't keep data local

Claude Code and the Agent SDK run **tools and files** on your machine, but the **model runs at Anthropic**. On every turn the agent sends the conversation to Anthropic's API.

| Stays on the machine | Sent to Anthropic on every turn |
|---|---|
| Files the agent never opens | Prompts and the model's replies |
| Running tools and scripts | **The contents of any file the agent reads** |
| The script code itself (for skill scripts) | **The output of any command or script** |
| | Results from connectors and MCP servers |
| | CLAUDE.md, the persona and loaded skill bodies |

"Claude Code runs locally. To interact with the LLM, Claude Code sends data over the network. This data includes all user prompts and model outputs." ([Data usage](https://code.claude.com/docs/en/data-usage)). Everything the agent reads goes into the conversation that is sent ([Agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop)).

**So data stays protected through two things:**

1. **The contract and the org's configuration:** ZDR, a BAA and the HIPAA settings.
2. **Minimization:** designing the twin so the sensitive data never enters the conversation.

**A surprise for Enterprise orgs:** with the Compliance API on, Anthropic records *local* Claude Code and Cowork sessions on its servers, including file contents in tool results. These are kept **for 6 years by default**, or for your custom retention period, or 30 days in HIPAA orgs. Only ZDR sessions are excluded. ([Compliance sessions](https://platform.claude.com/docs/en/manage-claude/compliance-sessions))

Local transcripts also sit in plain text under `~/.claude/projects` for 30 days by default.

## What ZDR is, and isn't

**What it is:** Zero data retention means Anthropic doesn't store your inputs and outputs after responding. It is set up per organization by contract.

**Two routes for Claude Code:**

- a Console API key in an org with a ZDR contract
- Claude Enterprise ZDR.

Sources: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention).

**What ZDR doesn't cover:**

- **API features:** skills, code execution, the Files API, Batch, the API's MCP connector and MCP tunnels, programmatic tool calling, and hosted Managed Agents. (A fully self-hosted Managed Agents deployment is the exception.)
- **Enterprise apps:** chat, Cowork, artifacts and the Chrome extension.
- **Analytics metadata.**

**What ZDR turns off:** cloud sessions, Claude Tag, Remote Control and feedback submission (`/feedback`, `/bug`, `/share`) ([Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention)).

**What is still retained under ZDR:**

- Content flagged for trust and safety review: up to **2 years**. Classifier scores: up to 7 years.
- Metrics and metadata.

**Without ZDR,** transcripts a user shares with `/feedback`, `/bug` or `/share` are kept for **5 years** ([Data usage](https://code.claude.com/docs/en/data-usage)). Under ZDR those commands are off, so this doesn't apply.

**Model choice:** Anthropic's most capable "Covered Models" tier **requires 30-day retention.** ZDR roles must use a model outside it.

## What HIPAA covers

**The API route:**

- Turn on HIPAA readiness in the Console. It is **permanent** for that org.
- Eligible: messages, prompt caching, citations, PDFs, client-side tools (bash, text editor, memory tool), web search and structured outputs.
- Blocked with an error: skills, code execution, Files, Batch, the MCP connector, web fetch, tool search, context editing and Managed Agents.
- JSON schemas are cached for 24 hours, so put no PHI in schemas or tool definitions.

**The Enterprise HIPAA configuration:**

- **Covered:** the Claude Code CLI and the Code tab, under the BAA.
- **Requirements:** Claude Code v2.1.285 or later, signing in through claude.ai, and managed settings (`forceLoginMethod`, `forceLoginOrgUUID`, `allowedProviders: ["anthropic"]`, `cleanupPeriodDays`).
- **Not eligible:** Console keys, gateways or a custom base URL.
- **Turned off by the configuration:** web fetch, cloud sessions, Remote Control and artifact publishing.

**Not covered by the BAA:**

- Connectors and skills.
- The VS Code and JetBrains extensions.
- Claude Tag, which isn't available at all.
- Local skills and local MCP servers: "available but not covered".

**⚠ Conflict:** the API data-retention page says "Claude Code is not covered under HIPAA readiness". That refers to the API route. The BAA article and the HIPAA setup page say the Claude Code CLI *is* covered with an Enterprise sign-in going directly to Anthropic. Confirm in writing with Anthropic.

**Agent SDK and HIPAA.** The [HIPAA setup page](https://code.claude.com/docs/en/hipaa-setup.md) says a session that connects with "A Claude Console API key or federation credentials" is not eligible for the HIPAA configuration: "These sessions belong to a Claude Console organization, which has its own agreement and settings". The [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md) tells developers to use API key authentication. (Our reading): an Agent SDK session is such a session, so the HIPAA configuration doesn't cover it. **⚠ Unverified:** whether the Console organization's own agreement covers the Agent SDK for PHI, and whether the Agent SDK is covered under ZDR. Get written confirmation from Anthropic before using it for PHI.

Sources: [HIPAA setup](https://code.claude.com/docs/en/hipaa-setup), [BAA article](https://support.claude.com/en/articles/8114513-business-associate-agreements-baa-for-commercial-customers), [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

## Other controls

| Control | What it does | Limits |
|---|---|---|
| Commercial terms | No training on your data by default | Doesn't apply to individual plans ([09](09-plans-and-it-controls.md)) |
| Custom retention (Enterprise) | Sets how long data is kept; the minimum is 30 days | Doesn't cover Claude Tag, Managed Agents or cloud Claude Code |
| `inference_geo: us` | Keeps processing in the US, at 1.1× the price | US or global only, unless you use the cloud providers |
| CMEK | Your own encryption keys (US only; compatible with ZDR) | Turns off Claude Tag, Claude Code on the web and skill scanning |
| IP allowlist (beta) | Restricts which networks can reach the Platform and Enterprise apps | Doesn't cover Slack/Tag or Managed Agents' networking |
| Inference hooks (Enterprise) | Inline data-loss-prevention checks across products | **Can block but can't redact**; not available for API orgs |
| Compliance API | Activity, content and session records | **Doesn't capture ZDR sessions**, so ZDR roles need their own audit trail |
| Claude Code deny rules plus sandbox | Limit which files and commands are reachable | Deny rules don't stop `grep -r` or scripts from reading files; only the sandbox enforces at the OS level. Lock both through managed settings. |

Sources: [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency), [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek-coverage-claude-enterprise), [IP allowlist](https://platform.claude.com/docs/en/manage-claude/ip-allowlist), [Inference hooks](https://platform.claude.com/docs/en/manage-claude/inference-hooks), [Custom retention](https://support.claude.com/en/articles/10440198-custom-data-retention-controls-for-claude-enterprise), [Permissions](https://code.claude.com/docs/en/permissions), [Sandboxing](https://code.claude.com/docs/en/sandboxing).

## Decision matrix by data class (our recommendation, built from the sources above)

| Data class | Examples | Plan and org | Allowed surfaces | Not allowed | Required controls |
|---|---|---|---|---|---|
| **Internal** | Process docs, public account info | Team or Enterprise | Everything: chat, Cowork, Claude Code, Claude Tag, connectors, Managed Agents | Individual plans | Commercial terms; SSO; baseline managed settings |
| **Confidential** | CRM data, customer contracts, financials | Enterprise (Team acceptable with a lower audit need) | Claude Code local, Cowork, vetted connectors; Claude Tag only in scoped private channels | Individual plans; unvetted connectors | Custom retention (otherwise local sessions are kept 6 years); IP allowlist; inference-hook data-loss prevention; managed deny rules plus sandbox; connector allowlist; telemetry and feedback off |
| **Highly sensitive** (PE deal data, MNPI) | Target lists, deal models, LP data | **Separate Enterprise org with ZDR** | Claude Code locally on a ZDR sign-in; fully self-hosted Managed Agents. The Agent SDK: a session on a Console API key is not eligible for the HIPAA configuration ([HIPAA setup](https://code.claude.com/docs/en/hipaa-setup.md)). **⚠ Unverified:** whether it is covered under ZDR; don't use it until Anthropic confirms in writing | Claude Tag, cloud sessions, Remote Control, hosted Managed Agents, API skills, code execution, Files, Batch, the API's MCP connector, **web search and fetch** (queries can reveal deal intent) | A model outside "Covered Models"; org lock via MDM; sandbox that fails closed; allowlists of reachable domains and file paths; scripts that return results, not raw records; redaction hooks; **your own audit log** (the Compliance API excludes ZDR); one org or deployment per deal team, as an information barrier |
| **PHI / HIPAA** | Patient records | **Dedicated HIPAA org** (permanent) with a signed BAA | Claude Code CLI or Code tab under the HIPAA configuration. **No hosted agent runtime:** Managed Agents is blocked under HIPAA readiness, and an Agent SDK session on a Console API key is not eligible for the HIPAA configuration (above). (Our reading) of the eligible and blocked lists: the API route's eligible features above are Messages API features for code the customer or we write, and Managed Agents is on its blocked list, so it gives no hosted agent runtime ([What HIPAA covers](#what-hipaa-covers)); (Our recommendation) don't build a twin on it until Anthropic confirms a hosted route in writing | Connectors, IDE extensions, Claude Tag, skills, code execution, Files, Batch, MCP connector, web fetch, Managed Agents; the Agent SDK (a Console API key session isn't eligible for the HIPAA configuration; see above) | HIPAA managed settings; v2.1.285 or later; no gateway or custom base URL; no PHI in schemas, tool names, workspace names or CLAUDE.md; local transcripts purged within 30 days |

## Design patterns that keep data out of the conversation

1. **Scripts that return results, not records.** For a skill script, only its output enters the conversation. Have it return totals, IDs or pass/fail, never raw rows. Example: a reconciliation script returns "3 mismatches: IDs 104, 221, 380", not the ledger.
2. **Tokenize before the model sees it.** A local hook or local MCP server can swap names and identifiers for tokens on the way in and swap them back on the way out. Anthropic's inference hooks can only block, so redaction has to be yours.
3. **Read-only, least-privilege connectors,** run locally rather than through the API's MCP connector, which isn't ZDR- or HIPAA-eligible. Remember that local MCP servers aren't covered by the BAA: treat them as your own processing, under your own vendor agreements.
4. **Separate orgs by data class.** HIPAA is permanent per org, and ZDR, CMEK and Claude Tag constrain each other. Don't mix classes in one org.
5. **Clean up laptops.** Shorten `cleanupPeriodDays`, use full-disk encryption, and run `claude purge --all --yes` when someone leaves.

## Questions to settle with compliance and legal

- Will compliance accept **2-year retention of flagged content**, even under ZDR? In orgs without ZDR, will it accept **5-year retention of `/feedback` transcripts**? If not, turn feedback off with `DISABLE_FEEDBACK_COMMAND=1` in managed settings ([Data usage](https://code.claude.com/docs/en/data-usage)).
- With the Compliance API on, Anthropic keeps local sessions for **6 years**. Is that what your records and eDiscovery policies want? If not, set a custom retention period.
- What is the **audit trail for ZDR roles,** since the Compliance API can't see them?
- Are **local transcripts on laptops** in scope for legal hold and offboarding?
- Do our own vendor agreements and BAAs cover the **local MCP servers and their upstream SaaS vendors**? Anthropic neither audits nor covers them.
- Does our contract address the **Agent SDK** and **Covered Models** explicitly?

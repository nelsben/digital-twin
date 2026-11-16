# 12 — How many Claude orgs, and who owns them

## What "ownership" means

Each Claude org is a separate tenant, with its own users, settings, plugins, connectors, retention and audit. Someone has to run each one. Every org needs three kinds of owner:

| Owner | Usually | Responsible for |
|---|---|---|
| **Technical owner** (the Owner or Primary Owner role in Claude, plus a backup) | IT | Setup and day-to-day running, listed below |
| **Business / data owner** | The role's leader, or compliance for private equity | Who may join; which data classes are allowed; approving skills and autonomy levels; signing off on retention exceptions |
| **Skill owners** | Domain experts | Each skill's content, evals and updates, recorded in the registry ([04](04-distribution-governance.md)) |

The technical owner's duties:

- SSO, SCIM and the domain.
- Device policies and managed settings.
- Publishing plugins and adding connectors. Only Owners can manage these; the Admin role can't.
- Retention, audit and the Compliance API.
- Offboarding.

Sources: [Plugins admin](https://claude.com/docs/plugins/admin) (Plugins & skills is for Owners and Primary Owners; the Admin role doesn't include it), [Connectors](https://claude.com/docs/connectors/getting-started.md) (an Owner adds connectors on Team and Enterprise), [Pricing](https://claude.com/pricing) (SCIM, audit logs and the Compliance API on Enterprise), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention) (ZDR is enabled per org; a new org needs its own enablement).

**Why this matters:** each extra org repeats all of that work: its own SSO app, settings, plugin publishing, connector setup, audit and offboarding. Orgs are easy to request and costly to run. So the goal is **as few orgs as the data rules allow** (our recommendation).

## Why more than one org

Some settings apply to a whole org and conflict with each other:

- **HIPAA readiness on the API is permanent** once it's turned on, and it blocks many features. ⚠ **Unverified:** whether the Enterprise HIPAA configuration can be turned off again; no page fetched says so.
- **ZDR** turns off Claude Tag, cloud sessions and artifacts in Claude Code.
- **CMEK** turns off Claude in Slack (Claude Tag), Claude Code on the web and skill scanning.

Sources: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention), [CMEK](https://platform.claude.com/docs/en/manage-claude/cmek-coverage-claude-enterprise).

A sales twin that uses Claude Tag and a private-equity twin that needs ZDR can't share an org. ([10](10-sensitive-data.md))

**Decided (2026-11-14):** the **Director of IT** is the technical owner and the **RevOps manager** is the business owner. Each org still needs a backup with the Owner role, so that no single person can lock everyone out.

## Recommended starting point

| # | Org | Plan type | For | Key settings | When |
|---|---|---|---|---|---|
| 1 | **General** | Claude Enterprise | Sales, CS and ops twins; internal and confidential data | SSO, SCIM, custom retention, Compliance API, Claude Tag allowed; connectors for Salesforce, HubSpot, Google, Microsoft 365 and Slack | Day 1 |
| 2 | **Private equity** | Claude Enterprise **with ZDR** (CMEK optional) | Private-equity twins (the primary use case) | ZDR; no Claude Tag or cloud sessions; custom retention for chat (ZDR doesn't cover chat, see [14](14-private-equity.md)); org lock via device management; our own audit log | Day 1 |
| 3 | **Build and hosted** | Claude Platform (API/Console) org **with ZDR** | Developing and evaluating skills (API skills aren't ZDR- or HIPAA-eligible, so develop them with non-sensitive data); hosted private-equity agents on self-hosted Managed Agents. ⚠ **Unverified:** whether the Agent SDK is covered under HIPAA or ZDR | Workspaces: `dev`, `staging`, `prod`; `inference_geo: us`; pinned skill versions ([Skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide): pin a version for production) | Day 1 if a hosted twin is in phase 1 or 2; otherwise when the first hosted job arrives |
| 4 | **HIPAA** | Enterprise with the HIPAA configuration, or Platform with HIPAA readiness | Roles that handle PHI | Permanent; requires a BAA | **Only when a PHI role is actually in scope.** Don't create it early. |
| +N | **Walled private equity** | Copy of org 2 | One per *hard* information barrier | Same as org 2 | Only if compliance requires provable separation ([14](14-private-equity.md)) |

Sources: [Pricing](https://claude.com/pricing), [Custom retention](https://support.claude.com/en/articles/10440198-custom-data-retention-controls-for-claude-enterprise) (Enterprise only; doesn't apply to Claude Tag, Managed Agents or cloud Claude Code), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention) (covers Claude Code on Enterprise, not chat or Cowork), [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) (API skills not eligible; self-hosted Managed Agents is the ZDR exception; HIPAA readiness), [HIPAA setup](https://code.claude.com/docs/en/hipaa-setup), [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) (`inference_geo`, set per workspace). The org split itself is our recommendation.

**Start with three orgs:** 1, 2 and 3. Add 4 when needed, and N only for hard walls.

### Team-plan variant: a non-regulated role (our recommendation)

A customer on **Team** whose twins handle only internal and confidential data (for example a customer-success twin) needs **one Team org and no ZDR org**. It replaces orgs 1 to 3: there is no deal data, so no org 2, and no org 3 unless a hosted twin is in scope. This is the case [09](09-plans-and-it-controls.md) designs for ("Design twins to work on Team").

| # | Org | Plan type | For | Key settings | When |
|---|---|---|---|---|---|
| 1T | **General (Team)** | Claude Team | Customer success and other non-regulated roles | SSO (⚠ **Conflict:** the docs disagree on SSO for Team, see [09](09-plans-and-it-controls.md)); Owner-added connectors with per-tool permissions; org-wide skills and plugins, shared to everyone (no group targeting); usage dashboard; server-managed settings for Claude Code, the same for every user; Claude Tag allowed | Day 1 |

What Team lacks compared with org 1: SCIM, custom retention, audit logs, the Compliance API and group targeting are Enterprise only. If the customer must log every action, see [13](13-devices.md#team-plan-with-no-device-management).

Sources: [Pricing](https://claude.com/pricing), [Plugin admin](https://claude.com/docs/plugins/admin), [Connectors](https://claude.com/docs/connectors/getting-started.md), [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md), [Custom retention](https://support.claude.com/en/articles/10440198-custom-data-retention-controls-for-claude-enterprise), [Claude Tag](https://claude.com/docs/claude-tag/overview.md) (Team and Enterprise, public beta).

⚠ **Ask Anthropic:**

- Can a Platform org and an Enterprise org share administration, or are they fully separate?
- Can ZDR apply to part of an Enterprise org?

If either answer is yes, the count may drop.

## The ask, quantified (fill in)

| Item | Org 1 General | Org 2 Private equity | Org 3 Build / hosted | Org 4 HIPAA (later) |
|---|---|---|---|---|
| Plan | Enterprise | Enterprise | Platform (usage-based) | Enterprise or Platform |
| Pilot seats | ___ sales + ___ CS + ___ ops | ___ deal team members | n/a (API usage) | ___ |
| Contract add-ons | Claude Tag (beta) | ZDR addendum; CMEK (optional) | ZDR addendum; self-hosted Managed Agents access (by request) | BAA |
| Connectors | Salesforce, HubSpot, Google, M365, Slack | Salesforce, HubSpot, SharePoint/Drive (per-user only) | Built or wrapped MCP servers | Built servers only |
| Technical owner and backup | Director of IT / ___ | Director of IT / ___ | Director of IT / ___ | Director of IT / ___ |
| Business owner | RevOps manager | RevOps manager (compliance signs off on retention and walls) | RevOps manager | RevOps manager (compliance signs off) |
| Optional | MCP tunnels (Enterprise, research preview, by request) for private-network systems | | | |

Sources: [Claude Tag](https://claude.com/docs/claude-tag/overview.md) (public beta), [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) (ZDR is arranged by contract), [Self-hosted Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access) (access through your Anthropic account team), [MCP tunnels](https://claude.com/docs/connectors/mcp-tunnels/overview.md) (Enterprise, research preview, by request).

(Our recommendation) Pilot with 5 to 10 people per role. That's enough variety to find where skills fail, and few enough to interview everyone.

## Questions to bring to Anthropic (as a partner)

These are the points where Anthropic's own docs conflict, or the research couldn't confirm them.

1. Is the **Agent SDK** covered under ZDR and HIPAA? No page says so.
2. Is the **Claude Code CLI** covered under HIPAA? The API data-retention page and the BAA article disagree.
3. Can **Enterprise ZDR** extend to chat and Cowork for our private-equity org? Today it covers Claude Code only.
4. Can a Platform org and an Enterprise org be **linked**, and can ZDR be set **per workspace or group**?
5. Can **Project and chat sharing** be restricted **per group** (for information barriers)?
6. Which models are **"Covered Models"** that require 30-day retention, and which models qualify for ZDR?
7. How do we get access to **self-hosted Managed Agents**?
8. Does **Team include SSO**? Do **Free plans get custom skills**? Is there **data residency for claude.ai**? (See the conflicts in [09](09-plans-and-it-controls.md).)
9. Are **Salesforce and HubSpot** listed in the Claude directory, and does the Google Drive connector support **shared drives**?
10. Is a **Claude Tag** setup possible that keeps per-user identity, for teams with walls?

These are open questions, not facts. The pages they rest on: [API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), [Claude Code ZDR](https://code.claude.com/docs/en/zero-data-retention), [HIPAA setup](https://code.claude.com/docs/en/hipaa-setup), [Self-hosted Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access), [Tag identity](https://claude.com/docs/claude-tag/concepts/agent-identity.md).

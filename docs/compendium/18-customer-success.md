# 18 — Customer success: Anthropic's customer-support plugin, connectors and typical tasks

Page [16](16-oob-skills-and-references.md) recommends starting the customer-success twin from Anthropic's `customer-support` plugin in [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins). This page is the review of that plugin for a customer-success manager at a B2B software company on a **Team** plan, with HubSpot, Google Workspace, Slack, a ticketing system and product-usage data. It lists every part of the plugin, follows every connector it ships, says which connectors the role needs, and gives the role's typical tasks. It is the source for the `b2b-software` industry pack.

**What was reviewed.** Commit [`e91a134584eb798bac7fb0379358006a2b63b965`](https://github.com/anthropics/knowledge-work-plugins/commit/e91a134584eb798bac7fb0379358006a2b63b965) on `main` (2026-11-13), read on 2026-11-15 through the GitHub API. The plugin is at version `1.3.0` in its [plugin.json](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/.claude-plugin/plugin.json). The last commit that touched the plugin folder is [`c71b6f3`](https://github.com/anthropics/knowledge-work-plugins/commit/c71b6f3082b1e5ace3d1a9e30ac9205934134c9c) (2026-09-21). The plugin's licence is Apache-2.0 ([LICENSE](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/LICENSE)). Every file link below is pinned to the reviewed commit.

Verdicts: **take** (use as shipped, apart from the frontmatter and length fixes every copy needs), **adapt** (change it, and we say what), **skip** (don't use, and we say why). All verdicts are (our recommendation).

## The short answer

- **Five skills, no separate commands, no agents, no hooks.** Each skill is its own slash command (it has an `argument-hint`). The plugin has no `commands/`, `agents/` or `hooks/` folder.
- **It is a support-desk plugin, not a customer-success one.** Three skills help a customer-success manager and are adapted: `customer-escalation`, `draft-response` and `customer-research`. `ticket-triage` and `kb-article` are support-team work and are skipped.
- **It ships eight connectors.** Slack, Intercom, HubSpot, Guru, Atlassian and Notion are remote MCP servers with a URL. Gmail and Google Calendar are listed with an empty URL, so the user connects Claude's own connectors for them. It ships no Google Drive, no Zendesk and no data vendor.
- **No skill takes as shipped.** Every skill body is 248 to 418 lines, and the kit's limit is under 150 ([`test_kit_structure.py`](../../tests/test_kit_structure.py)). Every description is 246 to 297 characters, over the 200 that page [03](03-skills-authoring.md) sets. Every frontmatter has `argument-hint`, which isn't one of the cross-surface keys (page 03). Our copy fixes all three.
- **Mail and calendar are read-only on claude.ai.** The Gmail and Google Calendar connectors can't draft, send or book ([11](11-connectors.md#what-exists-for-our-systems)). So every email task below ends in a draft in the conversation that a person sends.
- **Most of the role's tasks come from the `sales` plugin, not this one.** Account briefs, renewals and call follow-up match skills in `sales` (`account-context`, `call-prep`, `renewal-radar`, `customer-health`, `call-summary`, `log-activity`). We list it as a reference, not a starting point, because this page doesn't review it.

## What's in `customer-support`

Links: [plugin.json](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/.claude-plugin/plugin.json), [.mcp.json](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/.mcp.json), [CONNECTORS.md](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/CONNECTORS.md), [README.md](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/README.md).

| Skill and command | What it does | Reaches outside the laptop? | Verdict |
|---|---|---|---|
| [customer-escalation](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/skills/customer-escalation/SKILL.md), `/customer-escalation` | Packages an issue into an escalation brief for engineering, product or leadership: reproduction steps, business impact (including ARR at risk), the target team and a follow-up cadence | Reads the support platform, CRM, chat, project tracker and knowledge base. Offers to post the brief in a chat channel and to draft a customer update | **Adapt** (C5). Point it at Zendesk and HubSpot, use the customer's escalation tiers and targets, and post to Slack only after a person approves |
| [draft-response](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/skills/draft-response/SKILL.md), `/draft-response` | Drafts a customer-facing reply for the situation and channel, with internal "do not send" notes on what to check first | Reads email, chat, CRM, support platform and knowledge base. It drafts; it doesn't send | **Adapt** (C3, C4). Add the customer's tone, signature and renewal and follow-up templates. Keep it draft-only |
| [customer-research](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/skills/customer-research/SKILL.md), `/customer-research` | Answers a customer question from several sources, ranks the sources and gives a confidence level | Reads the knowledge base, cloud storage, CRM notes, support platform, chat and email, **and web search** | **Adapt.** Keep the source ranking. Limit it to connected systems, with web search only for public product facts, because a query can carry the customer's name |
| [ticket-triage](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/skills/ticket-triage/SKILL.md), `/ticket-triage` | Categorises a new ticket, gives it a P1 to P4 priority, routes it and checks for duplicates | Reads the support platform, knowledge base and project tracker | **Skip.** Triage of incoming tickets is the support team's job, not the customer-success manager's |
| [kb-article](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/skills/kb-article/SKILL.md), `/kb-article` | Drafts a knowledge-base article from a resolved issue, with a review and upkeep cadence | Reads the support platform, knowledge base and project tracker | **Skip.** Help-centre content belongs to the support or documentation team |

Notes that apply to the whole plugin:

- **⚠ Conflict:** the [README](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/README.md) lists five commands (`/triage`, `/research`, `/draft-response`, `/escalate`, `/kb-article`) and five skills with other names (`ticket-triage`, `customer-research`, `response-drafting`, `escalation`, `knowledge-management`). The skill folders are `customer-escalation`, `customer-research`, `draft-response`, `kb-article` and `ticket-triage`, and there is no `commands/` folder. We go by the files.
- **⚠ Conflict:** the README and [CONNECTORS.md](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/customer-support/CONNECTORS.md) say email and cloud storage come from Microsoft 365. The `.mcp.json` has no Microsoft 365 entry; it was removed in [#285](https://github.com/anthropics/knowledge-work-plugins/commit/181c4f6ff5a246f776027dcd79e2b330b68bf3be). It lists Gmail and Google Calendar instead. We go by the file.
- **Placeholders.** The skills name a category (`~~support platform`, `~~CRM`, `~~chat`), not a product, so any connector in that category works. CONNECTORS.md names Zendesk as an "other option" for the support platform.

## Where the data goes: connectors and external tools

Each connector call sends its arguments (an account name, a ticket number, a question) to the server's host, and the answer enters the conversation, which is sent to Anthropic ([10](10-sensitive-data.md#first-running-locally-doesnt-keep-data-local)). Whether a plugin's remote server is called from the laptop or from Anthropic is the open point on page [17](17-anthropic-pe-plugins-review.md#3-where-the-data-goes-connectors-and-external-tools).

| Connector (from `.mcp.json`) | Host | Who runs it | Identity | For a customer-success twin |
|---|---|---|---|---|
| `slack` | `https://mcp.slack.com/mcp`, with Anthropic's Slack OAuth client ID | Slack | Per user (user tokens); a Slack admin approves the client ([11](11-connectors.md#what-exists-for-our-systems)) | **Yes**, for internal context and the team-channel digest |
| `intercom` | `https://mcp.intercom.com/mcp` | Intercom | Per user via OAuth, or a bearer token ([11](11-connectors.md#what-exists-for-our-systems)) | Only if the customer runs Intercom. Remove it otherwise |
| `hubspot` | `https://mcp.hubspot.com/anthropic` | HubSpot | Per user via OAuth, within the user's HubSpot permissions ([11](11-connectors.md#what-exists-for-our-systems)) | **Yes**, the CRM |
| `guru` | `https://mcp.api.getguru.com/mcp` | Guru | ⚠ Unverified: not fetched. A Guru page on its sign-in model would confirm it | Only if the customer uses Guru, after the review on page [11](11-connectors.md#buying-a-connector-and-reviewing-it) |
| `atlassian` | `https://mcp.atlassian.com/v1/mcp` | Atlassian (Jira and Confluence) | ⚠ Unverified: not fetched. An Atlassian page on its sign-in model would confirm it | Only if the customer tracks bugs in Jira, after the page 11 review |
| `notion` | `https://mcp.notion.com/mcp` | Notion | ⚠ Unverified: not fetched. A Notion page on its sign-in model would confirm it | Only if the customer keeps its knowledge base there, after the page 11 review |
| `google calendar` | Empty URL; the user connects Claude's Google Calendar connector | Google | Per user via OAuth; read-only ([11](11-connectors.md#what-exists-for-our-systems)) | **Yes**, read-only |
| `gmail` | Empty URL; the user connects Claude's Gmail connector | Google | Per user via OAuth; read-only ([11](11-connectors.md#what-exists-for-our-systems)) | **Yes**, read-only |

Every server with a URL is the vendor's own domain; none is an aggregator. None is a third-party data vendor of the kind page 17 found: each one holds the customer's own data. The empty-URL entries follow the `sales` plugin's [CONNECTORS.md](https://github.com/anthropics/knowledge-work-plugins/blob/e91a134584eb798bac7fb0379358006a2b63b965/sales/CONNECTORS.md), which says to "Connect them in Claude's connector settings"; the `customer-support` CONNECTORS.md doesn't say this.

| Other external tool a skill asks for | Used by | Where data goes | For a customer-success twin |
|---|---|---|---|
| Web search | `customer-research` | The search provider and the sites fetched; the query can name the customer | Public product facts only (adapt, above) |
| Posting to a chat channel | `customer-escalation` (it offers) | Slack | Only after a person approves the post |

## The connectors a customer-success role needs

The facts are in the rows on page [11](11-connectors.md#what-exists-for-our-systems); this table only maps the role to them.

| System kind | Product | Row on page 11 | What the role uses it for |
|---|---|---|---|
| CRM | HubSpot | [HubSpot](11-connectors.md#what-exists-for-our-systems) | Accounts, contacts, deals, renewal dates, call notes |
| Documents | Google Drive | [Google Drive / Sheets](11-connectors.md#what-exists-for-our-systems) | Account plans, QBR decks, contracts, call notes |
| Email and calendar | Gmail, Google Calendar | [Gmail](11-connectors.md#what-exists-for-our-systems), [Google Calendar](11-connectors.md#what-exists-for-our-systems) | Recent threads with the customer; the next meeting and its attendees (both read-only) |
| Messaging | Slack | [Slack](11-connectors.md#what-exists-for-our-systems) | Internal context; the weekly digest |
| Ticketing | Zendesk (Intercom where the customer uses it) | [Zendesk](11-connectors.md#what-exists-for-our-systems), [Intercom](11-connectors.md#what-exists-for-our-systems) | A customer's open tickets |
| Product data | Internal usage database | [Product-usage data](11-connectors.md#what-exists-for-our-systems) | Usage trends behind renewal risk. Our own MCP server ([11](11-connectors.md#building-our-own-mcp-server)) |

## Typical customer-success tasks (our recommendation)

The data class comes from page [10](10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)'s matrix: CRM data and customer contracts are **Confidential**, and Team is acceptable for that class where the audit need is lower. Triggers are the persona card's: person, schedule-team, event.

| Id | Task | Reads | Writes | Trigger | Data class | Layers on |
|---|---|---|---|---|---|---|
| C1 | **Account brief** before a customer call | HubSpot (company, contacts, deals, open tickets, notes); Google Drive (account plan, last QBR deck, contract) | Nothing: the brief stays in the conversation | Person, before the call | Confidential | `account-context` and `call-prep` in `sales` (reference) |
| C2 | **Weekly renewal-risk digest** to a team channel | HubSpot (renewal dates, deal stage, contacts); the product-usage database (usage trend per account) | One Slack post in the team's channel | Schedule, for the team (weekly) | Confidential | `renewal-radar` and `customer-health` in `sales` (reference) |
| C3 | **Renewal quote email** | HubSpot (the renewal deal, line items, products, quote) | A draft email in the conversation, which the manager sends | Person | Confidential | `draft-response` (adapt) |
| C4 | **Follow-up email and CRM call note** | The call notes or transcript, in Google Drive | A draft email in the conversation; a call or note on the HubSpot record | Person, after the call | Confidential | `draft-response` (adapt); `call-summary` and `log-activity` in `sales` (reference) |
| C5 | **Open-ticket summary on escalation** | Zendesk (the customer's open tickets) | Nothing at first: the summary stays in the conversation | Event: an escalation | Confidential | `customer-escalation` (adapt) |

What the rows rest on:

- **C2 needs a runtime that runs on a schedule and a Slack write.** Page [05](05-decision-matrix.md) covers when a scheduled job earns a hosted runtime. The Slack directory connector's page documents only search, so posting through it is ⚠ Unverified ([11](11-connectors.md#what-exists-for-our-systems)); the Slack MCP server can send. On Team, the usage database has no MCP tunnel, so it must be reachable from Anthropic's IP range or the job runs inside the network ([11](11-connectors.md#what-exists-for-our-systems)).
- **C3 touches money.** HubSpot's quote tools are in beta, and the Gmail connector can't draft or send ([11](11-connectors.md#what-exists-for-our-systems)). The manager checks the figures and sends from Gmail.
- **C4's HubSpot write** is a create on an engagement, which the HubSpot connector supports. HubSpot recommends setting write tools to Needs approval ([11](11-connectors.md#what-exists-for-our-systems)). Start it there (page [06](06-autonomy.md)).
- **C5's event has no confirmed source.** No page we fetched shows a Zendesk escalation starting a Claude session. ⚠ Unverified: what would fire it (a Zendesk trigger calling a hosted agent, or a Slack alert to Claude Tag). Until that is confirmed, the manager starts it when told of the escalation. The Zendesk connection is also in early access ([11](11-connectors.md#what-exists-for-our-systems)).
- **C2 and C5 read untrusted content** (ticket text, usage data) next to a way to send (Slack). Check 10 on page [11](11-connectors.md#buying-a-connector-and-reviewing-it) applies: a person approves each post.

## What changes on a Team plan

The Team facts live on their own pages; read them there.

- Plan features and IT levers: [09, feature matrix](09-plans-and-it-controls.md#feature-matrix) and [09, what IT can do on each plan](09-plans-and-it-controls.md#what-it-can-do-on-each-plan).
- How many orgs: [12, Team-plan variant](12-orgs-and-ownership.md#team-plan-variant-a-non-regulated-role-our-recommendation).
- Devices without MDM: [13, Team plan with no device management](13-devices.md#team-plan-with-no-device-management).
- Governance and logging: [15, Team plan with no device management](15-governance-and-performance.md#team-plan-with-no-device-management).

What is new on this page for Team: each connector above needs an Owner to turn it on for the org, HubSpot also needs a HubSpot Super Admin's approval, and the usage database can't use an MCP tunnel. All three are on the rows on page [11](11-connectors.md#what-exists-for-our-systems).

Sources: [sources.md](sources.md), section "Customer success (page 18)".

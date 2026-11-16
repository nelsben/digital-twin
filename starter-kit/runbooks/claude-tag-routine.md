# Runbook: set up a Claude Tag routine in a Slack channel for a twin's task

## What this is

Claude Tag is Claude working in a team's Slack channels. A routine is standing work you ask for from a channel: a scheduled job, a channel watch, or a subscription to a single pull request. ([B]) It runs on the channel's own connections, with the same permissions as a typed request, and keeps running if the person who set it up leaves the channel. ([B]) Claude Tag is in public beta: features and behaviour may change before general availability. ([K], [B]) This runbook takes the engagement's decisions for one task (see "Inputs you need") and sets up the Slack side, the connections and the routine. It is generic: replace every `<placeholder>` with the customer's value.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Slack admin** | Source-system admins (the Slack workspace admin) |
| **Requester** | Business owner, or the channel's own leader: asks for the routine and judges its output |
| **Source-system admin** | Source-system admins: creates the service account in each connected tool |
| **Compliance** | Compliance / legal: confirms the data class and who may read the channel |
| **Security** | Security (CISO or security engineer) |
| **Skill owner** | Skill owners: keep the skill that holds the task's instructions |
| **Partner skill engineer** | Skill engineer (partner role) |
| **Partner integration engineer** | Integration engineer (partner role) |

## Read this first

How sources are marked: each numbered step and each product fact ends with the pages it came from, as tags like ([A], [B]) that the list below defines. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; the item says what would confirm it. Confirm each one at setup, then replace the mark with the page you checked. Menu paths, setting names, limits and commands are copied from the pages as read on 2026-11-16.

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Set up Claude Tag](https://claude.com/docs/claude-tag/admins/setup-overview)
- [B] [Set up routines](https://claude.com/docs/claude-tag/users/proactivity.md)
- [C] [How agent identity works](https://claude.com/docs/claude-tag/concepts/agent-identity.md)
- [D] [Personal connectors in channels](https://claude.com/docs/claude-tag/concepts/personal-connectors.md)
- [E] [What Claude Tag remembers](https://claude.com/docs/claude-tag/users/memory.md)
- [F] [Review what Claude Tag has done](https://claude.com/docs/claude-tag/admins/audit.md)
- [G] [Give Claude access to your tools](https://claude.com/docs/claude-tag/admins/add-connections.md)
- [H] [Connect a service that isn't in the list](https://claude.com/docs/claude-tag/admins/connections/custom.md)
- [I] [Restrict where Claude Tag operates](https://claude.com/docs/claude-tag/admins/restrict-access.md)
- [J] [Claude Tag settings map](https://claude.com/docs/claude-tag/concepts/settings-map.md)
- [K] [Work with Claude Tag (overview)](https://claude.com/docs/claude-tag/overview.md)
- [L] [Compendium 05, hosted agent or client skill](../../docs/compendium/05-decision-matrix.md)
- [M] [Compendium 06, autonomy](../../docs/compendium/06-autonomy.md)
- [N] [Compendium 10, sensitive data](../../docs/compendium/10-sensitive-data.md)
- [O] [Compendium 11, connectors](../../docs/compendium/11-connectors.md)

## Inputs you need

The engagement has already decided these for the task. The steps consume them; if one is missing, stop and ask the Requester.

- **Runs as:** the channel's own access, not a person: Claude's own service accounts, the same whoever asks. In a group DM it is the same. In a one-to-one DM it runs on that person's own claude.ai account. ([C]) Compendium [05](../../docs/compendium/05-decision-matrix.md) compares this with a Claude Code scheduled task. ([L])
- **Autonomy level:** the level it starts at and its ceiling, from [06](../../docs/compendium/06-autonomy.md). In Claude Tag the ceiling is what each service account may do. ([G], [M])
- **Data class:** the class and what follows from it: which surfaces are allowed and what retention applies, per the matrix in [10](../../docs/compendium/10-sensitive-data.md). Claude Tag is not available to an organization with Zero Data Retention, customer-managed encryption keys or the HIPAA configuration. ([A], [N])
- **Connectors:** each connector or MCP server the task uses and, for each, the service account and whether it may read or write. ([G])
- **Schedule or trigger:** the cadence and time zone, or the channels and topic to watch, or the one pull request to follow, and the channel where results post. ([B])
- **Memory:** on or off for the channel. Memory is per channel and anyone in the channel can read and change it; from a public channel Claude can also save workspace notes, which it reads in every channel, private ones included. ([E])
- **Skill:** the name of the skill that holds the task's instructions and the plugin that carries it. ([G])

## Before you start

- The organization is on a Team or Enterprise plan on Anthropic's first-party service, and is not on ZDR, CMEK or the HIPAA configuration. ([A], [K])
- **Routines** is on for the organization at **Organization settings > Capabilities > Remote sessions > Routines**; until it is, Claude answers every mention with a reply that it is unavailable and does no work. ([A])
- The person running setup has the **Owner** role in the Claude organization, a Slack workspace admin is available, and on a Team plan usage credits are loaded. ([A])
- A public Slack channel exists for the pilot. ([A])

## Steps

1. **Who: Claude org Owner with the Slack admin.** Pair and launch if not done: at `claude.ai/admin-settings/claude-tag` click **Start setup**; add the Claude app from claude.com/claude-for-slack; in any channel run `/invite @Claude`, then send `@Claude connect` with no other text; paste the code (valid for 15 minutes) into **Paste the pairing code**, click **Pair workspace**, then **Launch Claude Tag**. ([A])
2. **Who: Compliance with the Slack admin.** Check who can read the channel against the data class before any connector is added: follow [10](../../docs/compendium/10-sensitive-data.md) for what the class allows, and for the channel confirm its members, that no Slack guest is in it (by default Claude is off in a channel with a guest), and that it is not a Slack Connect channel (the guests setting, **How should Claude work in channels with guests**, decides whether Claude answers there, where **Restrict** posts no notice; routines are not set up and do not run there; guests can read what Claude posts). **⚠ Unverified:** the Slack menu path to list a channel's members and guests; confirm on a slack.com/help page or in the Slack admin console. ([I], [B])
3. **Who: Source-system admin.** For each tool the task needs, create a dedicated service account (not a personal login) scoped as narrowly as the autonomy level needs, because anyone in a channel where the connector applies can use it through Claude and Claude can never exceed what the key allows. ([G])
4. **Who: Claude org Owner.** Go to **Organization settings > Claude Tag**; under **Claude's access** select the **Connectors** tab, click **Add**, pick the service (or **Custom connector**) and enter the credential; on the form's **Advanced** tab check **Allowed websites**, then click **Connect**. ([G], [H])
5. **Who: Claude org Owner.** Limit where the connector applies: a first credential is on in every workspace and channel, so on the connector's page clear it on the **Slack** row under **Assign access**, then **Add place** for this channel only and **Save changes**; or put it in its own bundle (**Bundles** tab, **Add**) whose **Where it applies** lists only this channel. ([G])
6. **Who: Partner integration engineer.** For an MCP server, use a plugin plus a credential: add a plugin whose `.mcp.json` points at the server URL, from the organization's library or a skills repository, and add a custom connector for the server's host (for example a Bearer credential with **Allowed websites** set to the host) where the plugin applies. The server must be a remote URL (not stdio), and an `.mcp.json` checked into a repository Claude clones is not loaded. ([H], [O])
7. **Who: Partner integration engineer.** Pick the credential type for each server host from the **Credential type** list: **Bearer**, **Basic**, **Body parameter**, **AWS SigV4**, **GCP access token (with Service Account Key)**, **GCP IAP (with Service Account Key)**, **OAuth 2.0 JWT bearer**, **OAuth 2.0 client credentials**, or **MCP Connector** (one admin's sign-in, the agent then acts as that account). ([H])
8. **Who: Partner skill engineer.** Attach the skill's plugin where the task runs: on the **Skills and plugins** tab click **Add** (then **Assign access** to limit it), or on a bundle's page under **What's in it** click **Add** and choose **Plugin**; the change applies to new threads only. ([G])
9. **Who: Requester.** In the channel, create a scheduled job by describing the schedule and the work in one message, for example `@Claude every weekday at 9am Pacific, ...`, naming the time zone (schedules run in UTC; with none named Claude uses the one on your Slack profile) and the output format; a job runs at most once an hour and Claude declines anything more often. ([B])
10. **Who: Requester.** Or create a watch by naming the channels and the topic (`@Claude watch #channel-a and #channel-b. Once a day, post here if ...`), or follow one pull request (`@Claude subscribe to PR #<n> in <org>/<repo>. ...`); a subscription is the only GitHub event trigger, and a watch of other channels works only where Claude has been added. ([B])
11. **Who: Requester.** Set it up from inside a thread, or ask for results there, so each run reports in that thread; a routine started at the top level announces each run in a short top-level message and works in the thread under it. ([B])
12. **Who: Requester.** If the task needs memory, say `@Claude remember for this channel: <instruction>` and keep it short; Claude also saves facts itself, anyone in the channel can list, change or forget entries, and an Owner can view, edit or delete them under **Activity** (the **Memory** tab). **⚠ Unverified:** a setting that turns channel memory off; none appears on the pages read, so confirm with Anthropic if the engagement decided "memory off". ([E], [F])
13. **Who: Security.** Hold the routine to its level: it uses the channel's connections and never a member's personal connectors, so the level is the narrowest service account plus the scope of the channel's connectors; the **Tools and access** tab of the channel's **Configure** page shows what is resolved. An Owner can add plain-sentence **Auto mode allow rules** per scope. ([D], [G], [J])
14. **Who: Partner integration engineer.** Note where the record of a run is: the routine's posts in the channel, the **Scheduled work** tab of the Activity page at `claude.ai/admin-settings/claude-tag/audit`, each connected tool's own audit log under the service account, and on Enterprise with the Compliance API enabled the session transcripts. ([F])
15. **Who: Requester.** Record how to pause and remove it: ask in the channel (`@Claude !scheduled` lists the routines in UTC; "disable the Friday rollup" or "move the standup summary to 10am Pacific" changes one), or an Owner uses **Pause** or **Resume** or **Delete** in a row's **⋮** menu on the **Scheduled work** tab. ([B], [F])

## Check it worked

**Who: Requester, with the Partner skill engineer watching. About ten minutes.** Use a harmless test input agreed with Compliance. A routine runs at most hourly, so the first scheduled run is checked afterwards (last row).

| # | Do this | Pass if |
|---|---|---|
| 1 | Send `@Claude !scheduled` in the channel | The routine is listed with its schedule in UTC, and the UTC time matches what you asked for. ([B]) |
| 2 | Type the routine's work as a request in the channel | The answer is what the Requester expects. A job runs with the channel's connections, the same as an interactive request, so this checks the same access. ([B]) |
| 3 | Open the **Activity** page, **Scheduled work** tab, and choose **View details** on the row | **Created by** names the Requester and the scope is this channel. ([F]) |
| 4 | Look in the connected tool's own audit log | The test read appears under the service account, not under a person. ([F], [C]) |
| 5 | Ask Claude for something the service account must not do (for example a write at level 1) | Claude cannot do it. If it can, narrow the account and repeat. ([G]) |
| 6 | After the next hour boundary, read the routine's post | The scheduled run posted in the place chosen in step 11. ([B]) |

## Hand over

**Who: Partner skill engineer to the Requester and the Claude org Owner.** In the customer's folder under `engagements/<customer>/`, record: the workspace and channel; the routine's exact message and its schedule in UTC; who created it; the connectors, the service account for each and read or write; the plugin and bundle names; any memory entries saved; the data class and the date of the channel-readers check; the result and date of each check above; and the unverified items still open.

After set-up the channel owns it: a channel's routines keep running if their creator leaves the channel or the organization, and anyone still in the channel can disable them. ([B]) Name the Requester as the person who answers for it, and the Claude org Owner as the person who can pause or delete it from the Activity page. ([F]) A routine set up in a one-to-one DM belongs to that person's account and is turned off when they are removed from the organization, so do not use a DM for a shared task. ([B])

## What can go wrong

- **Claude declines the schedule.** The minimum is once an hour. ([B])
- **The local time moves.** Routines run at a fixed UTC time, so a daylight saving change shifts the local time by an hour; ask Claude to reschedule. ([B])
- **No run in the channel.** In a Slack Connect channel Claude sets up no routines, and routines set up before the channel was shared do not run there; a guest in the channel also turns Claude off by default. ([I])
- **Output goes nowhere.** Claude does not post a channel job's output into a different private or externally shared channel, into a DM, or to people directly; a group DM routine posts in that group DM only. ([B])
- **Claude says it cannot use a credential.** In the connector's **Access from** table, **Not enabled** means no rule sends it yet: click **Enable** and confirm. A host that none of the allow layers covers is blocked. ([H], [G])
- **A new plugin or connector is not picked up.** A running thread keeps the plugins it began with; start a new thread. ([G])
- **A member's own connector is not used.** Routines and other work Claude starts on its own never use a member's personal connectors. ([D])
- **A missed or failed run.** **⚠ Unverified:** whether a run missed while Claude Tag was down is replayed, and where a failure shows; Claude sends a completion or failure notice to whoever set up the routine when their Slack account is connected to their Claude account, so plan a reconcile check ([06](../../docs/compendium/06-autonomy.md)). ([B])
- **The beta changes.** Re-read [B] and [G] before each new engagement. ([K])

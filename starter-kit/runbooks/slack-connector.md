# Runbook: Connect Slack to a role's twin (reading and searching Slack)

## What this is

A role's twin searches the customer's Slack workspace for context, through Claude's Slack connector in claude.ai. This runbook takes the Slack admin, the Claude org Owner and our integration engineer from app approval to a tested read and a tested permission setting. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states, see the [Slack row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems).

This runbook covers the **Slack connector**: Claude, in claude.ai, searching Slack. It does not cover **Claude Tag**, which is Claude working inside Slack as one shared teammate that people tag into a channel ([E]). Claude's own page calls Claude Tag the current product and the per-user Claude in Slack app the earlier one ([A]). For Claude Tag, use [claude-tag-routine.md](claude-tag-routine.md). Release status: Claude Tag shows "Public Beta" on its overview page ([E]). **⚠ Unverified:** the connector's own release status, and who publishes the connector; [A] says neither.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Slack admin** | Source-system admin (03-stakeholders lists Salesforce, HubSpot, M365 and Google admins; for Slack, the Workspace Owner or app manager, named by the Director of IT; by default only Workspace Owners review app requests ([D])) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Business owner** | Business owner (RevOps manager, or the role's own leader) |
| **Security** | Security (CISO or security engineer) |
| **Partner integration engineer** | Integration engineer (partner role) |
| **Pilot user** | Pilot users (5 to 10 per role) |

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.

Pages used:

- [A] [Slack integration (Claude docs)](https://claude.com/docs/connectors/slack/index.md)
- [B] [Slack MCP server overview (Slack developer docs)](https://docs.slack.dev/ai/slack-mcp-server.md)
- [C] [Admin approval for apps with MCP servers (Slack developer docs)](https://docs.slack.dev/ai/slackbot-mcp-client/admin-approval/)
- [D] [Manage app requests for your workspace (Slack Help Center)](https://slack.com/help/articles/360024269514-Manage-app-requests-for-your-workspace)
- [E] [Work with Claude Tag (Claude docs)](https://claude.com/docs/claude-tag/overview.md)
- [F] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [G] [Use connectors to extend Claude's capabilities (Claude help center)](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [H] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role and the Claude group that gets the connector (the role's pilot users only).
- Which Slack workspace or workspaces the Claude app is deployed to, or the whole organization. Step 1 offers both ([A]); the Slack admin and Security decide, and the answer is recorded.
- The test record for the write test: one named test channel, and the text `connector write test`, so any post can be found and removed afterwards.
- For each task: which channels, direct messages and files it reads. The connector's page documents search only ([A]); whether it also exposes send tools is unconfirmed (step 5), so do not plan a task that posts to Slack on this connector until the tool list is recorded.
- For each tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)). Level 1 (Draft) keeps write tools **Blocked**; level 2 sets them to **Needs approval**. If the connector has no send or write tool, there is nothing to set.
- The data class of the tasks that use it ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)). Internal chat can hold Confidential material, so the class is the highest one a searched channel can hold.
- Whose identity the connector acts under: each pilot user connects their own account ([A]).
- The surfaces the role works in: claude.ai, the desktop app, mobile, or Claude Code ([F]). This runbook covers the claude.ai surfaces. In Claude Code the connection comes from the role plugin's `.mcp.json`, not from these steps: the `customer-support` plugin's `slack` entry points to `https://mcp.slack.com/mcp` with Anthropic's Slack OAuth client ID, and a Slack admin approves that client ([page 18](../../docs/compendium/18-customer-success.md)). That is the Slack MCP server route, not the directory connector. [F] adds that connectors added in claude.ai are also available in Claude Code when the user signs in with their Claude account.
- Whether the task also posts to Slack. That is a different product and runbook (Claude Tag), or a write tool on the Slack MCP server, and the compendium's rule 10 on [page 11](../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it) is conditional: do not give one twin both untrusted content and a way to send it out unless a person approves each send. Channel text is untrusted input.

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | The connector is available on Team and Enterprise plans and requires the Claude in Slack app to be installed first. | Claude org Owner | [A] |
| 2 | The Claude in Slack app is available to users on paid Slack plans, and a Slack admin must approve it for the workspace before individual users can connect. | Slack admin | [A] |
| 3 | By default only Workspace Owners can review app requests; an Owner can appoint other members as app managers. | Slack admin | [D] |
| 4 | Slack's MCP server accepts only apps published in the Slack Marketplace and internal apps. **⚠ Unverified:** whether this applies to Claude's connector; nothing we read says the connector goes through the MCP server. | Slack admin | [B] |
| 5 | If the customer uses an IP allowlist: API calls from IP addresses not on the allowlist are rejected. **⚠ Unverified:** whether the connector's calls pass through this check, and which addresses Claude's calls come from; ask Anthropic. | Security | [B] |

## Steps

1. Slack admin: install the Claude app. Open the Claude app's listing in the Slack App Marketplace, select **Add to Slack**, review and approve it, and choose to deploy it org-wide or to specific workspaces, as recorded in Inputs. ([A])
2. Slack admin: if approval is required, handle the request. The app appears in the **Requests** queue (the **Requests to install** tab on the Apps page); admins approve or restrict it from the Slack Marketplace management page, `https://slack.com/apps/manage`. Select **Review and Approve for Workspace** (choose any optional scopes, then **Approve**) or **Review and Restrict**. ([C], [D])
3. Slack admin: if the app has MCP servers, review them. On approval the admin sees the full list of requested scopes and a **Connected MCP Servers** section, and each server can be allowed or denied. **⚠ Unverified:** whether the Claude app or connector goes through this screen; [C] describes apps with MCP servers in general and does not name Claude. If no such section appears, record that. Re-approval is needed if a server from a different domain is added. Afterwards, **Integrations > Installed apps** shows each server as ALLOWED or INACTIVE. ([C])
4. Claude org Owner: enable the connector for the organization. Go to **Organization settings > Connectors** and enable the Slack connector. ([A]) The directory path in claude.ai is **Browse connectors**, then **Add to your team**, and adding grants no access by itself. ([G]) **⚠ Unverified:** whether a Team plan can show it to one Claude group; no page says so. On Enterprise, **Organization settings > Roles** > the role's **Connectors** tab sets each connector to **Always allow**, **Needs approval**, **Blocked** or **Custom**. **Custom** sets each tool on the connector individually, instead of one setting for the whole connector. The org-wide **Tool permissions** setting in step 5 is a ceiling: a role's setting can narrow it and cannot widen it, and where the two disagree the stricter one applies. Because the step 5 setting applies to every role that uses the connector, on a Team plan, which has no role setting, it must be the strictest any of those roles' tasks needs ([06-autonomy](../../docs/compendium/06-autonomy.md)); on Enterprise, set it to the loosest any role needs and narrow the other roles here. If a Team plan cannot limit it to the pilot group, the connector is visible to the whole organization: record that with Security as a risk before the pilot starts. ([H])
5. Claude org Owner, with the Business owner: set the tools. Go to **Customize > Connectors**, select Slack, and under **Tool permissions** choose **Always allow**, **Needs approval** or **Blocked** for each group or single tool; the setting applies org-wide and users cannot override it. ([G]) **⚠ Unverified:** the tool names. The connector page documents only search of channels, direct messages and files ([A]), and says nothing about sending. Slack's MCP server lists read operations (search messages and files, search users, search channels, read a channel, read a thread, read a canvas) and write operations (send message, schedule message, create a canvas, upload a file, add reactions), but names only `slack_get_file_upload_url` and `slack_complete_file_upload`. ([B]) Whether the connector exposes the write operations is not confirmed: read the real list on the connector's page and set every send or write tool to **Blocked** or **Needs approval**.
6. Pilot user: connect. Go to **Customize > Connectors**, find **Slack** and select **Connect**; the button then reads **Disconnect**. ([A]) The connector shows under **Your connectors** as **Connected**. **⚠ Unverified:** which permissions the sign-in screen lists; [A] names none. Copy the screen's list into the Hand over record. ([F])
7. Pilot user: turn it on in the chat. Select **+** at the lower left of the message box, select **Connectors**, and turn on **Slack**. ([A])
8. Partner integration engineer: write down the tool list and each tool's setting, with the date, for the record in Hand over. ([G])

## Check it worked

Run the tests in a pilot user's own Claude session, with the Partner integration engineer watching.

**Read test.** Ask "What did the team decide about the launch date in `#<test-channel>` last week?", naming a harmless test channel the user belongs to and a message seeded there. Expected: Claude answers from that channel. ([A]) Then ask about a private channel the user is not in (the Slack admin names one). Expected: nothing from it appears. **⚠ Unverified:** [A] does not state that results are limited to what the user can see; if the user sees more than Slack shows them, stop and escalate to Anthropic. See the [Slack row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems) for the compendium's position.

**Write test.** Ask Claude to post `connector write test` to the test channel. Expected, by the setting from step 5:

| Setting | Expected result |
|---|---|
| **Blocked**, or no send tool on the connector | Nothing is posted. Claude says it cannot. **⚠ Unverified:** the exact message; record what you see. If step 5 found no send tool, the **Needs approval** row cannot be run: record instead that the tool list shows no send tool, with the date. |
| **Needs approval** | Claude asks first; select **Allow once** to continue or decline. ([F]) Declining posts nothing. |

Never answer **Always allow**. Afterwards the Slack admin checks the test channel: any post that appears under a blocked or declined setting is a fail, so go back to step 5. Last, remove whatever the test created: delete any test post from the test channel by hand and name the channel in the Inputs record. ([F])

## Hand over

**Who: Partner integration engineer to the Slack admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- Who approved the Slack app, when, and which MCP servers were allowed (step 3).
- The connector's tool list, each tool's setting and the autonomy level behind it (step 5), and the pilot group.
- The permissions the sign-in screen listed (step 6).
- The read and write test results, with the date and users.
- The unverified items still open.

Offboarding and revocation, both sides. Claude: a user goes to **Customize > Connectors**, finds **Slack** and selects **Disconnect**; the Claude in Slack app has its own **Disconnect** on its **Home** tab in Slack, and disconnecting removes the account connection and deletes past conversations within 30 days. ([A]) An Owner removes the connector for the organization from **Organization settings > Connectors**. ([F]) Slack: **⚠ Unverified:** the approval pages ([C], [D]) describe approving and restricting an app, not removing an installed app or revoking its tokens; confirm in Slack's help center at setup.

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| No Slack connector for a member, or it will not connect | The Claude in Slack app is not installed yet, or an Owner has not enabled the connector. Install the app first. | [A] |
| A user sees **Request to install** instead of a connect screen | The workspace requires admin approval and the user is not an admin. A Slack admin approves the app, then the user connects. | [A] |
| The app waits in the queue | A Workspace Owner or app manager has not reviewed it under **Requests to install**. | [D] |
| Re-approval is asked for later | An MCP server from a different domain was added to the app. | [C] |
| Calls fail from the customer's network | Calls from addresses not on the Slack IP allowlist are rejected. | [B] |
| Someone expects the twin to post to Slack | The connector page documents search only, and posting is a different product (Claude Tag). Use [claude-tag-routine.md](claude-tag-routine.md), and keep a person approving each post. | [A], [E] |
| A twin reads untrusted channel text and can also send | Rule 10 on [page 11](../../docs/compendium/11-connectors.md#buying-a-connector-and-reviewing-it): do not give one twin both untrusted content and a way to send it out unless a person approves each send; this is the main prompt-injection route. Keep any send tool **Blocked** or **Needs approval**; if the connector has no send tool, record that. | [A] |

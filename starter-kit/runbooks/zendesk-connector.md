# Runbook: Connect Zendesk to a role's twin

## What this is

A role's twin looks up a customer's tickets in Zendesk, and may update them, through Zendesk's own MCP server, set up as an external AI connection (Zendesk Bridge). Zendesk publishes and runs it. This runbook takes the Zendesk admin, the Claude org Owner and our integration engineer from the Admin Center connection to a tested read and a tested write setting. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states, see the [Zendesk row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems).

Directory status: Zendesk's article lists Claude and Claude Code as pre-built providers ([A]). **⚠ Unverified:** whether Zendesk is listed in Claude's connector directory, and under what label. The listing address `claude.com/connectors/zendesk` returned a 404 on 2026-11-16, and the directory page we read names no Zendesk entry ([H]). Until Anthropic confirms a listing, treat it as a connector you add by URL, which Claude labels **Custom** and does not review ([F]).

Release status: Zendesk Bridge and external AI agents are in an early access program (EAP); they are available without charge during it, and packaging and pricing might change at general availability. ([A], [B])

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Zendesk admin** | Source-system admin (the customer's Zendesk administrator, who holds Admin Center access) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Business owner** | Business owner (RevOps manager, or the role's own leader) |
| **Security** | Security (CISO or security engineer) |
| **Partner integration engineer** | Integration engineer (partner role) |
| **Pilot user** | Pilot users (5 to 10 per role) |

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.

Pages used:

- [A] [Connecting external AI agents to Zendesk (EAP) (Zendesk help center)](https://support.zendesk.com/hc/en-us/articles/11400026079130-Connecting-external-AI-agents-to-Zendesk-EAP)
- [B] [Understanding Zendesk Bridge and allowing external AI agents to perform actions in Zendesk (EAP) (Zendesk help center)](https://support.zendesk.com/hc/en-us/articles/11398710406554)
- [C] [Editing and managing external AI agents (Zendesk help center)](https://support.zendesk.com/hc/en-us/articles/11400523951642)
- [D] [Add a connector that isn't in the directory (Claude docs)](https://claude.com/docs/connectors/custom/add-unlisted.md)
- [E] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [F] [Connector verification (Claude docs)](https://claude.com/docs/connectors/verification.md)
- [G] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)
- [H] [Connectors directory (Claude docs)](https://claude.com/docs/connectors/directory.md)

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role and the Claude group that gets the connector, and the matching Zendesk agent groups, if access is limited to groups (step 2).
- For each task: which Zendesk objects it reads (for example a customer's open tickets, users and organizations, help center articles) and which it writes, if any (ticket create or update, macros).
- For each tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)). Level 1 (Draft) keeps write tools **Blocked**; level 2 sets them to **Needs approval**.
- The data class of the tasks that use it ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)). Ticket text is customer content and can be untrusted input.
- Whose identity the connector acts under. For a pre-built provider each user authorizes the app for their own Zendesk account ([A]); the connection itself signs in with its own identity ([B]).
- The surfaces the role works in: claude.ai, the desktop app, mobile, or Claude Code ([E]).
- The Zendesk plan: it decides whether the connection can be created at all (Before you start).

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | Zendesk plan: all Suites (Team, Growth, Professional, Enterprise or Enterprise Plus), or Support (Team, Professional or Enterprise). | Zendesk admin | [A], [B] |
| 2 | The Zendesk admin can open Admin Center and has the right to create an external AI connection. **⚠ Unverified:** which admin role the pages require. | Zendesk admin | [A] |
| 3 | During the EAP there is one connection per built-in provider, and a pre-built provider connection holds up to 150 tools and AI agents. | Zendesk admin | [A] |
| 4 | On Team and Enterprise plans an Owner adds a custom connector for the organization; on Enterprise a member whose custom role includes managing the organization's libraries can add one too. | Claude org Owner | [D] |
| 5 | Destructive actions, bulk exports and third-party integrations are not supported during the EAP. | Business owner | [B] |

## Steps

1. Zendesk admin: create the connection. In Admin Center go to **AI** in the sidebar, then **External AI**, and click **Add connection**. ([A])
2. Zendesk admin: choose the type and who may use it. Under **Select connection type** choose **Use a pre-built provider**, then **Next**; on **Connection details** enter Provider (Claude, or Claude Code), Connection name and Description. Under **Select who should have access**, choose whether only admins or selected agent groups can use the connection. ([A])
3. Zendesk admin: grant only the tools the role needs. On **Tools and Zendesk AI agents**, click **Add tools**; you can select your own tools or accept the tools suggested by an AI-powered assistant. Agents have no access by default. Click **Next**, review and click **Save**. ([A], [B]) **⚠ Unverified:** the tool names and which are read or write; neither Zendesk page lists them. Read the list in the **Add tools** dialog and record it.
4. Zendesk admin: copy the connection details. Open the connection, click the **Setup** tab, and copy the MCP server URL under **Tools** (for example `https://example.zendesk.com/mcp`). ([A]) For Claude Code, the article's command carries "--client-id '<OAuth client ID from Setup>'". ([A])
5. Claude org Owner: add it for the organization. Go to **Organization settings > Connectors**, select **Add**, then **Custom**; enter a name and the MCP server URL from step 4, and choose the authentication settings. ([D]) **⚠ Unverified:** that the claude.ai custom-connector route works with this server, and which OAuth client option it needs; Zendesk's article does not describe a custom connector in Claude, and its Setup tab shows an OAuth client ID, which would point to **Use your own OAuth client** in Claude's dialog ([A], [D]). Test with one user before rolling out. Authentication settings cannot be changed after you add the connector. ([D])
6. Claude org Owner, with the Business owner: set the tools. Go to **Customize > Connectors**, select the connector, and under **Tool permissions** choose **Always allow**, **Needs approval** or **Blocked** for each group or single tool; the setting applies org-wide and users cannot override it. ([E]) You can also block individual tools you don't need by setting the tool's permission to **Blocked**. ([D]) On Enterprise, **Organization settings > Roles** > the role's **Connectors** tab sets each connector per role. ([G]) **⚠ Unverified:** whether a Team plan can show it to one Claude group; no page says so, so the Zendesk-side group limit in step 2 is the control.
7. Pilot user: connect. Go to **Customize > Connectors**, find the connector with the **Custom** label and click **Connect** to authenticate. Each user authorizes the app for their own Zendesk account. ([D], [A])
8. Pilot user: turn it on in the chat. Select **+** in the message box, select **Connectors**, and turn the connector on. ([D])
9. Partner integration engineer: write down the tool list and each tool's setting, with the date, for the record in Hand over. ([E])

## Check it worked

Run the tests in a pilot user's own Claude session, with the Partner integration engineer and the Zendesk admin watching.

**Read test.** Ask Claude to list the open tickets for one named test customer. Expected: the tickets appear, and the request makes no changes in Zendesk. ([A]) Then ask for a ticket in a group the user has no access to (the Zendesk admin names one). Expected: it does not appear, because a user who cannot perform an action in Zendesk cannot use an external AI agent to perform it, and the agent enforces the acting user's role and group access. ([B])

**Write test.** Ask Claude to add an internal note `connector write test` to a named test ticket. Expected, by the setting from step 6:

| Setting | Expected result |
|---|---|
| **Needs approval** | Claude asks first; select **Allow once** to continue or decline. ([E]) Zendesk also states the agent proposes a change and asks for human confirmation before making it. ([A]) Declining changes nothing. |
| **Blocked**, or the tool was never added in step 3 | The ticket is unchanged. **⚠ Unverified:** the exact message; record what you see. **⚠ Unverified:** whether the Zendesk tool set can add internal notes at all; the compendium has the same open item. |

Never answer **Always allow**. Afterwards the Zendesk admin checks the ticket and the transaction log, which records which agent acted and for whom. ([B]) A change that appears under a blocked or declined setting is a fail: go back to steps 3 and 6.

## Hand over

**Who: Partner integration engineer to the Zendesk admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- The Admin Center connection: name, provider, who has access, and the tools added (steps 2 and 3).
- The Claude-side setting for each tool and the level behind it (step 6), and the pilot group.
- The read and write test results, with the date and users.
- The unverified items still open, including the directory status.

Offboarding and revocation, both sides. Zendesk: in **Admin Center > AI > External AI**, select the connection, open the **Actions** menu in the upper right and choose **Deactivate** (takes effect immediately) or **Delete** (permanent and immediate). ([C]) Zendesk says you can update, restrict or disable an agent's access at any time, and users can see which agents have access to their data and revoke it. ([B]) **⚠ Unverified:** what happens to users' tokens when a connection is deactivated or deleted; [C] does not say. Claude: a user selects **Disconnect** on the connector page; an Owner uses **Organization settings > Connectors** to remove it for the organization. ([E], [D])

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| The **External AI** page or **Add connection** is missing | The Zendesk plan is not one the article lists for the EAP. Check the plan. | [A] |
| The second connection for Claude is refused | During the EAP there is one connection per built-in provider. Edit the existing one. | [A] |
| An action the user is not allowed in Zendesk is refused | The user's own Zendesk permissions apply, so the refusal is correct. | [B] |
| Claude cannot connect with the pasted URL | **⚠ Unverified:** the custom-connector route and its OAuth settings (step 5). Authentication settings cannot be edited; remove the connector and add it again. | [D] |
| A tool is missing or an action is not supported | The agent has no access by default and only the tools you added; destructive actions and bulk exports are not supported during the EAP. | [B] |
| The connection stops working after the EAP | Packaging and pricing might change at general availability. Re-check the plan and the price. | [A] |
| A change was proposed and applied without the user noticing | The tool was set to **Always allow**. Set it back to **Needs approval** or **Blocked** under **Tool permissions**. | [E] |

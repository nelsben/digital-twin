# Runbook: Connect HubSpot to a role's twin

## What this is

A role's twin reads CRM records in HubSpot, and may write notes or field updates, through Claude's HubSpot connector. HubSpot publishes the connector, and Claude's directory page for it carries the label "Anthropic verified" ([B]). This runbook takes the HubSpot admin, the Claude org Owner and our integration engineer from HubSpot-side approval to a tested read and a tested write setting. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states about this connector, see the [HubSpot row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems).

Release status: the listing says "Added November 2025" ([B]). Quote and quote-template create and update, HubSpot Work projects and HubSpot Work tables are labelled beta ([A]). **⚠ Unverified:** whether the connector as a whole is generally available; neither page says. Confirm with HubSpot.

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **HubSpot admin** | Source-system admin (HubSpot admin). A Super Admin approves the connector for other users; a Super Admin or a user with App Marketplace Access permissions can connect without approval (step 1). ([A]) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner |
| **Business owner** | Business owner (RevOps manager, or the role's own leader); decides which tasks write |
| **Security** | Security (CISO or security engineer) |
| **Partner integration engineer** | Integration engineer (partner role) |
| **Pilot user** | Pilot users (5 to 10 per role) |

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.

Pages used:

- [A] [Set up and use the HubSpot connector for Claude (HubSpot Knowledge Base)](https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude)
- [B] [HubSpot connector listing (Claude connectors directory)](https://claude.com/connectors/hubspot)
- [C] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [D] [Use connectors to extend Claude's capabilities (Claude help center)](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [E] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)
- [F] [Set up enterprise-managed authentication in Claude (HubSpot Knowledge Base)](https://knowledge.hubspot.com/integrations/set-up-enterprise-managed-authentication-in-claude)
- [G] [HubSpot connector for Claude: additional object access and admin controls (HubSpot changelog)](https://developers.hubspot.com/changelog/claude-connector-additional-objects-and-admin-controls)
- [H] [Connectors directory (Claude docs)](https://claude.com/docs/connectors/directory.md)

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role and the Claude group that gets the connector (the role's pilot users only).
- For each task the twin does: the HubSpot objects it reads (for example companies, contacts, deals, tickets, engagements) and the objects it writes, if any.
- For each tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)): level 1 (Draft) keeps write tools **Blocked**; level 2 sets them to **Needs approval**. Which tools count as write tools is not settled by the pages: see the rule in step 5.
- The data class of the tasks that use it ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)). CRM data is Confidential in that matrix.
- Whose identity the connector acts under. The default is each pilot user's own HubSpot account; see the [HubSpot row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems).
- The surfaces the role works in: claude.ai on the web, the desktop app, mobile, or Claude Code. This runbook covers the claude.ai surfaces: web, desktop and mobile ([A]). In Claude Code the connection comes from the role plugin's `.mcp.json`, not from these steps (see [page 18](../../docs/compendium/18-customer-success.md), where the `hubspot` entry points to `https://mcp.hubspot.com/anthropic`); [C] adds that connectors added in claude.ai are also available in Claude Code when the user signs in with their Claude account.
- The test record for the write test: one named test contact, so the note can be found and removed afterwards (see "Check it worked").
- Whether the customer's HubSpot account has Sensitive Data turned on. It decides whether the twin can use engagement data at all: with it on, Claude cannot access any engagement data ([A]); see the read test and the Sensitive Data row in "What can go wrong".

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | The customer has a paid Claude subscription tier the connector supports: Pro, Max, Team or Enterprise. The connector is available on the web, desktop and mobile versions of Claude. | Claude org Owner | [A] |
| 2 | HubSpot: any product and plan works ("All products and plans"), and each user needs an active HubSpot user account and an active Claude account. | HubSpot admin | [A] |
| 3 | On Team and Enterprise plans an Owner adds the connector for the organization, and members then connect with their own account. | Claude org Owner | [C] |
| 4 | A HubSpot Super Admin, or a user with App Marketplace Access permissions, is available. Everyone else needs a Super Admin to approve the connector first. | HubSpot admin | [A] |
| 5 | The pilot users are named, with their HubSpot user accounts. | Business owner | [A] |

## Steps

1. HubSpot admin: connect first, or approve. Super Admins and users with App Marketplace Access permissions can connect the connector without prior approval; for every other user a Super Admin must approve it first, and chooses which optional data permissions it may access. ([A])
2. HubSpot admin: set what the connector may reach and who may use it. In HubSpot, go to Settings icon > **Integrations** > **Connected Apps** > **Approved apps** tab, find the HubSpot Connector for Claude, click **Manage access**; the tabs include **Installed Permissions** and **Data permissions**. ([F]) HubSpot's changelog gives an older path, "Connected Apps > HubSpot connector for Claude > Give users access". ([G]) To add objects later a Super Admin must update the data permissions, and each user then reconnects. ([A]) **⚠ Unverified:** what each tab offers for restricting a pilot group; neither page lists it. Confirm on screen and record it.
3. Claude org Owner: add the connector for the organization. Go to **Organization settings > Connectors**, click **Browse connectors**, select **HubSpot**, click **Add to your team**. Adding it grants no access by itself: each person still authenticates individually. ([D]) The directory page names the same two places for an Owner. ([H])
4. Claude org Owner: limit it to the role's group. **⚠ Unverified:** whether a Team plan can show the connector to one Claude group; [D] describes no group or role scoping. On Enterprise, go to **Organization settings > Roles**, open the role, select the **Connectors** tab, and set the HubSpot dropdown to **Always allow**, **Needs approval**, **Blocked** or **Custom**. A new role defaults to **Needs approval** on every connector. ([E]) **Custom** sets each tool on the connector individually, instead of one setting for the whole connector. The org-wide **Tool permissions** setting in step 5 is a ceiling: a role's setting can narrow it and cannot widen it, and where the two disagree the stricter one applies. ([E]) Because the step 5 setting applies to every role that uses the connector, on a Team plan, which has no role setting, it must be the strictest any of those roles' tasks needs ([06-autonomy](../../docs/compendium/06-autonomy.md)); on Enterprise, set it to the loosest any role needs and narrow the other roles here. If Claude cannot limit the connector to the pilot group, the HubSpot-side restriction in step 2 is the only candidate control, and it is unconfirmed (its options are marked unverified there). If neither side can limit it, the connector is visible to the whole organization: record that with Security as a risk before the pilot starts. ([D])
5. Claude org Owner: set the tools for the role. Go to **Customize > Connectors**, select HubSpot, and under **Tool permissions** choose **Always allow**, **Needs approval** or **Blocked** for each category or tool. The setting applies org-wide and users cannot override it. ([D]) The directory listing names these tools: `get_crm_objects`, `query_crm_data`, `get_properties`, `get_user_details`, `get_organization_details`, `get_campaign_attribution_reports`, `get_content_analytics_report`, `get_marketing_email_analytics`, `get_aeo_metrics`, `get_conversation_channel_metadata`, `manage_crm_objects`, `manage_custom_properties`, `manage_custom_pipelines`, `manage_campaign_objects`, `manage_blog_post`, `manage_landing_page`, `manage_website_page`, `manage_marketing_email`, `manage_segment`, `manage_saved_reports`, `manage_aeo_prompts`, `manage_aeo_recommendations`, `manage_onboarding` and `import-claude-design-from-url`; the page says "Show all 36 tools" but lists 24. ([B]) **⚠ Unverified:** which of these are read and which write; the page does not label them. Read the grouping on the connector's own **Tool permissions** page and record it. Our recommendation, not the page's: until the screen's own grouping is recorded, treat every tool whose name does not start with `get_` or `query_` as a write tool. That covers all the `manage_*` tools, including the content ones (blog post, landing page, website page, marketing email, segment), and `import-claude-design-from-url`. ([B])
6. Claude org Owner, with the Business owner: apply the autonomy decision. HubSpot recommends always asking for approval before updates: its article names a **Write tools** setting in Claude's connector tool settings and says to set it to **Needs Approval**, because **Always allow** lets edits happen without confirmation. ([A]) **⚠ Unverified:** whether the screen groups tools as "Write tools"; if it does not, apply the `get_` and `query_` rule from step 5 tool by tool. For a level 1 role, set the write tools to **Blocked**; for level 2, **Needs approval**. ([06-autonomy](../../docs/compendium/06-autonomy.md)) Writes the connector supports: create and update on contacts, leads, companies, deals, tickets, custom objects and activable objects (no delete); calls, meetings, notes, tasks and emails can be read, created and updated; conversations are read-only. At most 10 records can be created or updated at a time. ([A])
7. Pilot user: connect. Go to **Customize > Connectors** and select **Connect** on HubSpot. ([C]) HubSpot's article words it as profile icon > **Settings** > **Connectors** > **Browse**, search for **HubSpot**, click **Connect**; select the HubSpot account, and on the page "Connecting HubSpot Connector for Claude to HubSpot" select the permissions and click **Connect app**. Use whichever path the screen shows. **⚠ Unverified:** which permissions that screen lists; [A] says to select them but names none. Copy the screen's list into the Hand over record. ([A])
8. Pilot user: turn it on in the chat. Select **+** in the message box, then **Connectors**, and turn the HubSpot toggle on. ([A], [C])
9. Partner integration engineer: open **Customize > Connectors**, select HubSpot, and write down each tool's **Tool permissions** setting, with the date, for the record in Hand over. ([D])

## Check it worked

Run both tests in a pilot user's own Claude session, with the Partner integration engineer watching and the HubSpot admin ready to look at HubSpot's Audit Log.

**Read test.** Ask Claude to list the open deals on one named test company. Expected: the deal records appear, taken from HubSpot. Then ask for a record the user cannot open in HubSpot itself (the HubSpot admin names one); expected: it does not appear. The connector runs under the user's own HubSpot permissions ([page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems)); if the user sees more than in HubSpot, stop and fix HubSpot first. If Sensitive Data is on, an engagement question should fail: with it on, Claude cannot access any engagement data. ([A])

**Write test.** Ask Claude to add a note reading `connector write test` to a named test contact. Expected, by the setting from step 5 or 6:

| Setting | Expected result |
|---|---|
| **Needs approval** | Claude asks before it uses the tool; choose **Allow once** to continue, or decline. ([C]) HubSpot's article has you type "Yes" to confirm or "No" to cancel. ([A]) Declining leaves no note on the contact. |
| **Blocked** | The note is not created. ([C]) **⚠ Unverified:** the exact message Claude shows for a blocked tool; record what you see. |

Never answer **Always allow** during this test. Afterwards the HubSpot admin checks the contact and the Audit Log: attribution is recorded there to both the user and the Claude connector, and Super Admins can see who connected or reconnected and all create and update actions. ([A]) Any note that appears under a blocked or declined setting is a fail: go back to step 5. Last, remove what the test created: the connector cannot delete ([A]), so remove the test note in HubSpot itself, and name the test contact in the Inputs record.

## Hand over

**Who: Partner integration engineer to the HubSpot admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- The HubSpot approval: who approved, the data permissions chosen (step 2), and the date.
- The Claude-side setting for each tool and the level behind it (steps 5 and 6), and the pilot group.
- The permissions the connect screen listed (step 7).
- The read and write test results, with the date and the two users.
- The unverified items still open.

Offboarding and revocation, both sides. Claude: the user clicks the profile icon > **Settings** > **Connectors**, selects **HubSpot**, and clicks **Disconnect** at the top right ([A]); an Owner removes the connector for the whole organization from **Organization settings > Connectors**. ([C]) HubSpot: **⚠ Unverified:** [A] describes no HubSpot-side disconnect; a Super Admin can update data permissions and review connection attempts in audit logs, and the **Manage access** screen in step 2 is the place to look for revoking a user. Confirm at setup.

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| A user sees a **Connect** prompt that fails, or no HubSpot connector | The user is not a Super Admin or an App Marketplace Access user, so a Super Admin must approve the connector first. On Team and Enterprise, the Owner must also add it. | [A], [C] |
| The twin cannot write, or cannot see engagements, after setup | The user connected before the permission existed. Disconnect and reauthenticate their HubSpot account. | [A] |
| Engagement data (calls, meetings, notes, emails) is missing for everyone | HubSpot's Sensitive Data setting is on; Claude cannot access any engagement data, and custom Sensitive Data properties are not accessible. | [A] |
| Writes happen with no prompt | A tool was set to **Always allow** (by the user or by a role). Set it back to **Needs approval** or **Blocked** at **Customize > Connectors**; the org-wide setting cannot be overridden by users. | [A], [D] |
| A bulk change stops partway | At most 10 records can be created or updated at a time. | [A] |
| The twin cannot reach a Partner Seat's client records | Reference the Partner Client Object (PCO) explicitly in the prompt. | [A] |
| After the HubSpot URL changes, the connector shows as Custom | A provider can move its endpoint; the old connection keeps working but shows under **Custom**. Remove it and add it again from the directory. | [H] |
| Which Claude group sees the connector on a Team plan | **⚠ Unverified:** no page says a Team plan can scope a connector to one group; rely on the HubSpot-side restriction until Anthropic confirms. | [D] |

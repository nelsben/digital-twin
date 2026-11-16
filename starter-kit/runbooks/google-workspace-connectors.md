# Runbook: Connect Google Drive, Gmail and Google Calendar to a role's twin

## What this is

A role's twin finds and reads files in Google Drive, searches email in Gmail and reads Google Calendar through three Claude connectors. Google builds and runs the Drive connector ([A]). This runbook takes the Google Workspace admin, the Claude org Owner and our integration engineer through admin approval, enablement and a tested read and a tested permission setting for each of the three. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states, see the [Drive, Gmail and Calendar rows on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems) and the [customer-success review on page 18](../../docs/compendium/18-customer-success.md).

Plainly: the Gmail and Google Calendar connectors cannot send mail or create events. Gmail: "Claude can't create, send, or modify emails" ([B]). Calendar: "Claude can't create, modify, or delete calendar events" and "can't send calendar invitations" ([C]). So a task that needs an email or a meeting ends in a draft in the conversation, or a proposed time, and the person sends or books it. The Drive connector can create new files ([A]).

Release status: none of the three pages labels its connector beta or generally available. **⚠ Unverified:** the release status of the three directory connectors; confirm in each connector's directory listing. Google's own Workspace MCP servers, a different route, are in the Google Workspace Developer Preview Program ([G]).

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Google Workspace admin** | Source-system admin (M365 or Google admin) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner. Gmail and Calendar need an Owner or Primary Owner. |
| **Business owner** | Business owner (RevOps manager, or the role's own leader) |
| **Security** | Security (CISO or security engineer) |
| **Partner integration engineer** | Integration engineer (partner role) |
| **Pilot user** | Pilot users (5 to 10 per role) |

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.

Pages used:

- [A] [Google Drive connector (Claude docs)](https://claude.com/docs/connectors/google/drive.md)
- [B] [Gmail connector (Claude docs)](https://claude.com/docs/connectors/google/gmail.md)
- [C] [Google Calendar connector (Claude docs)](https://claude.com/docs/connectors/google/calendar.md)
- [D] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [E] [Use connectors to extend Claude's capabilities (Claude help center)](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [F] [Control which apps access Google Workspace data (Google Workspace Admin Help; the address redirects to knowledge.workspace.google.com)](https://support.google.com/a/answer/7281227)
- [G] [Configure Google Workspace MCP servers (Google for Developers)](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [H] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role and the Claude group that gets each connector. Drive, Gmail and Calendar are separate decisions: a role may get one, two or all three.
- For each task: which Drive files it reads (and whether it creates any), which mail it searches, and which calendars it reads. Mail and calendar are read-only, so no task writes there.
- For each tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)). File creation in Drive is the only write: level 1 (Draft) keeps it **Blocked**; level 2 sets it to **Needs approval**.
- The data class of the tasks that use each connector ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)). Customer contracts are Confidential in that matrix.
- Whose identity the connectors act under: each pilot user's own Google account ([A], [B], [C]).
- The surfaces the role works in: claude.ai, the desktop app, mobile, or Claude Code ([D]).
- Whether the customer's Google Workspace restricts third-party apps (step 1).

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | Plans: Gmail and Calendar are available on Pro, Max, Ultra, Team and Enterprise plans. On Team and Enterprise an Owner or Primary Owner enables them first. | Claude org Owner | [B], [C] |
| 2 | Drive: on Team and Enterprise it does not appear in a member's connector list until an Owner adds it for the organization. | Claude org Owner | [A] |
| 3 | The Google Workspace admin holds the Service Settings administrator privilege, which the API controls page requires. | Google Workspace admin | [F] |
| 4 | Pilot users sign in with the Google account the data lives in. Gmail and Calendar reach only that account. | Business owner | [B], [C] |
| 5 | Decide which of the three connectors the role gets. Each is connected and tested on its own. | Business owner | [A], [B], [C] |

## Steps

1. Google Workspace admin: decide whether the apps are allowed. Open the Google Admin console, then **Menu** > **Security** > **Access and data control** > **API controls**. Under **Manage Google Services**, services are set to **Unrestricted** or **Restricted**; under **Manage App Access**, an app is set to **Trusted**, **Limited**, **Specific Google data** or **Blocked**. ([F]) **⚠ Unverified:** the app name the Claude connectors appear under and which services they need; connect one test user (step 4) and look in **Manage App Access**, then record the name.
2. Google Workspace admin: scope it to the pilot. A setting applies to the top-level organizational unit by default; to target specific units click **Select org units** then **Include organizations**. The page describes organizational units, not groups. ([F])
3. Claude org Owner: add each connector for the organization. Go to **Organization settings > Connectors**, click **Browse connectors**, select the connector, click **Add to your team**. Adding it grants no access by itself. ([E]) On Enterprise, **Organization settings > Roles** > the role's **Connectors** tab sets each connector to **Always allow**, **Needs approval**, **Blocked** or **Custom**; a new role defaults to **Needs approval**. ([H]) **⚠ Unverified:** whether a Team plan can show a connector to one Claude group; no page says so, so the Google-side scope in step 2 is the control.
4. Pilot user: connect each connector. Go to **Customize > Connectors**, find the connector, select **Connect**, sign in to Google and grant the requested permissions; the button then reads **Disconnect**. ([A], [B], [C]) The connector then shows under **Your connectors** with the status **Connected**. ([D])
5. Pilot user: turn each one on in the chat. Select **+** at the lower left of the message box, select **Connectors**, and turn on the connector. ([A], [B], [C])
6. Claude org Owner, with the Business owner: set the tools. Go to **Customize > Connectors**, select the connector and, under **Tool permissions**, choose **Always allow**, **Needs approval** or **Blocked** for each group of tools or single tool. The Owner's setting applies org-wide and users cannot override it. ([E]) **⚠ Unverified:** the tool names. The three Claude pages name no tools; read them on the connector's own **Tool permissions** page and record them.

### Google Drive

7. Read what Drive gives Claude: it searches Drive, lists recent files, checks a file's details and who it is shared with, and reads a file's content. It reads Google Docs, Sheets, Slides, PDF, Word, Excel and PowerPoint files, OpenDocument files, and PNG and JPEG images. ([A])
8. Know the limits. Content can be incomplete for a very large file; Claude cannot read comments or suggested edits. Files added from the picker are text copies, and Google caps exports of Docs, Sheets and Slides at about 10 MB. ([A])
9. Keep creation off or on ask-each-time. The connector can create new files, so set the tool that creates files to **Blocked** (level 1) or **Needs approval** (level 2) in step 6. ([A], [E]) **⚠ Unverified:** which tool that is; Google's preview server lists `create_file` and `copy_file` as its Drive write tools ([G]), but whether the directory connector uses those names is not confirmed.
10. Project files: Drive files can be added only to a private project, not a shared one. ([A])

### Gmail

11. The connector searches email and answers with citations; it is read-only. Claude cannot create, send or modify messages, and cannot see images embedded in email. ([B])
12. Whose permissions apply: your existing Gmail permissions, so Claude can search only the email the signed-in user can access. ([B])
13. Do not plan a send or draft tool on this connector. Google's own preview Gmail server has `create_draft` and no send tool ([G]), but that is a separate route and not this connector. Every email task ends in a draft the person sends ([page 18](../../docs/compendium/18-customer-success.md)). ([B])

### Google Calendar

14. The connector reads calendars to answer questions about meetings, attendees and availability; it is read-only. ([C])
15. Whose permissions apply: your existing calendar permissions, so Claude can search only the calendars the signed-in user can access. ([C])
16. Do not plan event creation on this connector. Google's preview Calendar server lists `create_event`, `update_event` and `delete_event`, but the scopes the page lists are `calendar.calendarlist.readonly`, `calendar.events.freebusy` and `calendar.events.readonly`. ([G]) **⚠ Unverified:** whether those write tools work with those scopes; this is the compendium's open item and is not the directory connector.

## Check it worked

Run the tests in a pilot user's own Claude session, with the Partner integration engineer watching.

**Read test, Drive.** Ask Claude to find a named test file in the user's Drive and summarize it. Expected: the file is found and summarised. Then ask for a file the user cannot open in Drive (the Google Workspace admin names one); expected: it does not appear. ([A])

**Read test, Gmail.** Ask for emails about a named test subject sent by a named test sender. Expected: an answer with citations that link to the messages. ([B])

**Read test, Calendar.** Ask "What meetings do I have tomorrow?" Expected: the user's own events, with links to them. ([C])

**Write test, Drive.** Ask Claude to create a file named `connector write test`. Expected, by the setting from step 6: **Needs approval** shows an approval prompt, with **Allow once** to continue; declining creates nothing. **Blocked**: nothing is created. ([D]) Check Drive afterwards. Never answer **Always allow**. **⚠ Unverified:** the message Claude shows for a blocked tool; record what you see.

**Write test, Gmail and Calendar.** Ask Claude to send a short email to the test user, then to book a meeting. Expected: it cannot; it offers a draft or a time in the conversation, and nothing is sent or booked. ([B], [C]) A mail or event that does appear is a fail: stop and investigate.

## Hand over

**Who: Partner integration engineer to the Google Workspace admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- The API controls decision: the app name found, its access level and the organizational units (steps 1 and 2).
- Which of the three connectors each role got, each tool's setting, and the autonomy level behind it (step 6).
- The read and write test results for each connector, with the date and users.
- The unverified items still open.

Offboarding, both sides. Claude: a user opens **Customize > Connectors**, selects the connector and clicks **Disconnect**, or uses the three-dot menu and **Remove**; an Owner removes a connector for the organization from **Organization settings > Connectors**. ([A], [D]) Google: **⚠ Unverified:** no page we read says how a user revokes Claude's access inside their Google account. The Google Workspace admin can set the app to **Blocked** under **Manage App Access**. ([F])

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| Gmail or Calendar does not appear in a member's connector list | An Owner or Primary Owner has not enabled it for the organization. | [B], [C] |
| Drive does not appear in a member's connector list | An Owner has not added it for the organization. | [A] |
| A user asks Claude to send mail or book a meeting and it cannot | By design: both connectors are read-only. The twin ends in a draft or a proposed time. | [B], [C] |
| Claude shows **Reconnect**, or a reconnection error keeps returning | Claude lost access to the Google account. Select **Reconnect**; if it persists, **Disconnect**, then **Connect**, and sign in again. | [A] |
| A large file's answer is incomplete, or a file over 10 MB gives only its name | Very large files can arrive incomplete, and exports over about 10 MB give details but no content. | [A] |
| Email images or document comments are missing from answers | Claude cannot see embedded email images, nor a file's comments or suggested edits. | [A], [B] |
| The Google Workspace admin set the app to **Blocked** or **Restricted** | Users cannot connect or the connector loses access; set the app to **Trusted** or **Specific Google data** for the pilot units. | [F] |
| Someone expects the Google preview server's write tools | Those are a different route, in developer preview, and the directory connectors do not promise them. | [G] |

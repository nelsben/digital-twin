# Runbook: Connect Google Drive, Gmail and Google Calendar to a role's twin

## What this is

A role's twin finds and reads files in Google Drive, searches email in Gmail and reads Google Calendar through three Claude connectors. Google builds and runs the Drive connector ([A]), and the directory listings name Google as the maker of all three ("Made by Google", [I], [J], [K]). This runbook takes the Google Workspace admin, the Claude org Owner and our integration engineer through admin approval, enablement and a tested read and a tested permission setting for each of the three. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states, see the [Drive, Gmail and Calendar rows on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems) and the [customer-success review on page 18](../../docs/compendium/18-customer-success.md).

Plainly: the Gmail and Google Calendar connectors cannot send mail or create events. Gmail: "Claude can't create, send, or modify emails" ([B]). Calendar: "Claude can't create, modify, or delete calendar events" and "can't send calendar invitations" ([C]). So a task that needs an email or a meeting ends in a draft in the conversation, or a proposed time, and the person sends or books it. The Drive connector can create new files ([A]). **⚠ Conflict:** the directory listings disagree with [B] and [C]. The Gmail listing's tagline is "Draft replies, summarize threads, & search your inbox" and its tools include `send_message`, `reply`, `forward` and `create_draft` ([J]); the Calendar listing says Claude can "create and update events, respond to invitations" and lists `create_event`, `update_event`, `delete_event` and `respond_to_event` ([K]). Until the write test below settles it for the customer, treat those as write tools and set them to **Blocked** or **Needs approval** in step 6.

Release status: none of the three pages labels its connector beta or generally available. **⚠ Unverified:** the release status of the three directory connectors; each listing shows "Anthropic verified" and "Added March 2026" but no beta or GA label ([I], [J], [K]). Setting up Google's own Workspace MCP servers as a custom connector is a different route, in the Google Workspace Developer Preview Program ([G]); but the listings' connector URLs are the addresses [G] gives for those servers, for example `https://gmailmcp.googleapis.com/mcp/v1` ([G], [J]).

Roles use the names in [03-stakeholders](../../docs/playbook/03-stakeholders.md):

| Name used here | Role in 03-stakeholders |
|---|---|
| **Google Workspace admin** | Source-system admin (M365 or Google admin) |
| **Claude org Owner** | Technical owner (Director of IT), or the Backup Owner. Gmail and Calendar need an Owner or Primary Owner to enable them. ([B], [C]) |
| **Business owner** | Business owner (RevOps manager, or the role's own leader) |
| **Security** | Security (CISO or security engineer) |
| **Partner integration engineer** | Integration engineer (partner role) |
| **Pilot user** | Pilot users (5 to 10 per role) |

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used:

- [A] [Google Drive connector (Claude docs)](https://claude.com/docs/connectors/google/drive.md)
- [B] [Gmail connector (Claude docs)](https://claude.com/docs/connectors/google/gmail.md)
- [C] [Google Calendar connector (Claude docs)](https://claude.com/docs/connectors/google/calendar.md)
- [D] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [E] [Use connectors to extend Claude's capabilities (Claude help center)](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [F] [Control which apps access Google Workspace data (Google Workspace Admin Help; the address redirects to knowledge.workspace.google.com)](https://support.google.com/a/answer/7281227)
- [G] [Configure Google Workspace MCP servers (Google for Developers)](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [H] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)
- [I] [Google Drive listing (Claude connectors directory)](https://claude.com/connectors/google-drive)
- [J] [Gmail listing (Claude connectors directory)](https://claude.com/connectors/gmail)
- [K] [Google Calendar listing (Claude connectors directory)](https://claude.com/connectors/google-calendar)
- [L] [Manage links between your Google Account & apps from other developers (Google Account Help)](https://support.google.com/accounts/answer/13533235)

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role and the Claude group that gets each connector. Drive, Gmail and Calendar are separate decisions: a role may get one, two or all three.
- For each task: which Drive files it reads (and whether it creates any), which mail it searches, and which calendars it reads. [B] and [C] say mail and calendar are read-only, so no task writes there; the listings disagree (the ⚠ Conflict under What this is). ([B], [C], [J], [K])
- For each tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)). File creation is the only Drive write [A] names, but the Drive listing also names `share_file`, `trash_file` and `update_file` ([I]), and the Gmail and Calendar listings name send and event tools ([J], [K]): level 1 (Draft) keeps every write tool **Blocked**; level 2 sets it to **Needs approval**.
- The data class of the tasks that use each connector ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)). Customer contracts are Confidential in that matrix.
- Whose identity the connectors act under: each pilot user's own Google account ([A], [B], [C]).
- The surfaces the role works in: claude.ai, the desktop app, mobile, or Claude Code ([D]). This runbook covers the claude.ai surfaces. In Claude Code the connection comes from the role plugin's `.mcp.json`, not from these steps: for Gmail and Calendar the `customer-support` plugin's entries have an empty URL, so the user connects Claude's own connectors, and it ships no Drive ([page 18](../../docs/compendium/18-customer-success.md)). [D] adds that connectors added in claude.ai are also available in Claude Code when the user signs in with their Claude account.
- Whether the customer's Google Workspace restricts third-party apps (step 1).
- The test record for the Drive write test: the file name `connector write test` and the folder it lands in, so it can be found and trashed afterwards.
- Where the files live. **⚠ Unverified:** whether the Drive connector reaches shared drives; the [Drive row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems) marks shared-drive support unconfirmed, and [A], [G] and the Drive listing [I] do not mention shared drives. Test one shared-drive file at setup before promising it.

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | Plans: Gmail and Calendar are available on Pro, Max, Ultra, Team and Enterprise plans. On Team and Enterprise an Owner or Primary Owner enables them first. | Claude org Owner | [B], [C] |
| 2 | Drive: on Team and Enterprise it does not appear in a member's connector list until an Owner adds it for the organization. **⚠ Unverified:** which Claude plans include Drive; [A] and the page 11 row state none. | Claude org Owner | [A] |
| 3 | The Google Workspace admin holds the Service Settings administrator privilege, which the API controls page requires. | Google Workspace admin | [F] |
| 4 | Pilot users sign in with the Google account the data lives in. Gmail and Calendar reach only that account. | Business owner | [B], [C] |
| 5 | Decide which of the three connectors the role gets. Each is connected and tested on its own. | Business owner | [A], [B], [C] |

## Steps

1. Google Workspace admin: decide whether the apps are allowed. Do steps 3 and 4 for one test user first, then return here: once a user has connected, the app appears under **Accessed apps** in **Manage App Access**, and details typically appear 24–48 hours after authorization; an app whose name or client ID you already know can be set up in advance with **Configure new app**. Open the Google Admin console, then **Menu** > **Security** > **Access and data control** > **API controls**. Under **Manage Google Services**, services are set to **Unrestricted** or **Restricted**; under **Manage App Access**, an app is set to **Trusted**, **Limited**, **Specific Google data** or **Blocked**. **Trusted** gives an app all Google Workspace services, including restricted ones; **Limited** only unrestricted ones; **Specific Google data** only the scopes you specify (include the Google Sign-in scopes); **Blocked** none. The page recommends no setting for third-party apps, so the Google Workspace admin and Security choose, and the choice and the reason go in the Hand over record. ([F]) **⚠ Unverified:** the app name the Claude connectors appear under and which services they need; look in **Manage App Access** after the test user connects, then record the name. The listings say Google makes the connectors ([I], [J], [K]) and [F] says "By default, most Google-owned apps are Trusted", but no page says whether these connectors count as Google-owned apps there.
2. Google Workspace admin: scope it to the pilot. A setting applies to the top-level organizational unit by default; to target specific units click **Select org units** then **Include organizations**. The page describes organizational units, not groups, so for this to reach only the pilot the pilot users must sit in their own organizational unit; moving them there is a Google Workspace admin task to agree first. If neither side can scope it, the connector is visible to the whole organization: record that with Security as a risk before the pilot starts. ([F])
3. Claude org Owner: add each connector for the organization. Go to **Organization settings > Connectors**, click **Browse connectors**, select the connector, click **Add to your team**. Adding it grants no access by itself. ([E]) On Enterprise, **Organization settings > Roles** > the role's **Connectors** tab sets each connector to **Always allow**, **Needs approval**, **Blocked** or **Custom**; a new role defaults to **Needs approval**. ([H]) **Custom** sets each tool on the connector individually, instead of one setting for the whole connector. The org-wide **Tool permissions** setting in step 6 is a ceiling: a role's setting can narrow it and cannot widen it, and where the two disagree the stricter one applies. ([H]) Because the step 6 setting applies to every role that uses the connector, on a Team plan, which has no role setting, it must be the strictest any of those roles' tasks needs ([06-autonomy](../../docs/compendium/06-autonomy.md)); on Enterprise, set it to the loosest any role needs and narrow the other roles here; grants add up across roles, so a member who holds two roles gets the more permissive one ([H]). **⚠ Unverified:** whether a Team plan can show a connector to one Claude group; no page says so, so the Google-side scope in step 2 is the only candidate control, and it works only if the pilot users have their own organizational unit.
4. Pilot user: connect each connector. Go to **Customize > Connectors**, find the connector, select **Connect**, sign in to Google and grant the requested permissions; the button then reads **Disconnect**. ([A], [B], [C]) The connector then shows under **Your connectors** with the status **Connected**. **⚠ Unverified:** which Google permissions each consent screen lists; [A], [B] and [C] say only "grant the requested permissions". Copy each screen's list into the Hand over record. ([D])
5. Pilot user: turn each one on in the chat. Select **+** at the lower left of the message box, select **Connectors**, and turn on the connector. ([A], [B], [C])
6. Claude org Owner, with the Business owner: set the tools. Go to **Customize > Connectors**, select the connector and, under **Tool permissions**, choose **Always allow**, **Needs approval** or **Blocked** for each group of tools or single tool. The Owner's setting applies org-wide and users cannot override it. ([E]) The three Claude pages name no tools; the directory listings do ([I], [J], [K]), and steps 9, 13 and 16 name the write tools. Check them against the connector's own **Tool permissions** page, which groups tools by type, and record them. ([E], [I], [J], [K])

### Google Drive

7. Read what Drive gives Claude: it searches Drive, lists recent files, checks a file's details and who it is shared with, and reads a file's content. It reads Google Docs, Sheets, Slides, PDF, Word, Excel and PowerPoint files, OpenDocument files, and PNG and JPEG images. ([A])
8. Know the limits. Content can be incomplete for a very large file; Claude cannot read comments or suggested edits. Files added from the picker are text copies, and Google caps exports of Docs, Sheets and Slides at about 10 MB. ([A])
9. Keep creation off or on ask-each-time. The connector can create new files ([A]), and the Drive listing names `copy_file`, `create_file`, `share_file`, `trash_file` and `update_file` beside its read tools ([I]); set each of those to **Blocked** (level 1) or **Needs approval** (level 2) in step 6. ([A], [E], [I]) **⚠ Unverified:** what `share_file`, `trash_file` and `update_file` do; the listing names them without describing them, and [A] describes only creating files.
10. Project files: Drive files can be added only to a private project, not a shared one. ([A])

### Gmail

11. The connector searches email and answers with citations; it is read-only. Claude cannot create, send or modify messages, and cannot see images embedded in email. ([B]) The listing disagrees on writing: see the ⚠ Conflict under What this is ([J]).
12. Whose permissions apply: your existing Gmail permissions, so Claude can search only the email the signed-in user can access. ([B])
13. Do not plan a send or draft tool on this connector. Google's own preview Gmail server lists `create_draft` and no send tool ([G]); the Gmail listing, at the same connector URL, names `send_message`, `reply`, `forward` and `create_draft` ([J]), against [B]. Every email task ends in a draft the person sends ([page 18](../../docs/compendium/18-customer-success.md)). ([B])

### Google Calendar

14. The connector reads calendars to answer questions about meetings, attendees and availability; it is read-only. ([C]) The listing disagrees: see the ⚠ Conflict under What this is ([K]).
15. Whose permissions apply: your existing calendar permissions, so Claude can search only the calendars the signed-in user can access. ([C])
16. Do not plan event creation on this connector. Google's preview Calendar server lists `create_event`, `update_event` and `delete_event`, but the scopes the page lists are `calendar.calendarlist.readonly`, `calendar.events.freebusy` and `calendar.events.readonly`. ([G]) The Calendar listing names the same nine tools at the same connector URL ([K]). **⚠ Unverified:** whether those write tools work with those scopes; this is the compendium's open item, and the write test below checks it on the directory connector.

## Check it worked

Run the tests in a pilot user's own Claude session, with the Partner integration engineer watching.

**Read test, Drive.** Ask Claude to find a named test file in the user's Drive and summarize it. Expected: the file is found and summarised. Then ask for a file the user cannot open in Drive (the Google Workspace admin names one); expected: it does not appear. ([A])

**Read test, Gmail.** Ask for emails about a named test subject sent by a named test sender. Expected: an answer with citations that link to the messages. ([B])

**Read test, Calendar.** Ask "What meetings do I have tomorrow?" Expected: the user's own events, with links to them. ([C])

**Write test, Drive.** Ask Claude to create a file named `connector write test`. Expected, by the setting from step 6: **Needs approval** shows an approval prompt, with **Allow once** to continue; declining creates nothing. **Blocked**: nothing is created. ([D]) Check Drive afterwards. Never answer **Always allow**. **⚠ Unverified:** the message Claude shows for a blocked tool; record what you see. Afterwards trash the test file in Drive and name it in the Inputs record.

**Write test, Gmail and Calendar.** Ask Claude to send a short email to the test user, then to book a meeting. Expected, per [B] and [C]: it cannot; it offers a draft or a time in the conversation, and nothing is sent or booked. ([B], [C]) A mail or event that does appear is a fail: stop and investigate. Because the listings name send and event tools ([J], [K]), run this only after step 6 has set those tools to **Blocked** or **Needs approval**, decline any prompt, and record which tools the **Tool permissions** page shows.

## Hand over

**Who: Partner integration engineer to the Google Workspace admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- The API controls decision: the app name found, its access level and the organizational units (steps 1 and 2).
- Which of the three connectors each role got, each tool's setting, and the autonomy level behind it (step 6).
- The permissions each consent screen listed (step 4).
- The read and write test results for each connector, with the date and users.
- The unverified items still open.

Offboarding, both sides. Claude: a user opens **Customize > Connectors**, selects the connector and clicks **Disconnect**, or uses the three-dot menu and **Remove**; an Owner removes a connector for the organization from **Organization settings > Connectors**. ([A], [D]) Google: a user opens their Google Account's linked apps page, selects **Access to your Google Account**, selects the app, **See details**, then **Remove access** ([L]). **⚠ Unverified:** whether the Google-made connectors are listed there; [L] covers apps from other developers. The Google Workspace admin can set the app to **Blocked** under **Manage App Access**. ([F])

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| Gmail or Calendar does not appear in a member's connector list | An Owner or Primary Owner has not enabled it for the organization. | [B], [C] |
| Drive does not appear in a member's connector list | An Owner has not added it for the organization. | [A] |
| A user asks Claude to send mail or book a meeting and it cannot | By design per [B] and [C]: both connectors are read-only, and the twin ends in a draft or a proposed time. If the listings' send or event tools ([J], [K]) are there and **Blocked** in step 6, that is the setting working. | [B], [C], [J], [K] |
| Claude shows **Reconnect**, or a reconnection error keeps returning | Claude lost access to the Google account. Select **Reconnect**; if it persists, **Disconnect**, then **Connect**, and sign in again. | [A] |
| A large file's answer is incomplete, or a file over 10 MB gives only its name | Very large files can arrive incomplete, and exports over about 10 MB give details but no content. | [A] |
| Email images or document comments are missing from answers | Claude cannot see embedded email images, nor a file's comments or suggested edits. | [A], [B] |
| The Google Workspace admin set the app to **Blocked**, or a service it uses to **Restricted** | **Blocked**: the app can't access any Google service. **Restricted**: apps not trusted stop working and their tokens are revoked. Set the app to **Trusted** or **Specific Google data** for the pilot units. | [F] |
| Someone expects the write tools the Google preview server or a listing names | The preview server is a different setup route, in developer preview ([G]); the listings name write tools at the same connector URLs ([I], [J], [K]), but [B] and [C] say Gmail and Calendar are read-only. Plan on what the **Tool permissions** page shows and the write test proves. | [G], [I], [J], [K] |

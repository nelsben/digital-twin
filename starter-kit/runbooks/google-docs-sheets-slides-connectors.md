# Runbook: Connect the Google Docs, Google Sheets and Google Slides connectors to a role's twin

## What this is

A role's twin that edits a document, a sheet or a deck does it through three Claude connectors that are separate from Google Drive: "These are separate connectors from Google Drive. Google Drive still handles searching, uploading, and sharing files." ([A]) Claude edits the open file live in a pane beside the chat, creates new Docs, Sheets and Slides files, and in Docs reads and works with comments and suggestions ([A]). This runbook takes the Google Workspace admin, the Claude org Owner and our integration engineer through enablement, one test user's connection and a tested permission setting for each of the three. It reuses the [Google Workspace runbook](google-workspace-connectors.md) for the Workspace admin's app-access decision, the role steps and the Drive write test, and does not copy them. It is generic: replace every `<placeholder>` with the customer's value. For what the compendium already states, see the [Drive / Sheets row on page 11](../../docs/compendium/11-connectors.md#what-exists-for-our-systems) and the [customer-success review on page 18](../../docs/compendium/18-customer-success.md).

Not this product: "Claude for Google Workspace" is a sidebar installed from the Google Workspace Marketplace, in beta, and the help center says it is "different from the Google Workspace connectors in Claude" ([E]). It has its own install and admin steps and is not covered here.

What the pages do not give us: no page we downloaded lists the tools of the Docs, Sheets or Slides connectors, their plans, or who builds them (each is marked below). **(Our recommendation):** a task that changes a document, a sheet or a deck starts with every write tool **Blocked**, or at **Needs approval** when the plan's level allows it ([06-autonomy](../../docs/compendium/06-autonomy.md)), and the write test in "Check it worked" is run in the customer's org before any task depends on a write tool. Roles use the names in the [Google Workspace runbook's table](google-workspace-connectors.md#what-this-is) ([03-stakeholders](../../docs/playbook/03-stakeholders.md)).

## Read this first

How sources are marked: each numbered step and each product sentence ends with the page it came from, in brackets. **⚠ Unverified:** (the compendium's marker) means the pages we read did not confirm it; confirm each such item at setup, then replace the mark with the page you checked. Where two pages disagree we write **⚠ Conflict:**, name both and take the safer reading; none of these pages disagree on the three connectors. Menu paths and setting names are copied from the pages, so a screen that reads differently means the product has changed: trust the screen and note the difference.

Checked 2026-11-16 by the author against the pages listed. Every claim was checked again on 2026-11-16 by a second reader; the results are in the [verification log](verification-log.md).

Pages used (each downloaded on 2026-11-16):

- [A] [Use Google Workspace connectors (Claude help center)](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors)
- [B] [Use connectors to extend Claude's capabilities (Claude help center)](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [C] [Get started with connectors (Claude docs)](https://claude.com/docs/connectors/getting-started.md)
- [D] [Configure the Google Workspace MCP servers (Google for Developers)](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [E] [Use Claude in Google Docs, Sheets, and Slides (Claude help center)](https://support.claude.com/en/articles/16951679-use-claude-in-google-docs-sheets-and-slides)
- [F] [Claude docs index (llms.txt)](https://claude.com/docs/llms.txt)
- [G] [Claude connectors directory](https://claude.com/connectors)
- [H] [Set up role-based permissions on Enterprise plans (Claude help center)](https://support.claude.com/en/articles/13930458-set-up-role-based-permissions-on-enterprise-plans)

Pages that do not exist, so no listing or docs page can be cited: `claude.com/connectors/google-docs`, `/google-sheets` and `/google-slides` (and the shorter `docs`, `sheets`, `slides` forms) and `claude.com/docs/connectors/google/docs.md`, `sheets.md`, `slides.md` all returned 404. The docs index lists Google pages for Drive, Gmail and Google Calendar only ([F]), and the directory index we downloaded names Google Drive and Google Calendar but no Docs, Sheets or Slides entry ([G]).

## Inputs you need

These are decisions the engagement has already made. The steps consume them; do not make them during setup. They live in the customer's folder under `engagements/`.

- The role, and which of the three connectors it gets. Docs, Sheets and Slides are separate decisions: a role may get one, two or all three. ([A])
- For each task: which files it changes or creates, and whether it changes one the person owns or a shared one. Claude "can only open and change files your Google account has access to". ([A])
- For each write tool, its permission (**Always allow**, **Needs approval** or **Blocked**) and the autonomy level behind it ([06-autonomy](../../docs/compendium/06-autonomy.md)): level 1 (Draft) keeps every write tool **Blocked**; level 2 sets it to **Needs approval**. ([B])
- The data class of the files ([10-sensitive-data](../../docs/compendium/10-sensitive-data.md#decision-matrix-by-data-class-our-recommendation-built-from-the-sources-above)).
- The surface the role works in. Live editing "works on Claude on the web in Chrome, and on Claude Desktop when the built-in browser is turned on"; otherwise the file opens through "Open in Google". ([A])
- Whose identity the connectors act under: each pilot user's own Google account. ([A])
- The test user and, for each connector, one test file: `connector test doc`, `connector test sheet` and `connector test deck`, with the folder each lives in, so each can be found and deleted afterwards.
- The Google Workspace admin's answer to step 1 of the [Google Workspace runbook](google-workspace-connectors.md#steps).

## Before you start

| # | Check | Who | Source |
|---|---|---|---|
| 1 | The Claude Owner is ready to add the connectors: on Team and Enterprise "an Owner or Primary Owner must enable these connectors at the organization level before individual users can authenticate". | Claude org Owner | [A] |
| 2 | The app-access decision is made. Live editing "uses the same Claude for Google Drive app. Admins approve it once, and no separate approval is needed for each file type." | Google Workspace admin | [A] |
| 3 | The test user can open the three test files in Google, signed in to only the one Google account. | Business owner | [A] |
| 4 | Decide whether any task needs the Drive connector too (searching, sharing, moving files). That is the [Google Workspace runbook](google-workspace-connectors.md), not this one. | Business owner | [A] |

## Steps

1. Google Workspace admin: decide whether the Claude app is allowed. Follow steps 1 and 2 of the [Google Workspace runbook](google-workspace-connectors.md#steps); the app is the same one, so there is no second approval for Docs, Sheets and Slides. ([A]) **⚠ Unverified:** the scopes Claude's connectors ask for. Google lists scopes for its own preview servers, including read-only and edit scopes for documents, spreadsheets and presentations ([D]), but no page lists Claude's. Copy each consent screen's list into the Hand over record.
2. Claude org Owner: add each connector for the organization. Go to **Organization settings > Connectors**, click **Browse connectors**, select the connector, click **Add to your team**; adding it gives nobody access, and each person still authenticates. ([B]) **⚠ Unverified:** whether Docs, Sheets and Slides appear as three entries there, since the directory index we downloaded shows none ([G]).
3. Claude org Owner, Enterprise only: set each role's connector access as step 3 of the [Google Workspace runbook](google-workspace-connectors.md#steps) says (the role's **Connectors** tab; the org-wide **Tool permissions** are a ceiling the role can only narrow). ([B], [H])
4. Pilot user: connect and turn on. Click the plus sign in the chat, hover over "Connectors" and toggle them on; "If the connector isn't turned on when you ask Claude to edit a Google file, Claude prompts you to connect it, then continues with your request." ([A]) The connector then shows under **Your connectors** with the status **Connected**. ([C])
5. Pilot user: open a file in the pane. Paste a Google link into the chat, or ask for a new file by naming Google ("make a Google Slides deck from these notes"); "Asking for a generic "doc" or "deck" without naming Google creates a local file instead." The pane needs its own Google sign-in, with the same account you connected to Claude. ([A])
6. Claude org Owner, with the Business owner: set the tools. Go to **Customize > Connectors**, select the connector and, under **Tool permissions**, choose **Always allow**, **Needs approval** or **Blocked** for each category or single tool; the setting applies org-wide and users cannot override it. ([B]) **⚠ Unverified:** whether each of the three connectors has its own **Tool permissions** page, and what its tools are called; no Claude page names them. Record what the page shows.

### Google Docs

7. Who builds it and which plans. **⚠ Unverified:** who builds and runs the Google Docs connector, and which Claude plans have it. [A] says "Google Workspace connectors (Gmail, Google Calendar, and Google Drive) are available for all users on Claude and Claude Desktop", naming three and not Docs. Google runs a Docs MCP server in developer preview at `https://docsmcp.googleapis.com/mcp/v1` ([D]), but no page says Claude's connector is that server. Record the plan the customer's org has.
8. Who adds it and who connects. Owner adds it for the organization (step 2) and each member signs in with their own Google account ([A]); the pane's Google account must match, or "Claude tells you and offers to switch". ([A])
9. Read what Docs gives Claude: it opens the file in the pane and "Read and work with comments and suggestions in Google Docs"; "Claude can see comments and suggestions in Google Docs, but it can't see images." ([A]) Google's preview server lists `read_doc` ([D]).
10. Know what writes. Live edits to the open file, and creating new Docs files ([A]); "You and Claude can work in the same file at the same time. Claude re-reads the current content before each change, but in a busy file, check the result." ([A]) Google's preview server lists `update_doc` ([D]). **⚠ Unverified:** the write tools' names on Claude's connector, and whether editing in the pane asks for approval. Set each write tool to **Blocked** (level 1) or **Needs approval** (level 2) in step 6.

### Google Sheets

11. Who builds it and which plans. **⚠ Unverified:** who builds and runs the Google Sheets connector, and its plans, for the reasons in step 7. Google's Sheets MCP server is at `https://sheetsmcp.googleapis.com/mcp/v1` in developer preview ([D]).
12. Who adds it and who connects: as step 8. ([A])
13. Read what Sheets gives Claude. Claude opens the sheet in the pane ([A]); Google's preview server lists `get_spreadsheet` and `get_values` ([D]). **⚠ Unverified:** Claude's read tool names.
14. Know what writes. Live edits to the open sheet and creating new Sheets files ([A]). Google's preview server lists `update_spreadsheet`, `update_values`, `update_formulas` and `insert_dimension` ([D]). **⚠ Unverified:** the write tools' names on Claude's connector. Set each write tool, however named, to **Blocked** (level 1) or **Needs approval** (level 2) in step 6.

### Google Slides

15. Who builds it and which plans. **⚠ Unverified:** who builds and runs the Google Slides connector, and its plans, for the reasons in step 7. Google's Slides MCP server is at `https://slidesmcp.googleapis.com/mcp/v1` in developer preview ([D]).
16. Who adds it and who connects: as step 8. ([A])
17. Read what Slides gives Claude. Claude opens the deck in the pane ([A]); Google's preview server lists `read_presentation` ([D]). **⚠ Unverified:** Claude's read tool name.
18. Know what writes, and the limits. Live edits to the open deck and creating new Slides files ([A]); Google's preview server lists `update_presentation` ([D]). "Claude can't add charts to Google Slides, and Slides edits may not appear live in the pane." ([A]) **⚠ Unverified:** the write tool's name on Claude's connector. Set it to **Blocked** (level 1) or **Needs approval** (level 2) in step 6.

## Check it worked

Run the tests in one test user's own Claude session, with the Partner integration engineer watching, on the test file for that connector. The Drive write test and its record are in the [Google Workspace runbook](google-workspace-connectors.md#check-it-worked); this adds the three.

**Read test, Google Docs.** Ask Claude to open `connector test doc` and summarise it. Expected: the file opens in the pane and the summary matches it. Then ask for a doc the user cannot open in Google; expected: Claude cannot open it. ([A])

**Read test, Google Sheets.** Ask Claude what a named formula in `connector test sheet` calculates. Expected: the sheet opens in the pane and the answer matches. ([A])

**Read test, Google Slides.** Ask Claude to list the slide titles in `connector test deck`. Expected: the deck opens in the pane and the titles match. ([A])

**Write test, each connector.** Run this only after step 6 has set the write tools to **Blocked** or **Needs approval**. Ask Claude to add the line `write test` to the test doc, to put `write test` in cell A1 of the test sheet, and to add a slide titled `write test` to the test deck. Expected, by the setting from step 6: **Needs approval** shows an approval prompt, with **Allow once** to continue; decline it, and the file is unchanged. **Blocked**: the file is unchanged. ([C]) Never answer **Always allow**. The only fail is a changed file without an approval prompt, or a change that a **Blocked** tool allowed: stop and investigate. **⚠ Unverified:** the message Claude shows for a blocked tool, and whether a **Blocked** tool also stops edits in the pane; record what you see. Record which tools each **Tool permissions** page shows. ([B]) Afterwards delete the test files and name them in the Inputs record.

## Hand over

**Who: Partner integration engineer to the Google Workspace admin, the Claude org Owner and the Business owner.** Record the following in the customer's folder under `engagements/` (for example, as `engagements/sample-team-cs/` does for the fictional worked example), never in the compendium:

- The app-access decision and the permissions each consent screen listed (steps 1 and 4).
- Which of the three connectors each role got, each tool's name and setting, and the autonomy level behind it (step 6).
- The plan the org has and whether the three connectors appear as three entries (steps 2 and 7).
- The read and write test results for each connector, with the date and the test user.
- Whether any write tool is used at **Needs approval**, who decided and when.
- The unverified items still open.

Offboarding: a user opens **Customize > Connectors**, selects the connector and clicks **Disconnect**, or uses the three-dot menu and **Remove**; an Owner removes a connector for the organization from **Organization settings > Connectors**. ([C]) Owners can also disable the Google Workspace connectors there. ([A])

## What can go wrong

| Symptom | Cause and fix | Source |
|---|---|---|
| A member cannot find the connector, or Claude cannot open a file | An Owner has not added the connector, or the user's Google account has no access: Claude "can only open and change files your Google account has access to". | [A], [B] |
| "Access blocked: your institution's admin needs to review Claude for Google Drive" | The Google Workspace admin has not allowed the Claude app. Follow step 1; the fix the page gives is **Manage third-party app access**, **Add app**, search "Claude", set it **Trusted**, wait about 15 minutes. | [A] |
| The pane does not open, or shows a Google sign-in | Live editing works on Claude on the web in Chrome, and on Claude Desktop with the built-in browser on; elsewhere use "Open in Google". The pane needs a Google session with the account connected to Claude. | [A] |
| Claude makes a local file, not a Google file | The request did not name Google. Ask for a Google doc, sheet or deck, or paste a link. | [A] |
| A person edits the file while Claude does | Allowed: "Claude re-reads the current content before each change, but in a busy file, check the result." Keep write tasks on files one person owns. | [A] |
| Someone expects Slides charts, or edits to show live in Slides | "Claude can't add charts to Google Slides, and Slides edits may not appear live in the pane." | [A] |
| Someone expects the Marketplace sidebar's rules, or the tool names Google's preview server lists | The sidebar is a different product with its own install, in beta ([E]); the preview server is a different route, in developer preview ([D]). Neither shows what Claude's directory connectors name. Rely on what the **Tool permissions** page shows and the write test proves. | [D], [E] |

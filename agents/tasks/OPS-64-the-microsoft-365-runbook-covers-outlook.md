---
id: OPS-64
title: The Microsoft 365 runbook covers Outlook mail and calendar: what the connector reads and writes, how its write tools are set, and a check
domain: ops
tier: standard
tier_reason: One runbook section from vendor pages, same shape as the OPS-54 connector runbooks that ran on sonnet
status: merged
issue: 229
parent: 228
fixes: []
scope: [starter-kit/runbooks/microsoft-365-connector.md, starter-kit/README.md, tests/test_runbook_m365_outlook.py]
forbid: [docs/**, partner-kit/**, engagements/**, starter-kit/runbooks/verification-log.md, starter-kit/runbooks/google-workspace-connectors.md, CLAUDE.md]
red_test: python3 -m unittest tests.test_runbook_m365_outlook
gate: test
budget: 3-attempts
spend: 10
---
## Why

Compendium page 11 now has an Outlook row (OPS-61), and the general pack gains an Outlook entry that links the Microsoft 365 runbook (OPS-62), but the runbook covers tenant consent and SharePoint and barely mentions Outlook. An engineer handed an email or calendar task on Microsoft 365 has no steps. Issue #229.

## Done when

- READ FIRST. starter-kit/runbooks/microsoft-365-connector.md whole; docs/compendium/11-connectors.md (the Outlook and Microsoft 365 rows under 'What exists for our systems'); docs/compendium/18-customer-success.md and starter-kit/runbooks/google-workspace-connectors.md steps 13 to 16 (how the kit plans an email task to end in a draft); docs/compendium/README.md (the marker conventions: **⚠ Conflict:**, **⚠ Unverified:**, **(Our recommendation):**, **(Our reading):**; the warning sign appears only inside those two bold labels). You do not change the compendium; if the runbook cannot be made true without a compendium change, list it in the hand-back.
- SOURCES. Every new claim comes from a page you download yourself: curl -sL -m 40 -A 'Mozilla/5.0 (compatible; doc-check)' <url>, saved under .delegation/<this card's id>/pages/ in your worktree, tags stripped with a python3 -I script, and the phrase you quote found in the text. Claude docs pages on claude.com/docs, code.claude.com/docs and platform.claude.com/docs return markdown when you add .md to the URL. Read the Claude help-center article on the Microsoft 365 connector (support.claude.com) beside the docs page: the two can disagree, and where they do, write **⚠ Conflict:** naming both and take the safer reading. Microsoft's own pages (learn.microsoft.com) are accepted for Graph scopes and admin consent. Never confirm a claim from memory or from a summarising fetch. A claim no downloaded page states gets **⚠ Unverified:**.
- THE SECTION. A new level-2 section '## 6a. Outlook mail and calendar' directly after section 6. No existing heading is renamed, renumbered or removed (task templates link sections 2, 3 and 5 by anchor). It says: which Outlook mail and calendar tools the connector gives Claude, read and write listed separately, as the pages name them; that access is delegated per user and needs the tenant consent from section 3; which Microsoft Graph permissions mail and calendar use, read and write separately, if a page names them; whether write actions are off until an administrator turns them on, as page 11's row says, with the page that says it; that every tool that sends mail or creates, updates or deletes an event is set to Blocked or Needs approval in the connector's tool permissions, with the setting's path as section 6 names it; and, as **(Our recommendation):**, that an email task ends in a draft the person sends and a meeting task in a proposed time the person books, linking compendium page 18 as the Google runbook does. Then a check with one test user: Claude reads a named message and finds a named event; a send attempt stops at Blocked or asks for approval; record the result. 15 to 45 lines.
- OTHER LINES. The runbook's 'What this is' gains one sentence saying it now covers Outlook mail and calendar and linking section 6a. The 'Open items to verify' list gains each new unverified point. In starter-kit/README.md change only the description cell of the microsoft-365-connector.md row so it names Outlook mail and calendar. starter-kit/runbooks/verification-log.md is not changed: the new section's first line says 'Written 2026-11-16 by the author from the pages listed; not yet checked by a second reader.'
- TEST FIRST. tests/test_runbook_m365_outlook.py is committed first, alone, failing. It checks: the runbook has the heading '## 6a. Outlook mail and calendar' after the '## 6.' heading and before the '## 7.' heading; headings 1 to 9 keep their current text; the section is 15 to 45 lines; it contains 'Blocked', 'Needs approval', '(Our recommendation):' and a link to docs/compendium/18-customer-success.md; it carries the 'not yet checked by a second reader' sentence; every https link in the section is on learn.microsoft.com, support.claude.com, claude.com or support.microsoft.com; every relative link in the whole runbook resolves to a file; every warning sign in the section sits inside **⚠ Conflict:** or **⚠ Unverified:**; and the README row for the runbook names Outlook. Standard library only.
- GATE AND EVIDENCE. Run tests only through the lease: node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 1800 -- python3 -m unittest <args>, from your worktree. Save the red run's unittest output, and nothing else, to .delegation/<this card's id>/red-1.txt in your worktree. No note file in place of red evidence, no test run on a scratch copy outside the lease. The full gate python3 -m unittest discover -s tests passes. No rebase, no push, no PR.
- HAND-BACK. Each new claim with the URL you downloaded and the exact phrase you found; each point marked unverified or conflict and why; anything in compendium page 11 the pages contradict (listed, not changed); and in the [[report]] line, files= lists every file changed on the branch since origin/main.

## Review

Brain read the whole diff and re-searched the worker's downloaded pages (a.md docs, b.txt help-center setup, c.txt security guide): "Permissions are read-only by default", "only when your administrators have turned on write actions", "Shared mailbox access remains read-only", "All access is delegated", "Always allow, Needs approval, or Blocked", the Application Administrator line, the Outlook tool names and the chat/Cowork confirmation sentence are all on the pages. One simplification, not wrong in the unsafe direction: the runbook says users cannot choose Always allow for the Outlook send and event tools unless an admin set it; c.txt adds "on or after November 9, 2026" and says the limit does not apply to orgs that added the connector after that date. Left for a second-reader pass. No reviewer agent ran (standard tier, next=accept).

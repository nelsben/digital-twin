---
id: OPS-65
title: A runbook connects the Google Docs, Sheets and Slides connectors to a role's twin
domain: ops
tier: standard
tier_reason: One new connector runbook in the house shape from vendor pages, as OPS-54 did on sonnet
status: merged
issue: 230
parent: 228
fixes: []
scope: [starter-kit/runbooks/google-docs-sheets-slides-connectors.md, starter-kit/runbooks/google-workspace-connectors.md, starter-kit/README.md, tests/test_runbook_google_docs_sheets_slides.py]
forbid: [docs/**, partner-kit/**, engagements/**, starter-kit/runbooks/verification-log.md, starter-kit/runbooks/microsoft-365-connector.md, CLAUDE.md]
red_test: python3 -m unittest tests.test_runbook_google_docs_sheets_slides
gate: test
budget: 3-attempts
spend: 10
---
## Why

The Google Workspace runbook covers Drive, Gmail and Calendar. Its own step 8 sends comments and suggested edits to the separate Google Docs connector, and compendium page 11 marks the Docs, Sheets and Slides connectors' tools and plans unverified. An engineer handed a task that edits a doc or a sheet has no steps. Issue #230.

## Done when

- READ FIRST. starter-kit/runbooks/google-workspace-connectors.md whole (the shape, the write test, the tool-permission steps and the role steps you follow); tests/test_runbooks_connectors.py (the eight headings and the shape rules); docs/compendium/11-connectors.md (the Google Drive / Sheets row and the sentence on Docs, Sheets and Slides); docs/compendium/README.md (the marker conventions: **⚠ Conflict:**, **⚠ Unverified:**, **(Our recommendation):**, **(Our reading):**; the warning sign appears only inside those two bold labels). You do not change the compendium; list anything the pages contradict in the hand-back.
- SOURCES. Every claim comes from a page you download yourself: curl -sL -m 40 -A 'Mozilla/5.0 (compatible; doc-check)' <url>, saved under .delegation/<this card's id>/pages/ in your worktree, tags stripped with a python3 -I script, and the phrase you quote found in the text. Start from the Claude help-center article 'Use Google Workspace connectors' on support.claude.com, the directory listings on claude.com/connectors for Google Docs, Google Sheets and Google Slides (if a listing does not exist, say so), and the Claude docs pages under claude.com/docs/connectors/google/ (add .md for markdown; a 404 is a finding). Where two sources disagree write **⚠ Conflict:** naming both and take the safer reading. Never confirm a claim from memory or from a summarising fetch. A claim no downloaded page states gets **⚠ Unverified:**.
- THE RUNBOOK. starter-kit/runbooks/google-docs-sheets-slides-connectors.md has, in this order, the level-2 headings What this is, Read this first, Inputs you need, Before you start, Steps, Check it worked, Hand over, What can go wrong, and a 'Pages used' list that defines every source tag with an https URL; 100 to 260 lines. It covers, for each of the three connectors separately: who builds and runs it, which plans have it (or unverified), who adds it for the organization and whether each member connects their own Google account, which tools it gives Claude with read and write listed separately as the pages name them, and how each write tool is set to Blocked or Needs approval. It reuses the Google Workspace runbook by link for anything already there (the Workspace admin's app-access decision, the role steps, the write test) instead of copying it. As **(Our recommendation):** a task that changes a document, sheet or deck starts with every write tool Blocked, or at Needs approval when the plan's level allows it, and the write test is run in the customer's org before any task depends on a write tool. Its check uses one test user and one test file per connector. In place of the 'Checked 2026-11-16' sentence the other connector runbooks carry, it says 'Written 2026-11-16 by the author from the pages listed; not yet checked by a second reader.' starter-kit/runbooks/verification-log.md is not changed.
- LINKS IN. In starter-kit/runbooks/google-workspace-connectors.md add one link to the new runbook inside the existing step 8 sentence that names the separate Google Docs connector, and change nothing else in that file; it must still pass tests/test_runbooks_connectors.py and tests/test_runbook_verification_log.py unchanged. In starter-kit/README.md add one row for the new runbook directly after the google-workspace-connectors.md row, in the same form.
- TEST FIRST. tests/test_runbook_google_docs_sheets_slides.py is committed first, alone, failing. It checks the new runbook exists; carries the eight headings in order and 'Pages used'; is 100 to 260 lines; names Google Docs, Google Sheets and Google Slides each in at least one heading or step; contains 'Blocked', 'Needs approval' and '(Our recommendation):'; carries the 'not yet checked by a second reader' sentence; defines every [X] source tag it uses with an https URL on support.claude.com, claude.com, support.google.com, knowledge.workspace.google.com or developers.google.com; resolves every relative link; keeps every warning sign inside **⚠ Conflict:** or **⚠ Unverified:**; and that google-workspace-connectors.md and starter-kit/README.md link it. Standard library only.
- GATE AND EVIDENCE. Run tests only through the lease: node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 1800 -- python3 -m unittest <args>, from your worktree. Save the red run's unittest output, and nothing else, to .delegation/<this card's id>/red-1.txt in your worktree. No note file in place of red evidence, no test run on a scratch copy outside the lease. The full gate python3 -m unittest discover -s tests passes. No rebase, no push, no PR.
- HAND-BACK. Each claim with the URL you downloaded and the exact phrase you found; each point marked unverified or conflict and why; anything in compendium page 11 the pages contradict (listed, not changed); and in the [[report]] line, files= lists every file changed on the branch since origin/main.

## Review

Standard tier, accepted by the verifier directly. Brain read the diff (4 files: new runbook 116 lines, one link in the Google Workspace runbook step 8, one README row, test) and searched every quoted phrase in the runbook against the worker's downloaded pages in .delegation/OPS-65/pages/: all found. Unverified marks for builder, plans, tool names and approval behaviour are appropriate; no verification-log rows, as the card says. Compendium page 11's "Our runbooks don't cover these connectors" is now stale — left for OPS-68 / a later card (compendium forbidden here).

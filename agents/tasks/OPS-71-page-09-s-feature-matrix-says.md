---
id: OPS-71
title: Page 09's feature matrix says what the spend section says: Team spend controls are org-wide with per-user limits not on every Team org, and Claude Code's Free cell agrees with the pricing page
domain: ops
tier: standard
tier_reason: small docs edit with fetched sources and a structural test
effort: low
effort_reason: two table cells against two downloaded pages
status: merged
issue: 244
parent: 228
fixes: [OPS-69]
scope: [docs/compendium/09-plans-and-it-controls.md, tests/test_compendium_matrix_spend.py]
forbid: [starter-kit/**, partner-kit/**, engagements/**, CLAUDE.md, agents/**, .claude-plugin/**, docs/playbook/**, partner-kit/plugins/twin-consultant/data/rules.json, partner-kit/plugins/twin-consultant/data/task-library.json, partner-kit/plugins/twin-consultant/data/industry-packs/general.json, partner-kit/plugins/twin-consultant/skills/**/evals/**, partner-kit/docs/design.md, engagements/sample-pe/design.md, engagements/sample-pe/personas/**, engagements/sample-team-cs/personas/**, tests/fixtures/twincard/**, tests/test_twincard_followups.py, tests/test_twincard_rule_audit.py, tests/test_twincard_backlog_consistency.py, tests/test_twincard_walk_rules.py, tests/test_twincard_backlog.py, starter-kit/runbooks/verification-log.md, starter-kit/runbooks/microsoft-365-connector.md, starter-kit/runbooks/google-docs-sheets-slides-connectors.md, starter-kit/runbooks/claude-code-for-a-role.md, starter-kit/connectors/hubspot/README.md, starter-kit/connectors/zendesk/README.md, tests/test_runbook_second_reader_new_pages.py, tests/test_runbook_m365_outlook.py, tests/test_runbook_google_docs_sheets_slides.py, tests/test_runbook_claude_code_for_a_role.py, tests/test_twin_marker_hubspot_zendesk.py]
red_test: python3 -m unittest tests.test_compendium_matrix_spend
gate: test
budget: 3-attempts
spend: 10
---
## Why

OPS-69 added a sourced "Spend and usage limits" section to compendium page 09, and its worker reported two cells in the same page's feature matrix that the downloaded pages contradict or qualify: Team "Spend controls: Y" (the Team help article says per-user limits are not available to every Team org; the pricing page lists user and org spend limits as an Enterprise addition), and Claude Code "Pro and up" against the pricing FAQ's "included in all paid plans". The matrix is what readers scan, so it must not be looser than the section below it.

## Done when

- Read first: docs/compendium/README.md (markers), docs/compendium/09-plans-and-it-controls.md (the feature matrix and '## Spend and usage limits').
- Download with curl (generic user agent, no project details) https://claude.com/pricing and https://support.claude.com/en/articles/12005970, strip tags and search the text. Do not rely on memory or a summarising fetch.
- SPEND CELL. The Team cell of the 'Spend controls' row says, in the pages' own terms, that an Owner sets an org-wide monthly spend limit and that per-user limits are not available to every Team org, linking 12005970; the Enterprise cell keeps per-user limits and adds group limits if the section below already cites them (link #spend-and-usage-limits rather than repeating sources). If the pricing page's Team column says something else about spend controls, write what it says and mark the disagreement with **⚠ Conflict:** naming both pages.
- CLAUDE CODE CELL. Check the pricing page's Free column and FAQ for Claude Code. If Free does not include Claude Code, 'Pro and up' stays and the cell links the pricing page; if Free does, change the cell to say so. Quote the words that decide it in the hand-back.
- Nothing else on page 09 changes; no heading is renamed or removed; no other file changes except the test.
- TEST FIRST. New file tests/test_compendium_matrix_spend.py, committed alone and run failing first: the Spend controls row's Team cell contains 'per-user' and links 12005970; the Claude Code row's Individual cell links claude.com/pricing. The whole suite passes: python3 -m unittest discover -s tests.
- Hand-back lists: old -> new for each cell, with the URL and the exact words that support it.
- Test runs: run tests through `node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 600 -- <command>`; never bypass the hook and never run tests on a scratch copy outside the lease. If the lease is not granted within 20 minutes in total, write the red test file first, commit it alone, then build, commit and hand back with gate=fail and the words 'gate not run: lease blocked'. Keep any saved failing-run output under 1 MB.

## Review

Standard tier, no reviewer. Brain read the two-cell diff and searched the downloaded pricing page: "Claude Code No Yes Yes Yes" row, FAQ "Claude Code is included in all paid plans", Enterprise card "All Team plan features, plus: Admins set user and org spend limits", "Spend controls Yes" in the team table; 12005970 quotes were already checked for OPS-69. Conflict marker on the Team spend cell is justified.

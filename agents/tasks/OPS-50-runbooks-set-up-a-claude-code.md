---
id: OPS-50
title: Runbooks: set up a Claude Code scheduled task and a Claude Tag routine from a task's plan
domain: ops
tier: standard
tier_reason: two new docs and one text test in a fixed shape; the two frontier slots are held for the engine fix chain
effort: high
effort_reason: every fact must be fetched and copied exactly from vendor pages, which is slow careful work
status: merged
issue: 201
parent: 200
fixes: []
scope: [starter-kit/runbooks/claude-code-scheduled-task.md, starter-kit/runbooks/claude-tag-routine.md, tests/test_runbooks_client_runtimes.py]
forbid: [docs/**, partner-kit/**, engagements/**, agents/**, CLAUDE.md, starter-kit/README.md, starter-kit/runbooks/verification-log.md, starter-kit/runbooks/identity-devices-publishing.md, starter-kit/runbooks/microsoft-365-connector.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/plugins/**, starter-kit/settings/**, starter-kit/templates/**]
red_test: python3 -m unittest tests.test_runbooks_client_runtimes
gate: test
budget: 2-attempts
spend: 8
---
## Why

The generated backlog's set-up tasks for these two runtimes link to compendium page 05, which helps choose a runtime but does not say how to set one up. The consultant-walk review (OPS-44) judged that an engineer could not build from the backlog alone. These runbooks are the missing how-to; another card points the backlog at them.

## Done when

- Two new files exist: starter-kit/runbooks/claude-code-scheduled-task.md and starter-kit/runbooks/claude-tag-routine.md. Read starter-kit/runbooks/microsoft-365-connector.md first and follow its shape and tone.
- FACTS RULE. Write no product fact from memory: both products are new and change often. Fetch the vendor pages during this task (accepted domains: code.claude.com, platform.claude.com, claude.com/docs, support.claude.com; for Slack admin steps also slack.com/help and docs.slack.dev). Start from the URLs in docs/compendium/sources.md and the sources lines on compendium pages 02, 05, 06, 10, 11, 13 and 15. Every numbered step and every factual product sentence ends with one or more source tags like ([A], [C]) that the 'Pages used' list defines. Menu paths, setting names, limits, commands and URLs are copied character by character from the fetched page. A fact that no fetched page confirms is left out, or it starts with the compendium's marker **⚠ Unverified:** and says what would confirm it. A page you could not fetch is not cited; name it in the hand-back.
- SECTIONS, in this order, as level-2 headings with exactly these words: 'What this is', 'Read this first', 'Inputs you need', 'Before you start', 'Steps', 'Check it worked', 'Hand over', 'What can go wrong'. 'What this is' ends with the role table that maps the names used to docs/playbook/03-stakeholders.md, as the Microsoft 365 runbook does. 'Read this first' says how sources are marked, holds the 'Pages used' list, and carries this sentence: 'Checked 2026-11-16 by the author against the pages listed. Not yet independently verified: verification-log.md has no rows for this runbook.'
- 'Inputs you need' lists, in plain words, the decisions the engagement has already made for the task and that the steps consume: who the task runs as, the autonomy level it starts at and its ceiling (docs/compendium/06-autonomy.md), the data class and the surfaces and retention that follow, each connector and each tool's permission, the schedule or trigger, memory on or off, and the skill that holds the task's instructions. It does not mention the partner kit, a persona card or levelled.json: the strings 'partner-kit' and 'levelled' do not appear in either file.
- claude-code-scheduled-task.md covers, each from a fetched page or marked unverified: the two places the task can run (Anthropic's cloud or the customer's own environment) and a link to the compendium sections that decide between them by data class, without restating them; creating the task with the skill as its prompt; the schedule and its limits; that it acts as the employee with their connectors, and what holds it to the autonomy level (which permission controls apply to a scheduled run); whether the managed governance hook runs for it; where the run history is; what happens on a missed or failed run; how to pause and remove it; its release status.
- claude-tag-routine.md covers, each from a fetched page or marked unverified: what must be installed and on which plans; creating a channel routine and its schedule or watch mode with their limits; which identity it acts as in a channel, a group DM and a one-to-one DM, and the option for a user's own connectors; servers declared in a plugin's .mcp.json and the credential per server host; checking who can read the channel against the task's data class (link compendium 10, do not restate); channel memory and who can edit it; where the record of a run is; how to pause and remove the routine; its release status.
- Where the compendium already states a fact, link that compendium section in addition to the vendor tag instead of explaining it again. Where a fetched page contradicts the compendium, the runbook follows the fetched page and the hand-back lists the contradiction with both quotes. The compendium is not edited.
- 'Check it worked' is a test one named role can run in under ten minutes with an expected result. 'Hand over' says what to record in the customer's engagement folder and who owns the task after set-up. Each runbook is between 110 and 260 lines. No real company or person is named.
- A new test file tests/test_runbooks_client_runtimes.py (standard library only) checks for both files: the eight headings exist in order; every relative link resolves to an existing file; every numbered line under 'Steps' ends with a source-tag group or contains the unverified marker; every tag used is defined under 'Pages used' and every defined page is an https URL on an accepted domain or a relative path that exists; the strings 'partner-kit' and 'levelled' are absent; the 'Checked 2026-11-16' sentence is present. It fails before the change and passes after.
- Not changed: starter-kit/README.md, starter-kit/runbooks/verification-log.md, the three existing runbooks, anything under partner-kit or docs.
- python3 -m unittest discover -s tests passes. The hand-back gives, per runbook: the number of sourced facts and of unverified ones; every page fetched with its URL and whether the fetch worked; each contradiction with the compendium; each choice this card did not decide.

## Review

Read by the brain (no reviewer asked for): both runbooks and the test in full. Every numbered step ends in source tags or the unverified marker; 11 items are marked unverified with how to confirm each. The worker's own test run never got the shared Mac test lease; the verifier ran the gate green at 6bafa60. Red-first was NOT captured: red-1.txt is a note saying so, not a failing run. The test's first assertion is that both files exist, so it fails without them by construction. Product facts were fetched by the worker on 2026-11-16 and not re-fetched by anyone else; the runbooks say so. Follow-ups: step 2 of the scheduled-task runbook uses a "⚠ Conflict:" marker the compendium README does not define; compendium 05 needs two refinements the worker found (a Tag routine never uses a member's personal connectors; a routine set up in a one-to-one DM is turned off when its owner is removed).

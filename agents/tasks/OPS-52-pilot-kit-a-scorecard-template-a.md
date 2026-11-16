---
id: OPS-52
title: Pilot kit: a scorecard template, a memory policy template and a pilot training and failure-report template
domain: ops
tier: standard
tier_reason: four fill-in templates and one text test, every section decided in the card
status: merged
issue: 204
parent: 200
fixes: []
scope: [starter-kit/templates/pilot/**, tests/test_pilot_templates.py]
forbid: [docs/**, partner-kit/**, engagements/**, agents/**, CLAUDE.md, starter-kit/README.md, starter-kit/runbooks/**, starter-kit/plugins/**, starter-kit/settings/**, starter-kit/templates/persona/**, starter-kit/templates/skill/**, starter-kit/templates/role-plugin/**, starter-kit/runbooks/claude-code-scheduled-task.md, starter-kit/runbooks/claude-tag-routine.md, tests/test_runbooks_client_runtimes.py, starter-kit/runbooks/managed-agents.md, starter-kit/runbooks/agent-sdk-runner.md, tests/test_runbooks_hosted_runtimes.py]
red_test: python3 -m unittest tests.test_pilot_templates
gate: test
budget: 2-attempts
spend: 10
---
## Why

Three tasks in every generated backlog (set up the monthly scorecard, write the memory policy, train the pilot users and tell them how to report a failure) have nothing in the starter kit to copy, and one of their how lines has no link at all. The consultant-walk review (OPS-44) judged the backlog could not be built from alone. These templates give those tasks something to fill in; another card points the backlog at them.

## Done when

- A new folder starter-kit/templates/pilot/ holds four files: README.md, scorecard.md, memory-policy.md and pilot-training.md. Read starter-kit/templates/persona/README.md and persona.md first and follow their tone and their 'FILL IN:' marker.
- NO NEW PRODUCT FACTS. These files state no fact about Claude that the compendium does not already state. Where a fact is needed, link the compendium section (relative link) and say only what the reader must do with it. Do not copy compendium tables; the one exception is the four layer names (Adoption, Quality, Value, Safety) and the measure names in scorecard.md, each row linking back to docs/compendium/15-governance-and-performance.md#measuring-performance.
- scorecard.md is a fill-in monthly scorecard for one twin: a header (twin, role, month, business owner, who prepared it); one table per layer with the columns Measure, Where it comes from, Baseline, Target, This month, Last month, Note, with one row per measure the compendium names and FILL IN cells; a section 'Per task' with one row per task giving its autonomy level, eval pass rate, edit rate and approve and reject counts; a section 'Decision this month' with a choice per task of stay, move up one level or move down, and the evidence the compendium's rule for moving up asks for (link docs/compendium/06-autonomy.md#rules-for-moving-up-a-level, do not restate it); a section 'Actions' with owner and date. Where the customer's plan lacks a source (for example no governance log on a Team plan with no device management), the template says to write 'not available' and links docs/compendium/15-governance-and-performance.md#team-plan-with-no-device-management.
- memory-policy.md is a fill-in policy for one role: what the twin may remember and what it must not, as a table by task and data class with FILL IN cells; one row per place memory can live for this role, each linking docs/compendium/02-persona.md#memory instead of describing it; who can switch memory on or off for the org and the decision taken; what the pilot users are told (why it is on or off, and for on: where the user sees and clears what is kept, as a FILL IN that the engagement completes from the vendor page linked in compendium 02); the rule for tasks that read outsider-written input, linking the compendium's memory-poisoning paragraph; a sign-off line for the compliance owner and the business owner.
- pilot-training.md has two parts. Part 1, 'Session outline' (about 45 minutes): for each task, what the twin does, the autonomy level it runs at and what that means for the user, and what it never does; how to recognise the twin's output in each system (the marker); what data must not be pasted in; how to stop or undo. Each item is a FILL IN with one line saying where in the engagement's design the answer comes from. Part 2, 'Report a failure or a wrong draft': the one place reports go (FILL IN), a copyable report form (date, task, what you asked, what came back, what you expected, the system and record, data class, how bad: wrong but harmless, wrong and sent, or data exposed), who triages and how fast (roles named as in docs/playbook/03-stakeholders.md), and that a 'data exposed' report goes to security and compliance the same day.
- README.md says in under 40 lines what each file is for, which engagement phase uses it (link docs/playbook/01-engagement-model.md), that the filled copies go in the customer's delivery repo or engagement folder (link ../../README.md#start-a-new-customer for the delivery repo, do not describe it again), and gives the level-2 headings 'What is here', 'Fill them in' and 'When to use them'.
- None of the four files mentions the partner kit, a persona card or levelled.json: the strings 'partner-kit' and 'levelled' do not appear. No real company or person is named.
- A new test file tests/test_pilot_templates.py (standard library only) checks: the four files exist; the README has the three headings; scorecard.md has the four layer names and the headings 'Per task', 'Decision this month' and 'Actions'; memory-policy.md and pilot-training.md each hold at least five 'FILL IN' markers; pilot-training.md has the headings 'Session outline' and 'Report a failure or a wrong draft'; every relative link in the four files resolves to an existing file, and every #anchor on a link into docs/compendium or docs/playbook matches a heading in the target (use the same slug rule tests/test_persona_template.py uses); the strings 'partner-kit' and 'levelled' are absent. It fails before the change and passes after.
- Not changed: starter-kit/README.md, the other templates, anything under partner-kit or docs.
- python3 -m unittest discover -s tests passes; the hand-back gives the test count, each file's line count, and each choice this card did not decide.

## Review

Read by the brain earlier at 8f7c467 (the four templates and the test); every claim held at the verifier and no reviewer agent ran. The commit holds the test and the templates together, so the red run was taken at the branch base 09446f5 with only tests/test_pilot_templates.py added (8 tests: 1 failure, 7 errors; the evidence file says so in its first line). The gate ran at 8f7c467 through the test lease (456 tests, OK). One decision the worker made that the card left open: a "data exposed" failure report goes to security and compliance the same day, as a fixed row.

---
id: SHA-15
title: T1 and T2 skills are graded by an independent grader against a without-skill baseline, and the plugin is at 0.2.0
domain: shared
tier: standard
effort: high
effort_reason: many subagent runs and blind grading must be set up carefully
status: merged
issue: 72
parent: 23
scope: [starter-kit/plugins/twin-pe-deal-team/.claude-plugin/plugin.json, starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/README.md, starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/evals/README.md]
forbid: [starter-kit/runbooks/identity-devices-publishing.md]
red_test: none
gate: test
budget: 2-attempts
spend: 10
---
## Why

Both pilot skills report all evals passing, but the workers graded their own with-skill runs, with no baseline and no trigger-eval run, so we cannot yet say the skills are what make the cases pass. This is the evidence the pilot sign-off needs. Issue #72.

## Done when

- For each of preparing-company-briefs and drafting-crm-updates, every case in evals/evals.json is run twice on Sonnet: once with the skill and once without it (baseline), each in its own subagent given only the case prompt and fixture files and Read as its only tool
- Each run is graded by a separate grader subagent that sees the expectations and the response but not which run had the skill; grades are pass or fail per expectation with a one-line reason
- The trigger queries in evals/trigger-evals.json are checked: for each query, a subagent shown only the two skills' name and description says which skill, if any, it would load; the hit rate on should-trigger and the false-trigger rate on should-not-trigger are reported
- Each skill's evals/README.md gets a Results section (date, model, with-skill pass rate, baseline pass rate, trigger hit and false-trigger rates, and any failing case by id with the reason); raw outputs stay outside the repo
- If a with-skill case fails, the report names it; the worker does not change SKILL.md or the eval files in this card
- starter-kit/plugins/twin-pe-deal-team/.claude-plugin/plugin.json version is 0.2.0
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: independent eval run for both deal-team skills with blind per-run graders and a no-skill baseline. Briefs: with skill 47/47 (9/9), baseline 39/47 (5/9). CRM updates: with skill 44/44 (8/8), baseline 42/44 (6/8). Triggers 8/8 hit, 0/10 false on both. READMEs state the limits honestly: read-only by instruction only, inherited session context, tool-use expectations unverifiable from text, imperfect blinding, one run per case. Small baseline gap on the CRM skill noted. plugin.json bumped to 0.2.0. Spend overshoot (~$11-12 incl. sub-runs vs ~$10) flagged by worker and accepted. 70 tests pass.

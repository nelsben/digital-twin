---
id: SHA-13
title: preparing-company-briefs skill layers on Anthropic's PE plugins and passes its evals
domain: shared
tier: standard
effort: high
effort_reason: must reconcile upstream plugin skills with our MNPI rules
status: merged
issue: 32
parent: 31
scope: [starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/**, starter-kit/plugins/twin-pe-deal-team/README.md]
forbid: []
red_test: test -f starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/SKILL.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

Story T1 (#32): a one-page company brief before a management meeting. Per OD-1 it is built as a layer on the private-equity and financial-analysis plugins, using the adopt/adapt verdicts from page 17 and the evals from #55.

## Done when

- The worker reads docs/compendium/17-anthropic-pe-plugins-review.md first and builds on the skills it marks adopt or adapt; it does not copy upstream skill text into this repo unless page 17 says to vendor it
- starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/SKILL.md exists, passes tests/test_kit_structure.py, and covers the one-page format, a source link per item, saying what is missing instead of guessing, and no web tools
- If the skill depends on an upstream plugin, the twin-pe-deal-team README says which and how to install it
- Every case in the skill's evals/evals.json passes when run with skill-creator, and the worker pastes the results; evals files are not changed except to fix a fixture bug, named in the report
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: SKILL.md (58 lines) plus the output template match the card: one page, a source link per fact, status from the live record, conflicts under Unverified, no writes, no web, no-access reply carries no content. Builds on page 17 in idea only, with no install dependency. Caveat: 9/9 evals graded by the worker with no baseline run; an independent grader pass is owed before the pilot. plugin.json still at 0.1.0 with two skills, to bump at release.

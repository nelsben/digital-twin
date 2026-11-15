---
id: SHA-14
title: drafting-crm-updates skill layers on Anthropic's PE plugins, sets the twin marker, and passes its evals
domain: shared
tier: standard
effort: high
effort_reason: write path to the CRM; marker and draft-only rules must hold
status: merged
issue: 34
parent: 33
scope: [starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/**]
forbid: [starter-kit/connectors/salesforce/**, tests/test_salesforce_marker.py]
red_test: test -f starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/SKILL.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

Story T2 (#34): draft CRM updates after a meeting, marked as twin-written. Per OD-1 it layers on the upstream plugins where page 17 says they fit, and uses the marker field from #54 and the evals from #55.

## Done when

- The worker reads docs/compendium/17-anthropic-pe-plugins-review.md and starter-kit/connectors/salesforce/README.md first
- starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/SKILL.md exists, passes tests/test_kit_structure.py, drafts only at autonomy level 1 (shows the proposed field changes for the user to apply), and at level 2 sets Last_Updated_By_Twin__c on every write
- No web tools; the skill never writes to a record the user cannot already edit
- Every case in the skill's evals/evals.json passes when run with skill-creator, and the worker pastes the results; evals files are not changed except to fix a fixture bug, named in the report
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: SKILL.md (67 lines) and the level-2 reference match the card: level 1 draft-only, a user's "save it" never raises the level, marker in the same update call, fail closed on marker rejection, edit-access check before any write, no web tools. Stands alone per page 17. Caveat: 8/8 evals were graded by the worker itself with no baseline run; an independent grader pass is still owed before pilot.

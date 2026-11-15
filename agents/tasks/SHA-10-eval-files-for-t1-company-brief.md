---
id: SHA-10
title: Eval files for T1 (company brief) and T2 (CRM update) exist before either skill is built
domain: shared
tier: standard
status: merged
issue: 55
parent: 23
scope: [starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/**, starter-kit/plugins/twin-pe-deal-team/skills/drafting-crm-updates/evals/**]
forbid: [docs/compendium/17-anthropic-pe-plugins-review.md, docs/compendium/README.md, docs/compendium/sources.md, engagements/sample-pe/design.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
red_test: python3 -m json.tool starter-kit/plugins/twin-pe-deal-team/skills/preparing-company-briefs/evals/evals.json
gate: test
budget: 2-attempts
spend: 10
---
## Why

The playbook builds skills evals-first. The acceptance criteria for T1 and T2 already live in engagements/sample-pe/backlog.md; turning them into skill-creator eval files now means #32 and #34 are built against a fixed target. Issue #55.

## Done when

- Each of the two skills folders (preparing-company-briefs, drafting-crm-updates) gets evals/evals.json and evals/trigger-evals.json in the same format as starter-kit/templates/skill/your-skill-name/evals/
- evals.json has one case per acceptance criterion in backlog.md for that story (at least 3), each with prompt, expected_output, files and expectations; cases include the empty-deal-folder case, the no-access case and the no-web-tools case
- Fixtures are synthetic and obviously fictional, under evals/files/, and contain no real company or person names; the README of each evals folder says the customer's skill owners replace them with 3 redacted real examples
- trigger-evals.json has at least 8 should-trigger and 8 should-not-trigger queries, with the near-misses (for T1: pitch-book drafting; for T2: email drafting) as should-not-trigger
- No SKILL.md is written; all JSON parses with python3 -m json.tool
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: 9 + 8 eval cases map to backlog criteria, including the empty-folder, no-access and no-web-tools cases; fixtures are clearly fictional with banners; trigger near-misses present. Accepted choices: split T1 criteria 4 and 6, the 450-word one-page proxy, and the denial-only no-access fixture.

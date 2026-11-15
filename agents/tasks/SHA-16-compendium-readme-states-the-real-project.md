---
id: SHA-16
title: Compendium README states the real project status, and the two connector runbooks make no false statement about this repo's files
domain: shared
tier: standard
tier_reason: docs fact-check against repo files; an economy worker wrote the false statements this repairs
effort: low
effort_reason: mechanical comparison of statements with files, no design decisions
status: merged
issue: 79
parent: 23
fixes: []
scope: [docs/compendium/README.md, starter-kit/runbooks/salesforce-hosted-mcp.md, starter-kit/runbooks/microsoft-365-connector.md]
forbid: [starter-kit/settings/**, tests/test_settings.py, starter-kit/runbooks/identity-devices-publishing.md]
red_test: python3 -c "import sys;sys.exit('Nothing is built yet' in open('docs/compendium/README.md').read())"
gate: test
budget: 2-attempts
spend: 10
---
## Why

The compendium README still says the project is in a research phase and nothing is built, which is no longer true. A review found two false statements about this repo's own files in the identity runbook, so the other two runbooks need the same check before anyone follows them.

## Done when

- The Status line at the top of docs/compendium/README.md no longer says 'research phase' or 'Nothing is built yet'. It says: the facts are grounded in Anthropic's docs as fetched on 2026-11-14; the starter kit and the sample engagement are built on top of this compendium; with links to ../../starter-kit/README.md and ../../engagements/sample-pe/README.md. Nothing else in that README changes
- In starter-kit/runbooks/salesforce-hosted-mcp.md and starter-kit/runbooks/microsoft-365-connector.md, every statement about this repo's own files is compared with the file on the branch: statements cited as a repo file, and statements that name a path under starter-kit/, .claude-plugin/, tests/, docs/ or engagements/ or describe what such a file contains (for example which keys a settings baseline has, what the marker field is called, what a skill does). False statements are corrected to match the file
- Statements about Salesforce, Microsoft or Anthropic products are not changed, and no unverified marker is removed or added
- Every relative link in the three files resolves to a file that exists on the branch
- The report lists each repo statement checked, with file and line, as pass or fixed (with the old and new wording for each fix). If none is false, the report says so and the two runbooks are left unchanged
- The gate passes: python3 -m unittest discover -s tests

## Review

Brain review: README status line now names the built kit and sample engagement with working links. Level-1 wording in both connector runbooks corrected to match 06 (Draft: write tools blocked); quarterly review now cites 15. Accepted choice: M365 L52 tunnel inference left as is.

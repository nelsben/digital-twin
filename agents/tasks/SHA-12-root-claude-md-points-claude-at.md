---
id: SHA-12
title: Root CLAUDE.md points Claude at the compendium, playbook, starter kit, workflow and test command
domain: shared
tier: standard
effort: low
effort_reason: short docs file
status: merged
issue: 61
parent: 10
scope: [CLAUDE.md]
forbid: []
red_test: test -f CLAUDE.md
gate: test
budget: 2-attempts
spend: 10
---
## Why

Claude Code loads CLAUDE.md, not README.md, so the repo's sources of truth and its card-and-branch workflow are invisible to a fresh session today. Issue #61.

## Done when

- Before writing, the worker reads https://code.claude.com/docs/en/memory and follows its guidance on CLAUDE.md content and length
- CLAUDE.md at the repo root is under 60 lines and says: what the repo is (a partner playbook and starter kit for role-based digital twins); where facts live (docs/compendium, with page 16 for Anthropic's own skills and plugins), how engagements run (docs/playbook), the starter kit front door (starter-kit/README.md), and the sample engagement (engagements/sample-pe)
- It states the rules: compendium facts carry sources and an unverified mark when unconfirmed; customer answers go in the engagement folder, not the compendium; sample-engagement names are fictional
- It names the test command python3 -m unittest discover -s tests and that work goes on a branch, through a PR
- It links rather than copies; no other file is changed

## Review

Brain review: 24-line CLAUDE.md, links not copies, all paths exist; covers where facts live, the unverified rule, engagement-folder rule, fictional sample, branch-and-PR workflow, card scope and the test command. 70 tests pass.

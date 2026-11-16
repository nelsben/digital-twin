---
id: OPS-73
title: The sample PE design's Slack Connect row says what compendium page 11 says about the Slack directory connector
domain: ops
tier: economy
tier_reason: one table row in a fictional sample, its eval copy and one test; every word decided in the card
status: merged
issue: 252
parent: 170
fixes: []
scope: [engagements/sample-pe/design.md, partner-kit/plugins/twin-consultant/skills/filling-persona-cards/evals/files/engagements/sample-pe/design.md, tests/test_sample_pe_consistency.py, tests/test_sample_pe_slack_connect.py]
forbid: [docs/**, starter-kit/**, CLAUDE.md, agents/**, engagements/sample-pe/personas/**, engagements/sample-team-cs/**]
red_test: python3 -m unittest discover -s tests -p "test_sample_pe*.py"
gate: test
budget: 2-attempts
spend: 3
---
## Why

The fictional PE design's Slack Connect row (E3) says the directory connector connects "with Slack admin approval". Compendium page 11 attaches Slack admin approval to the Slack MCP server, while the directory connector is per user once an Owner enables it, and needs the Claude in Slack app installed first. The worked example should teach what the compendium says.

## Done when

- Read first: docs/compendium/11-connectors.md Slack row (line ~16) and engagements/sample-pe/design.md line ~182 (the **Slack Connect** (E3) row). Both read-only except the design row.
- In that row only: the identity cell says per user: an Owner enables the directory connector for the org, then each member connects their own account, and the Claude in Slack app must be installed in the workspace first (page 11). The who cell says Tomasz Hadjiev enables it as Owner after the Claude in Slack app is installed, and keeps 'no Slack admin is named yet' as the person who would install the app. Remove 'Slack admin approval' from the directory-connector wording. The use, writes and risk cells are unchanged; the row stays fictional; no other line of the design changes.
- partner-kit/plugins/twin-consultant/skills/filling-persona-cards/evals/files/engagements/sample-pe/design.md is copied from the edited design so the two stay byte-identical.
- Test: add one test method to tests/test_sample_pe_consistency.py if that file exists, otherwise a new file tests/test_sample_pe_slack_connect.py, committed first alone and seen failing through the lease: the Slack Connect row does not contain 'Slack admin approval' and contains 'Claude in Slack app'; the eval copy equals the design byte for byte. The whole suite passes: python3 -m unittest discover -s tests.
- Test runs only through `node /Users/bennelsen/WorkflowBridge/bin/wb lease gate-mac --wait 600 -- <command>`; never outside it. Red output under 1 MB. files= lists every file changed since origin/main. Hand-back gives the row old -> new.

## Review

Verdict consistent, accepted with no reviewer agent (economy tier). The brain read the diff: one row of the fictional PE design and its byte-identical eval copy now follow compendium page 11 (Owner enables, each member connects, Claude in Slack app installed first); "Slack admin approval" is gone. A new 2-test file. Gate: 843 OK.
